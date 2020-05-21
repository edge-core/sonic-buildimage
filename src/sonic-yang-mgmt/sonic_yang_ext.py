# This script is used as extension of sonic_yang class. It has methods of
# class sonic_yang. A separate file is used to avoid a single large file.

from __future__ import print_function
import yang as ly
import re
import syslog

from json import dump, dumps, loads
from xmltodict import parse
from glob import glob

"""
This is the Exception thrown out of all public function of this class.
"""
class SonicYangException(Exception):
    pass

# class sonic_yang methods, use mixin to extend sonic_yang
class SonicYangExtMixin:

    """
    load all YANG models, create JSON of yang models. (Public function)
    """
    def loadYangModel(self):

        try:
            # get all files
            self.yangFiles = glob(self.yang_dir +"/*.yang")
            # load yang modules
            for file in self.yangFiles:
                m = self._load_schema_module(file)
                if m is not None:
                    self.sysLog(msg="module: {} is loaded successfully".format(m.name()))
                else:
                    raise(Exception("Could not load module {}".format(file)))

            # keep only modules name in self.yangFiles
            self.yangFiles = [f.split('/')[-1] for f in self.yangFiles]
            self.yangFiles = [f.split('.')[0] for f in self.yangFiles]
            print('Loaded below Yang Models')
            print(self.yangFiles)

            # load json for each yang model
            self._loadJsonYangModel()
            # create a map from config DB table to yang container
            self._createDBTableToModuleMap()

        except Exception as e:
            print("Yang Models Load failed")
            raise SonicYangException("Yang Models Load failed\n{}".format(str(e)))

        return True

    """
    load JSON schema format from yang models
    """
    def _loadJsonYangModel(self):

        try:
            for f in self.yangFiles:
                m = self.ctx.get_module(f)
                if m is not None:
                    xml = m.print_mem(ly.LYD_JSON, ly.LYP_FORMAT)
                    self.yJson.append(parse(xml))
                    self.sysLog(msg="Parsed Json for {}".format(m.name()))
        except Exception as e:
            raise e

        return

    """
    Create a map from config DB tables to container in yang model
    This module name and topLevelContainer are fetched considering YANG models are
    written using below Guidelines:
    https://github.com/Azure/SONiC/blob/master/doc/mgmt/SONiC_YANG_Model_Guidelines.md.
    """
    def _createDBTableToModuleMap(self):

        for j in self.yJson:
            # get module name
            moduleName = j['module']['@name']
            # get top level container
            topLevelContainer = j['module'].get('container')
            # if top level container is none, this is common yang files, which may
            # have definitions. Store module.
            if topLevelContainer is None:
                self.confDbYangMap[moduleName] = j['module']
                continue

            # top level container must exist for rest of the yang files and it should
            # have same name as module name.
            assert topLevelContainer['@name'] == moduleName

            # Each container inside topLevelContainer maps to a sonic config table.
            container = topLevelContainer['container']
            # container is a list
            if isinstance(container, list):
                for c in container:
                    self.confDbYangMap[c['@name']] = {
                        "module" : moduleName,
                        "topLevelContainer": topLevelContainer['@name'],
                        "container": c
                        }
            # container is a dict
            else:
                self.confDbYangMap[container['@name']] = {
                    "module" : moduleName,
                    "topLevelContainer": topLevelContainer['@name'],
                    "container": container
                    }
        return

    """
    Get module, topLevelContainer(TLC) and json container for a config DB table
    """
    def _getModuleTLCcontainer(self, table):
        cmap = self.confDbYangMap
        m = cmap[table]['module']
        t = cmap[table]['topLevelContainer']
        c = cmap[table]['container']
        return m, t, c

    """
    Crop config as per yang models,
    This Function crops from config only those TABLEs, for which yang models is
    provided. The Tables without YANG models are stored in
    self.tablesWithOutYangModels.
    """
    def _cropConfigDB(self, croppedFile=None):

        for table in self.jIn.keys():
            if table not in self.confDbYangMap:
                # store in tablesWithOutYang
                self.tablesWithOutYang[table] = self.jIn[table]
                del self.jIn[table]

        if len(self.tablesWithOutYang):
            print("Note: Below table(s) have no YANG models:")
            for table in self.tablesWithOutYang.keys():
                print(unicode(table), end=", ")
            print()

        if croppedFile:
            with open(croppedFile, 'w') as f:
                dump(self.jIn, f, indent=4)

        return

    """
    Extract keys from table entry in Config DB and return in a dict

    Input:
    tableKey: Config DB Primary Key, Example tableKey = "Vlan111|2a04:5555:45:6709::1/64"
    keys: key string from YANG list, i.e. 'vlan_name ip-prefix'.
    regex: A regex to extract keys from tableKeys, good to have it as accurate as possible.

    Return:
    KeyDict = {"vlan_name": "Vlan111", "ip-prefix": "2a04:5555:45:6709::1/64"}
    """
    def _extractKey(self, tableKey, keys, regex):

        keyList = keys.split()
        # get the value groups
        value = re.match(regex, tableKey)
        # create the keyDict
        i = 1
        keyDict = dict()
        for k in keyList:
            if value.group(i):
                keyDict[k] = value.group(i)
            else:
                raise Exception("Value not found for {} in {}".format(k, tableKey))
            i = i + 1

        return keyDict

    """
    Fill the dict based on leaf as a list or dict @model yang model object
    """
    def _fillLeafDict(self, leafs, leafDict, isleafList=False):

        if leafs is None:
            return

        # fill default values
        def _fillSteps(leaf):
            leaf['__isleafList'] = isleafList
            leafDict[leaf['@name']] = leaf
            return

        if isinstance(leafs, list):
            for leaf in leafs:
                #print("{}:{}".format(leaf['@name'], leaf))
                _fillSteps(leaf)
        else:
            #print("{}:{}".format(leaf['@name'], leaf))
            _fillSteps(leafs)

        return

    """
    create a dict to map each key under primary key with a dict yang model.
    This is done to improve performance of mapping from values of TABLEs in
    config DB to leaf in YANG LIST.
    """
    def _createLeafDict(self, model):

        leafDict = dict()
        #Iterate over leaf, choices and leaf-list.
        self._fillLeafDict(model.get('leaf'), leafDict)

        #choices, this is tricky, since leafs are under cases in tree.
        choices = model.get('choice')
        if choices:
            for choice in choices:
                cases = choice['case']
                for case in cases:
                    self._fillLeafDict(case.get('leaf'), leafDict)

        # leaf-lists
        self._fillLeafDict(model.get('leaf-list'), leafDict, True)

        return leafDict

    """
    Convert a string from Config DB value to Yang Value based on type of the
    key in Yang model.
    @model : A List of Leafs in Yang model list
    """
    def _findYangTypedValue(self, key, value, leafDict):

        # convert config DB string to yang Type
        def _yangConvert(val):
            # Convert everything to string
            val = str(val)
            # find type of this key from yang leaf
            type = leafDict[key]['type']['@name']

            if 'uint' in type:
                vValue = int(val, 10)
            # TODO: find type of leafref from schema node
            elif 'leafref' in type:
                vValue = val
            #TODO: find type in sonic-head, as of now, all are enumeration
            elif 'head:' in type:
                vValue = val
            else:
                vValue = val
            return vValue

        # if it is a leaf-list do it for each element
        if leafDict[key]['__isleafList']:
            vValue = list()
            for v in value:
                vValue.append(_yangConvert(v))
        else:
            vValue = _yangConvert(value)

        return vValue

    """
    Xlate a list
    This function will xlate from a dict in config DB to a Yang JSON list
    using yang model. Output will be go in self.xlateJson
    """
    def _xlateList(self, model, yang, config, table):

        #create a dict to map each key under primary key with a dict yang model.
        #This is done to improve performance of mapping from values of TABLEs in
        #config DB to leaf in YANG LIST.
        leafDict = self._createLeafDict(model)

        # fetch regex from YANG models.
        keyRegEx = model['ext:key-regex-configdb-to-yang']['@value']
        # seperator `|` has special meaning in regex, so change it appropriately.
        keyRegEx = re.sub('\|', '\\|', keyRegEx)
        # get keys from YANG model list itself
        listKeys = model['key']['@value']
        self.sysLog(msg="xlateList regex:{} keyList:{}".\
            format(keyRegEx, listKeys))

        for pkey in config.keys():
            try:
                vKey = None
                self.sysLog(syslog.LOG_DEBUG, "xlateList Extract pkey:{}".\
                    format(pkey))
                # Find and extracts key from each dict in config
                keyDict = self._extractKey(pkey, listKeys, keyRegEx)
                # fill rest of the values in keyDict
                for vKey in config[pkey]:
                    self.sysLog(syslog.LOG_DEBUG, "xlateList vkey {}".format(vKey))
                    keyDict[vKey] = self._findYangTypedValue(vKey, \
                                        config[pkey][vKey], leafDict)
                yang.append(keyDict)
                # delete pkey from config, done to match one key with one list
                del config[pkey]

            except Exception as e:
                # log debug, because this exception may occur with multilists
                self.sysLog(syslog.LOG_DEBUG, "xlateList Exception {}".format(e))
                # with multilist, we continue matching other keys.
                continue

        return

    """
    Process list inside a Container.
    This function will call xlateList based on list(s) present in Container.
    """
    def _xlateListInContainer(self, model, yang, configC, table):
        clist = model
        #print(clist['@name'])
        yang[clist['@name']] = list()
        self.sysLog(msg="xlateProcessListOfContainer: {}".format(clist['@name']))
        self._xlateList(clist, yang[clist['@name']], configC, table)
        # clean empty lists
        if len(yang[clist['@name']]) == 0:
            del yang[clist['@name']]

        return

    """
    Process container inside a Container.
    This function will call xlateContainer based on Container(s) present
    in outer Container.
    """
    def _xlateContainerInContainer(self, model, yang, configC, table):
        ccontainer = model
        #print(ccontainer['@name'])
        yang[ccontainer['@name']] = dict()
        if not configC.get(ccontainer['@name']):
            return
        self.sysLog(msg="xlateProcessListOfContainer: {}".format(ccontainer['@name']))
        self._xlateContainer(ccontainer, yang[ccontainer['@name']], \
        configC[ccontainer['@name']], table)
        # clean empty container
        if len(yang[ccontainer['@name']]) == 0:
            del yang[ccontainer['@name']]
        # remove copy after processing
        del configC[ccontainer['@name']]

        return

    """
    Xlate a container
    This function will xlate from a dict in config DB to a Yang JSON container
    using yang model. Output will be stored in self.xlateJson
    """
    def _xlateContainer(self, model, yang, config, table):

        # To Handle multiple Lists, Make a copy of config, because we delete keys
        # from config after each match. This is done to match one pkey with one list.
        configC = config.copy()

        clist = model.get('list')
        # If single list exists in container,
        if clist and isinstance(clist, dict) and \
           clist['@name'] == model['@name']+"_LIST" and bool(configC):
                self._xlateListInContainer(clist, yang, configC, table)
        # If multi-list exists in container,
        elif clist and isinstance(clist, list) and bool(configC):
            for modelList in clist:
                self._xlateListInContainer(modelList, yang, configC, table)

        # Handle container(s) in container
        ccontainer = model.get('container')
        # If single list exists in container,
        if ccontainer and isinstance(ccontainer, dict) and bool(configC):
            self._xlateContainerInContainer(ccontainer, yang, configC, table)
        # If multi-list exists in container,
        elif ccontainer and isinstance(ccontainer, list) and bool(configC):
            for modelContainer in ccontainer:
                self._xlateContainerInContainer(modelContainer, yang, configC, table)

        ## Handle other leaves in container,
        leafDict = self._createLeafDict(model)
        for vKey in configC.keys():
            #vkey must be a leaf\leaf-list\choice in container
            if leafDict.get(vKey):
                self.sysLog(syslog.LOG_DEBUG, "xlateContainer vkey {}".format(vKey))
                yang[vKey] = self._findYangTypedValue(vKey, configC[vKey], leafDict)
                # delete entry from copy of config
                del configC[vKey]

        # All entries in copy of config must have been parsed.
        if len(configC):
            self.sysLog(syslog.LOG_ERR, "Alert: Remaining keys in Config")
            raise(Exception("All Keys are not parsed in {}\n{}".format(table, \
                configC.keys())))

        return

    """
    xlate ConfigDB json to Yang json
    """
    def _xlateConfigDBtoYang(self, jIn, yangJ):

        # find top level container for each table, and run the xlate_container.
        for table in jIn.keys():
            cmap = self.confDbYangMap[table]
            # create top level containers
            key = cmap['module']+":"+cmap['topLevelContainer']
            subkey = cmap['topLevelContainer']+":"+cmap['container']['@name']
            # Add new top level container for first table in this container
            yangJ[key] = dict() if yangJ.get(key) is None else yangJ[key]
            yangJ[key][subkey] = dict()
            self.sysLog(msg="xlateConfigDBtoYang {}:{}".format(key, subkey))
            self._xlateContainer(cmap['container'], yangJ[key][subkey], \
                                jIn[table], table)

        return

    """
    Read config file and crop it as per yang models
    """
    def _xlateConfigDB(self, xlateFile=None):

        jIn= self.jIn
        yangJ = self.xlateJson
        # xlation is written in self.xlateJson
        self._xlateConfigDBtoYang(jIn, yangJ)

        if xlateFile:
            with open(xlateFile, 'w') as f:
                dump(self.xlateJson, f, indent=4)

        return

    """
    create config DB table key from entry in yang JSON
    """
    def _createKey(self, entry, regex):

        keyDict = dict()
        keyV = regex
        # get the keys from regex of key extractor
        keyList = re.findall(r'<(.*?)>', regex)
        for key in keyList:
            val = entry.get(key)
            if val:
                #print("pair: {} {}".format(key, val))
                keyDict[key] = sval = str(val)
                keyV = re.sub(r'<'+key+'>', sval, keyV)
                #print("VAL: {} {}".format(regex, keyV))
            else:
                raise Exception("key {} not found in entry".format(key))
        #print("kDict {}".format(keyDict))
        return keyV, keyDict

    """
    Convert a string from Config DB value to Yang Value based on type of the
    key in Yang model.
    @model : A List of Leafs in Yang model list
    """
    def _revFindYangTypedValue(self, key, value, leafDict):

        # convert yang Type to config DB string
        def _revYangConvert(val):
            # config DB has only strings, thank god for that :), wait not yet!!!
            return str(val)

        # if it is a leaf-list do it for each element
        if leafDict[key]['__isleafList']:
            vValue = list()
            for v in value:
                vValue.append(_revYangConvert(v))
        else:
            vValue = _revYangConvert(value)

        return vValue

    """
    Rev xlate from <TABLE>_LIST to table in config DB
    """
    def _revXlateList(self, model, yang, config, table):

        # fetch regex from YANG models
        keyRegEx = model['ext:key-regex-yang-to-configdb']['@value']
        self.sysLog(msg="revXlateList regex:{}".format(keyRegEx))

        # create a dict to map each key under primary key with a dict yang model.
        # This is done to improve performance of mapping from values of TABLEs in
        # config DB to leaf in YANG LIST.
        leafDict = self._createLeafDict(model)

        # list with name <NAME>_LIST should be removed,
        if "_LIST" in model['@name']:
            for entry in yang:
                # create key of config DB table
                pkey, pkeydict = self._createKey(entry, keyRegEx)
                self.sysLog(syslog.LOG_DEBUG, "revXlateList pkey:{}".format(pkey))
                config[pkey]= dict()
                # fill rest of the entries
                for key in entry:
                    if key not in pkeydict:
                        config[pkey][key] = self._revFindYangTypedValue(key, \
                            entry[key], leafDict)

        return

    """
    Rev xlate a list inside a yang container
    """
    def _revXlateListInContainer(self, model, yang, config, table):
        modelList = model
        # Pass matching list from Yang Json if exist
        if yang.get(modelList['@name']):
            self.sysLog(msg="revXlateListInContainer {}".format(modelList['@name']))
            self._revXlateList(modelList, yang[modelList['@name']], config, table)
        return

    """
    Rev xlate a container inside a yang container
    """
    def _revXlateContainerInContainer(self, model, yang, config, table):
        modelContainer = model
        # Pass matching list from Yang Json if exist
        if yang.get(modelContainer['@name']):
            config[modelContainer['@name']] = dict()
            self.sysLog(msg="revXlateContainerInContainer {}".format(modelContainer['@name']))
            self._revXlateContainer(modelContainer, yang[modelContainer['@name']], \
                config[modelContainer['@name']], table)
        return

    """
    Rev xlate from yang container to table in config DB
    """
    def _revXlateContainer(self, model, yang, config, table):

        # IF container has only one list
        clist = model.get('list')
        if isinstance(clist, dict):
            self._revXlateListInContainer(clist, yang, config, table)
        # IF container has lists
        elif isinstance(clist, list):
            for modelList in clist:
                self._revXlateListInContainer(modelList, yang, config, table)

        ccontainer = model.get('container')
        # IF container has only one inner container
        if isinstance(ccontainer, dict):
            self._revXlateContainerInContainer(ccontainer, yang, config, table)
        # IF container has only many inner container
        elif isinstance(ccontainer, list):
            for modelContainer in ccontainer:
                self._revXlateContainerInContainer(modelContainer, yang, config, table)

        ## Handle other leaves in container,
        leafDict = self._createLeafDict(model)
        for vKey in yang:
            #vkey must be a leaf\leaf-list\choice in container
            if leafDict.get(vKey):
                self.sysLog(syslog.LOG_DEBUG, "revXlateContainer vkey {}".format(vKey))
                config[vKey] = self._revFindYangTypedValue(vKey, yang[vKey], leafDict)

        return

    """
    rev xlate ConfigDB json to Yang json
    """
    def _revXlateYangtoConfigDB(self, yangJ, cDbJson):

        yangJ = self.xlateJson
        cDbJson = self.revXlateJson

        # find table in config DB, use name as a KEY
        for module_top in yangJ.keys():
            # module _top will be of from module:top
            for container in yangJ[module_top].keys():
                #table = container.split(':')[1]
                table = container
                #print("revXlate " + table)
                cmap = self.confDbYangMap[table]
                cDbJson[table] = dict()
                #print(key + "--" + subkey)
                self.sysLog(msg="revXlateYangtoConfigDB {}".format(table))
                self._revXlateContainer(cmap['container'], yangJ[module_top][container], \
                    cDbJson[table], table)

        return

    """
    Reverse Translate tp config DB
    """
    def _revXlateConfigDB(self, revXlateFile=None):

        yangJ = self.xlateJson
        cDbJson = self.revXlateJson
        # xlation is written in self.xlateJson
        self._revXlateYangtoConfigDB(yangJ, cDbJson)

        if revXlateFile:
            with open(revXlateFile, 'w') as f:
                dump(self.revXlateJson, f, indent=4)

        return

    """
    Find a list in YANG Container
    c = container
    l = list name
    return: list if found else None
    """
    def _findYangList(self, container, listName):

        if isinstance(container['list'], dict):
            clist = container['list']
            if clist['@name'] == listName:
                return clist

        elif isinstance(container['list'], list):
            clist = [l for l in container['list'] if l['@name'] == listName]
            return clist[0]

        return None

    """
    Find xpath of the PORT Leaf in PORT container/list. Xpath of Leaf is needed,
    because only leaf can have leafrefs depend on them. (Public)
    """
    def findXpathPortLeaf(self, portName):

        try:
            table = "PORT"
            xpath = self.findXpathPort(portName)
            module, topc, container = self._getModuleTLCcontainer(table)
            list = self._findYangList(container, table+"_LIST")
            xpath = xpath + "/" + list['key']['@value'].split()[0]
        except Exception as e:
            print("find xpath of port Leaf failed")
            raise SonicYangException("find xpath of port Leaf failed\n{}".format(str(e)))

        return xpath

    """
    Find xpath of PORT. (Public)
    """
    def findXpathPort(self, portName):

        try:
            table = "PORT"
            module, topc, container = self._getModuleTLCcontainer(table)
            xpath = "/" + module + ":" + topc + "/" + table

            list = self._findYangList(container, table+"_LIST")
            xpath = self._findXpathList(xpath, list, [portName])
        except Exception as e:
            print("find xpath of port failed")
            raise SonicYangException("find xpath of port failed\n{}".format(str(e)))

        return xpath

    """
    Find xpath of a YANG LIST from keys,
    xpath: xpath till list
    list: YANG List
    keys: list of keys in YANG LIST
    """
    def _findXpathList(self, xpath, list, keys):

        try:
            # add list name in xpath
            xpath = xpath + "/" + list['@name']
            listKeys = list['key']['@value'].split()
            i = 0;
            for listKey in listKeys:
                xpath = xpath + '['+listKey+'=\''+keys[i]+'\']'
                i = i + 1
        except Exception as e:
            raise e

        return xpath

    """
    load_data: load Config DB, crop, xlate and create data tree from it. (Public)
    input:    data
    returns:  True - success   False - failed
    """
    def loadData(self, configdbJson):

       try:
          self.jIn = configdbJson
          # reset xlate and tablesWithOutYang
          self.xlateJson = dict()
          self.tablesWithOutYang = dict()
          # self.jIn will be cropped
          self._cropConfigDB()
          # xlated result will be in self.xlateJson
          self._xlateConfigDB()
          #print(self.xlateJson)
          self.sysLog(msg="Try to load Data in the tree")
          self.root = self.ctx.parse_data_mem(dumps(self.xlateJson), \
                        ly.LYD_JSON, ly.LYD_OPT_CONFIG|ly.LYD_OPT_STRICT)

       except Exception as e:
           self.root = None
           print("Data Loading Failed")
           raise SonicYangException("Data Loading Failed\n{}".format(str(e)))

       return True

    """
    Get data from Data tree, data tree will be assigned in self.xlateJson. (Public)
    """
    def getData(self):

        try:
            self.xlateJson = loads(self._print_data_mem('JSON'))
            # reset reverse xlate
            self.revXlateJson = dict()
            # result will be stored self.revXlateJson
            self._revXlateConfigDB()

        except Exception as e:
            print("Get Data Tree Failed")
            raise SonicYangException("Get Data Tree Failed\n{}".format(str(e)))

        return self.revXlateJson

    """
    Delete a node from data tree, if this is LEAF and KEY Delete the Parent.
    (Public)
    """
    def deleteNode(self, xpath):

        # These MACROS used only here, can we get it from Libyang Header ?
        try:
            LYS_LEAF = 4
            node = self._find_data_node(xpath)
            if node is None:
                raise('Node {} not found'.format(xpath))

            snode = node.schema()
            # check for a leaf if it is a key. If yes delete the parent
            if (snode.nodetype() == LYS_LEAF):
                leaf = ly.Schema_Node_Leaf(snode)
                if leaf.is_key():
                    # try to delete parent
                    nodeP = self._find_parent_data_node(xpath)
                    xpathP = nodeP.path()
                    if self._deleteNode(xpath=xpathP, node=nodeP) == False:
                        raise Exception('_deleteNode failed')
                    else:
                        return True

            # delete non key element
            if self._deleteNode(xpath=xpath, node=node) == False:
                raise Exception('_deleteNode failed')
        except Exception as e:
            raise SonicYangException("Failed to delete node {}\n{}".\
                format( xpath, str(e)))

        return True

    # End of class sonic_yang
