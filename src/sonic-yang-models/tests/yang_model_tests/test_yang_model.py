# This script is used to

import yang as ly
import logging
import argparse
import sys
import ijson
import json
#import sonic_yang as sy
from glob import glob
from os import listdir
from os.path import isfile, join, splitext

#Globals vars
PASS = 0
FAIL = 1
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("YANG-TEST")
log.setLevel(logging.INFO)
log.addHandler(logging.NullHandler())

# Global functions
def printExceptionDetails():
    try:
        excType, excObj, traceBack = sys.exc_info()
        fileName = traceBack.tb_frame.f_code.co_filename
        lineNumber = traceBack.tb_lineno
        log.error(" Exception >{}< in {}:{}".format(excObj, fileName, lineNumber))
    except Exception as e:
        log.error(" Exception in printExceptionDetails")
    return

# class for YANG Model YangModelTesting
# Run function will run all the tests
# from a user given list.

class Test_yang_models:

    def initTest(self):
        self.defaultYANGFailure = {
            'Must': ['Must condition', 'not satisfied'],
            'InvalidValue': ['Invalid value'],
            'LeafRef': ['Leafref', 'non-existing'],
            'When': ['When condition', 'not satisfied'],
            'Pattern': ['pattern', 'does not satisfy'],
            'Mandatory': ['required element', 'Missing'],
            'Verify': ['verified'],
            'Range': ['does not satisfy', 'range'],
            'None': []
        }

        self.ExceptionTests = {
            'WRONG_FAMILY_WITH_IP_PREFIX': {
                'desc': 'Configure Wrong family with ip-prefix for VLAN_Interface Table',
                'eStr': self.defaultYANGFailure['Must']
            },
            'DHCP_SERVER_INCORRECT_FORMAT': {
                'desc': 'Add dhcp_server which is not in correct ip-prefix format.',
                'eStr': self.defaultYANGFailure['InvalidValue'] + ['dhcp_servers']
            },
            'VLAN_WITH_NON_EXIST_PORT': {
                'desc': 'Configure a member port in VLAN_MEMBER table which does not exist.',
                'eStr': self.defaultYANGFailure['LeafRef']
            },
            'PORT_CHANNEL_TEST': {
                'desc': 'Configure a member port in PORT_CHANNEL table.',
                'eStr': self.defaultYANGFailure['None']
            },
            'PORTCHANNEL_MEMEBER_WITH_NON_EXIST_PORTCHANNEL': {
                    'desc': 'Configure PortChannel in PORTCHANNEL_MEMEBER table \
                        which does not exist in PORTCHANNEL table.',
                    'eStr': self.defaultYANGFailure['LeafRef'] + \
                    ['portchannel', 'name']
            },
            'PORTCHANNEL_MEMEBER_WITH_NON_EXIST_PORT': {
                    'desc': 'Configure Port in PORTCHANNEL_MEMEBER table \
                        which does not exist in PORT table.',
                    'eStr': self.defaultYANGFailure['LeafRef'] + \
                    ['port', 'name']
            },
            'PORTCHANNEL_INTERFACE_IP_ADDR_TEST': {
                'desc': 'Configure IP address on PORTCHANNEL_INTERFACE table.',
                'eStr': self.defaultYANGFailure['None']
            },
            'PORTCHANNEL_INTERFACE_IP_ADDR_ON_NON_EXIST_PO': {
                'desc': 'Configure IP address on a non existent PortChannel.',
                'eStr': self.defaultYANGFailure['LeafRef']
            },
            'VLAN_MEMEBER_WITH_NON_EXIST_VLAN': {
                'desc': 'Configure vlan-id in VLAN_MEMBER table which does not exist in VLAN table.',
                'eStr': self.defaultYANGFailure['LeafRef']
            },
            'TAGGING_MODE_WRONG_VALUE': {
                'desc': 'Configure wrong value for tagging_mode.',
                'eStr': self.defaultYANGFailure['InvalidValue'] + ['tagging_mode']
            },
            'INTERFACE_IP_PREFIX_EMPTY_STRING': {
                'desc': 'Configure empty string as ip-prefix in INTERFACE table.',
                'eStr': self.defaultYANGFailure['InvalidValue'] + ['ip-prefix']
            },
            'ACL_RULE_UNDEFINED_PACKET_ACTION': {
                'desc': 'Configure undefined packet_action in ACL_RULE table.',
                'eStr': self.defaultYANGFailure['InvalidValue'] + ['PACKET_ACTION']
            },
            'ACL_TABLE_EMPTY_PORTS': {
                'desc': 'Configure ACL_TABLE with empty ports.',
                'eStr': self.defaultYANGFailure['None']
            },
            'ACL_TABLE_UNDEFINED_TABLE_TYPE': {
                'desc': 'Configure undefined acl_table_type in ACL_TABLE table.',
                'eStr': self.defaultYANGFailure['InvalidValue'] + ['type']
            },
            'ACL_RULE_WITH_NON_EXIST_ACL_TABLE': {
                'desc': 'Configure non-existing ACL_TABLE in ACL_RULE.',
                'eStr': self.defaultYANGFailure['LeafRef']
            },
            'ACL_RULE_IP_TYPE_SRC_IPV6_MISMATCH': {
                'desc': 'Configure IP_TYPE as ipv4any and SRC_IPV6 in ACL_RULE.',
                'eStr': self.defaultYANGFailure['When'] + ['IP_TYPE']
            },
            'ACL_RULE_ARP_TYPE_DST_IPV6_MISMATCH': {
                'desc': 'Configure IP_TYPE as ARP and DST_IPV6 in ACL_RULE.',
                'eStr': self.defaultYANGFailure['When'] + ['IP_TYPE']
            },
            'ACL_RULE_WRONG_L4_SRC_PORT_RANGE': {
                'desc': 'Configure l4_src_port_range as 99999-99999 in ACL_RULE',
                'eStr': self.defaultYANGFailure['Pattern']
            },
            'ACL_RULE_ARP_TYPE_ICMPV6_CODE_MISMATCH': {
                'desc': 'Configure IP_TYPE as ARP and ICMPV6_CODE in ACL_RULE.',
                'eStr': self.defaultYANGFailure['When'] + ['IP_TYPE']
            },
            'ACL_RULE_WRONG_INNER_ETHER_TYPE': {
                'desc': 'Configure INNER_ETHER_TYPE as 0x080C in ACL_RULE.',
                'eStr': self.defaultYANGFailure['Pattern']
            },
            'INTERFACE_IPPREFIX_PORT_MUST_CONDITION_FALSE': {
                'desc': 'Interface Ip-prefix port-name must condition failure.',
                'eStr': self.defaultYANGFailure['Must']
            },
            'INTERFACE_IPPREFIX_PORT_MUST_CONDITION_TRUE': {
                'desc': 'Interface Ip-prefix port-name must condition pass.',
                'eStr': self.defaultYANGFailure['None']
            },
            'VLAN_INTERFACE_IPPREFIX_MUST_CONDITION_FALSE': {
                'desc': 'Vlan Interface Ip-prefix must condition failure.',
                'eStr': self.defaultYANGFailure['Must']
            },
            'LOOPBACK_IPPREFIX_PORT_MUST_CONDITION_FALSE': {
                'desc': 'Loopback Ip-prefix port-name must condition failure.',
                'eStr': self.defaultYANGFailure['Must']
            },
            'CRM_BRK_CFG_FLEX_TABLE': {
                'desc': 'CRM BREAKOUT CFG FLEX COUNTER TABLE.',
                'eStr': self.defaultYANGFailure['None']
            },
            'DEV_META_DEV_NEIGH_VERSION_TABLE': {
                'desc': 'DEVICE_METADATA DEVICE_NEIGHBOR VERSION TABLE.',
                'eStr': self.defaultYANGFailure['None']
            },
            'INCORRECT_VLAN_NAME': {
                'desc': 'INCORRECT VLAN_NAME FIELD IN VLAN TABLE.',
                'eStr': self.defaultYANGFailure['Pattern'] + ["Vlan"]
            },
            'ACL_TABLE_MANDATORY_TYPE': {
                'desc': 'ACL_TABLE MANDATORY TYPE FIELD.',
                'eStr': self.defaultYANGFailure['Mandatory'] + ['type'] + ['ACL_TABLE']
            },
            'ACL_TABLE_DEFAULT_VALUE_STAGE': {
                'desc': 'ACL_TABLE DEFAULT VALUE FOR STAGE FIELD.',
                'eStr': self.defaultYANGFailure['Verify'],
                'verify': {'xpath': "/sonic-acl:sonic-acl/ACL_TABLE/ACL_TABLE_LIST[ACL_TABLE_NAME='NO-NSW-PACL-V4']/ACL_TABLE_NAME",
                    'key': 'sonic-acl:stage',
                    'value': 'INGRESS'
                }
            },
            'INCORRECT_VLAN_NAME': {
                'desc': 'INCORRECT VLAN_NAME FIELD IN VLAN TABLE.',
                'eStr': self.defaultYANGFailure['Pattern'] + ["Vlan"]
            },
            'PORT_CHANNEL_WRONG_PATTERN': {
                'desc': 'INCORRECT PORTCHANNEL_NAME IN PORT_CHANNEL TABLE.',
                'eStr': self.defaultYANGFailure['Pattern'] + ["PortChannel"]
            },
            'ACL_TABLE_STAGE_SERVICES': {
                'desc': 'ACL_TABLE LOAD STAGE SERVICES SUCCESSFULLY.',
                'eStr': self.defaultYANGFailure['Verify'],
                'verify': {'xpath': "/sonic-acl:sonic-acl/ACL_TABLE/ACL_TABLE_LIST[ACL_TABLE_NAME='NO-NSW-PACL-V4']/ACL_TABLE_NAME",
                    'key': 'sonic-acl:services',
                    'value': ["SNMP"]
                }
            },
            'PORT_TEST': {
                'desc': 'LOAD PORT TABLE WITH FEC AND PFC_ASYM SUCCESSFULLY. VERIFY PFC_ASYM.',
                'eStr': self.defaultYANGFailure['Verify'],
                'verify': {'xpath': "/sonic-port:sonic-port/PORT/PORT_LIST[name='Ethernet8']/name",
                    'key': 'sonic-port:pfc_asym',
                    'value': 'on'
                }
            },
            'PORT_NEG_TEST': {
                'desc': 'LOAD PORT TABLE FEC PATTERN FAILURE',
                'eStr': self.defaultYANGFailure['Pattern'] + ['rc']
            },
            'PORT_VALID_AUTONEG_TEST_1': {
                'desc': 'PORT_VALID_AUTONEG_TEST_1 no failure.',
                'eStr': self.defaultYANGFailure['None']
            },
            'PORT_VALID_AUTONEG_TEST_2': {
                'desc': 'PORT_VALID_AUTONEG_TEST_2 no failure.',
                'eStr': self.defaultYANGFailure['None']
            },
            'PORT_INVALID_AUTONEG_TEST': {
                'desc': 'PORT_INVALID_AUTONEG_TEST must condition failure.',
                'eStr': self.defaultYANGFailure['Pattern'] + ['on|off']
            },
            'CRM_WITH_WRONG_PERCENTAGE': {
                'desc': 'CRM_WITH_WRONG_PERCENTAGE must condition failure.',
                'eStr': self.defaultYANGFailure['Must']
            },
            'CRM_WITH_HIGH_THRESHOLD_ERR': {
                'desc': 'CRM_WITH_HIGH_THRESHOLD_ERR must condition failure \
                    about high threshold being lower than low threshold.',
                'eStr': ['high_threshold should be more than low_threshold']
            },
            'CRM_WITH_CORRECT_FREE_VALUE': {
                'desc': 'CRM_WITH_CORRECT_FREE_VALUE no failure.',
                'eStr': self.defaultYANGFailure['None']
            },
            'CRM_WITH_CORRECT_USED_VALUE': {
                'desc': 'CRM_WITH_CORRECT_USED_VALUE no failure.',
                'eStr': self.defaultYANGFailure['None']
            },
            'CRM_WITH_WRONG_THRESHOLD_TYPE': {
                'desc': 'CRM_WITH_WRONG_THRESHOLD_TYPE pattern failure.',
                'eStr': self.defaultYANGFailure['Pattern'] + ['wrong']
            },
            'FLEX_COUNTER_TABLE_WITH_CORRECT_USED_VALUE': {
                'desc': 'FLEX_COUNTER_TABLE_WITH_CORRECT_USED_VALUE no failure.',
                'eStr': self.defaultYANGFailure['None']
            },
            'VERSIONS_WITH_INCORRECT_PATTERN': {
                'desc': 'VERSIONS_WITH_INCORRECT_PATTERN pattern failure.',
                'eStr': self.defaultYANGFailure['Pattern']
            },
            'VERSIONS_WITH_INCORRECT_PATTERN2': {
                'desc': 'VERSIONS_WITH_INCORRECT_PATTERN pattern failure.',
                'eStr': self.defaultYANGFailure['Pattern']
            },
            'DEVICE_METADATA_DEFAULT_BGP_STATUS': {
                'desc': 'DEVICE_METADATA DEFAULT VALUE FOR BGP_STATUS FIELD.',
                'eStr': self.defaultYANGFailure['Verify'],
                'verify': {'xpath': '/sonic-device_metadata:sonic-device_metadata/DEVICE_METADATA/localhost/hostname',
                    'key': 'sonic-device_metadata:default_bgp_status',
                    'value': 'up'
                }
            },
            'DEVICE_METADATA_DEFAULT_DOCKER_ROUTING_CONFIG_MODE': {
                'desc': 'DEVICE_METADATA DEFAULT VALUE FOR DOCKER_ROUTING_CONFIG_MODE FIELD.',
                'eStr': self.defaultYANGFailure['Verify'],
                'verify': {'xpath': '/sonic-device_metadata:sonic-device_metadata/DEVICE_METADATA/localhost/hostname',
                    'key': 'sonic-device_metadata:docker_routing_config_mode',
                    'value': 'unified'
                }
            },
            'DEVICE_METADATA_DEFAULT_PFCWD_STATUS': {
                'desc': 'DEVICE_METADATA DEFAULT VALUE FOR PFCWD FIELD.',
                'eStr': self.defaultYANGFailure['Verify'],
                'verify': {'xpath': '/sonic-device_metadata:sonic-device_metadata/DEVICE_METADATA/localhost/hostname',
                    'key': 'sonic-device_metadata:default_pfcwd_status',
                    'value': 'disable'
                }
            },
            'DEVICE_METADATA_TYPE_INCORRECT_PATTERN': {
                'desc': 'DEVICE_METADATA_TYPE_INCORRECT_PATTERN pattern failure.',
                'eStr': self.defaultYANGFailure['Pattern']
            },
            'BREAKOUT_CFG_CORRECT_MODES': {
                'desc': 'BREAKOUT_CFG correct breakout modes',
                'eStr': self.defaultYANGFailure['None']
            },
            'BREAKOUT_CFG_INCORRECT_MODES': {
                'desc': 'BREAKOUT_CFG wrong breakout modes',
                'eStr': self.defaultYANGFailure['Pattern']
            },
            'SNAT_WITH_WRONG_PERCENTAGE': {
                'desc': 'SNAT_WITH_WRONG_PERCENTAGE must condition failure.',
                'eStr': self.defaultYANGFailure['Must']
            },
            'SNAT_WITH_HIGH_THRESHOLD_ERR': {
                'desc': 'SNAT_WITH_HIGH_THRESHOLD_ERR must condition failure \
                    about high threshold being lower than low threshold.',
                'eStr': ['high_threshold should be more than low_threshold']
            },
            'SNAT_WITH_CORRECT_FREE_VALUE': {
                'desc': 'SNAT_WITH_CORRECT_FREE_VALUE no failure.',
                'eStr': self.defaultYANGFailure['None']
            },
            'SNAT_WITH_CORRECT_USED_VALUE': {
                'desc': 'SNAT_WITH_CORRECT_USED_VALUE no failure.',
                'eStr': self.defaultYANGFailure['None']
            },
            'SNAT_WITH_WRONG_THRESHOLD_TYPE': {
                'desc': 'SNAT_WITH_WRONG_THRESHOLD_TYPE pattern failure.',
                'eStr': self.defaultYANGFailure['Pattern'] + ['wrong']
            },
            'DNAT_WITH_WRONG_PERCENTAGE': {
                'desc': 'DNAT_WITH_WRONG_PERCENTAGE must condition failure.',
                'eStr': self.defaultYANGFailure['Must']
            },
            'DNAT_WITH_HIGH_THRESHOLD_ERR': {
                'desc': 'DNAT_WITH_HIGH_THRESHOLD_ERR must condition failure \
                    about high threshold being lower than low threshold.',
                'eStr': ['high_threshold should be more than low_threshold']
            },
            'DNAT_WITH_CORRECT_FREE_VALUE': {
                'desc': 'DNAT_WITH_CORRECT_FREE_VALUE no failure.',
                'eStr': self.defaultYANGFailure['None']
            },
            'DNAT_WITH_CORRECT_USED_VALUE': {
                'desc': 'DNAT_WITH_CORRECT_USED_VALUE no failure.',
                'eStr': self.defaultYANGFailure['None']
            },
            'DNAT_WITH_WRONG_THRESHOLD_TYPE': {
                'desc': 'DNAT_WITH_WRONG_THRESHOLD_TYPE pattern failure.',
                'eStr': self.defaultYANGFailure['Pattern'] + ['wrong']
            },
            'IPMC_WITH_WRONG_PERCENTAGE': {
                'desc': 'IPMC_WITH_WRONG_PERCENTAGE must condition failure.',
                'eStr': self.defaultYANGFailure['Must']
            },
            'IPMC_WITH_HIGH_THRESHOLD_ERR': {
                'desc': 'IPMC_WITH_HIGH_THRESHOLD_ERR must condition failure \
                    about high threshold being lower than low threshold.',
                'eStr': ['high_threshold should be more than low_threshold']
            },
            'IPMC_WITH_CORRECT_FREE_VALUE': {
                'desc': 'IPMC_WITH_CORRECT_FREE_VALUE no failure.',
                'eStr': self.defaultYANGFailure['None']
            },
            'IPMC_WITH_CORRECT_USED_VALUE': {
                'desc': 'IPMC_WITH_CORRECT_USED_VALUE no failure.',
                'eStr': self.defaultYANGFailure['None']
            },
            'IPMC_WITH_WRONG_THRESHOLD_TYPE': {
                'desc': 'IPMC_WITH_WRONG_THRESHOLD_TYPE pattern failure.',
                'eStr': self.defaultYANGFailure['Pattern'] + ['wrong']
            }
        }

        self.SpecialTests = {
            'ALL_VLAN_TEST': {
                'desc': 'VLAN TEST.',
                'eStr': self.defaultYANGFailure['None']
            }
        }

        self.tests = list(self.ExceptionTests.keys())+list(self.SpecialTests.keys())
        self.yangDir = './yang-models/'
        self.jsonFile = './tests/yang_model_tests/yangTest.json'
        self.testNum = 1
        # other class vars
        # self.ctx
        return

    """
        load all YANG models before test run
    """
    def loadYangModel(self, yangDir):

        try:
            # create context
            self.ctx = ly.Context(yangDir)
            # get all files
            yangFiles = glob(yangDir +"/*.yang")
            # load yang modules
            for file in yangFiles:
                log.debug(file)
                m = self.ctx.parse_module_path(file, ly.LYS_IN_YANG)
                if m is not None:
                    log.info("module: {} is loaded successfully".format(m.name()))
                else:
                    log.info("Could not load module: {}".format(file))

        except Exception as e:
            printExceptionDetails()
            raise e
        return

    """
        Get the JSON input based on func name
        and return jsonInput
    """
    def readJsonInput(self, test):
        try:
            # load test specific Dictionary, using Key = func
            # this is to avoid loading very large JSON in memory
            log.debug(" Read JSON Section: " + test)
            jInput = ""
            with open(self.jsonFile, 'rb') as f:
                jInst = ijson.items(f, test)
                for it in jInst:
                    jInput = jInput + json.dumps(it)
            log.debug("Read json JIn: {}".format(jInput))
        except Exception as e:
            printExceptionDetails()
        return jInput

    """
        Log the start of a test
    """
    def logStartTest(self, desc):
        log.info("\n------------------- Test "+ str(self.testNum) +\
        ": " + desc + "---------------------")
        self.testNum = self.testNum + 1
        return

    """
        Load Config Data and return Exception as String

        Parameters:
            jInput (dict): input config to load.
            verify (dict): contains xpath, key and value. This is used to verify,
            that node tree at xpath contains correct key and value.
            Example:
            'verify': {'xpath': "/sonic-acl:sonic-acl/ACL_TABLE/ACL_TABLE_LIST\
                        [ACL_TABLE_NAME='NO-NSW-PACL-V4']/stage",
                        'key': 'sonic-acl:stage',
                        'value': 'INGRESS'
            }
    """
    def loadConfigData(self, jInput, verify=None):
        s = ""
        try:
            node = self.ctx.parse_data_mem(jInput, ly.LYD_JSON, \
            ly.LYD_OPT_CONFIG | ly.LYD_OPT_STRICT)
            # verify the data tree if asked
            if verify is not None:
                xpath = verify['xpath']
                log.info("Verify xpath: {}".format(xpath))
                set = node.find_path(xpath)
                for dnode in set.data():
                    if (xpath == dnode.path()):
                        log.info("Verify dnode: {}".format(dnode.path()))
                        data = dnode.print_mem(ly.LYD_JSON, ly.LYP_WITHSIBLINGS \
                            | ly.LYP_FORMAT | ly.LYP_WD_ALL)
                        data = json.loads(data)
                        log.info("Verify data: {}".format(data))
                        assert (data[verify['key']] == verify['value'])
                        s = 'verified'
        except Exception as e:
            s = str(e)
            log.info(s)
        return s

    """
        Run Exception Test
    """
    def runExceptionTest(self, test):
        try:
            desc = self.ExceptionTests[test]['desc']
            self.logStartTest(desc)
            jInput = self.readJsonInput(test)
            # load the data, expect a exception with must condition failure
            s = self.loadConfigData(jInput, self.ExceptionTests[test].get('verify'))
            eStr = self.ExceptionTests[test]['eStr']
            log.debug("eStr: {}".format(eStr))
            if len(eStr) == 0 and s != "":
                raise Exception("{} in not empty".format(s))
            elif (sum(1 for str in eStr if str not in s) == 0):
                log.info(desc + " Passed\n")
                return PASS
            else:
                raise Exception("Mismatch {} and {}".format(eStr, s))
        except Exception as e:
            printExceptionDetails()
        log.info(desc + " Failed\n")
        return FAIL

    """
        Run Special Tests
    """
    def runSpecialTest(self, test):
        try:
            if test == 'ALL_VLAN_TEST':
                return self.runVlanSpecialTest(test);
        except Exception as e:
            printExceptionDetails()
        log.info(desc + " Failed\n")
        return FAIL

    def runVlanSpecialTest(self, test):
        try:
            desc = self.SpecialTests[test]['desc']
            self.logStartTest(desc)
            jInput = json.loads(self.readJsonInput(test))
            # check all Vlan from 1 to 4094
            for i in range(4095):
                vlan = 'Vlan'+str(i)
                jInput["sonic-vlan:sonic-vlan"]["sonic-vlan:VLAN"]["VLAN_LIST"]\
                      [0]["name"] = vlan
                log.debug(jInput)
                s = self.loadConfigData(json.dumps(jInput))
                if s!="":
                    raise Exception("{} in not empty".format(s))
            return PASS
        except Exception as e:
            printExceptionDetails()
        log.info(desc + " Failed\n")
        return FAIL

    """
        Run all tests from list self.tests
    """
    def test_run_tests(self):
        ret = 0
        try:
            self.initTest()
            self.loadYangModel(self.yangDir)
            assert len(self.tests) != 0
            print("Tests:{}".format(self.tests))
            for test in self.tests:
                test = test.strip()
                if test in self.ExceptionTests:
                    ret = ret + self.runExceptionTest(test);
                elif test in self.SpecialTests:
                    ret = ret + self.runSpecialTest(test);
                else:
                    raise Exception("Unexpected Test")
        except Exception as e:
            ret = FAIL * len(self.tests)
            printExceptionDetails()

        assert ret == 0
        return
# End of Class

"""
    Start Here
"""
def main():
    parser = argparse.ArgumentParser(description='Script to run YANG model tests',
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     epilog="""
Usage:
python yangModelTesting.py -h
""")
    parser.add_argument('-t', '--tests', type=str, \
    help='tests to run separated by comma')
    parser.add_argument('-f', '--json-file', type=str, \
    help='JSON input for tests ', required=True)
    parser.add_argument('-y', '--yang-dir', type=str, \
    help='Path to YANG models', required=True)
    parser.add_argument('-v', '--verbose-level', \
    help='Verbose mode', action='store_true')
    parser.add_argument('-l', '--list-tests', \
    help='list all tests', action='store_true')

    args = parser.parse_args()
    try:
        tests = args.tests
        jsonFile = args.json_file
        yangDir = args.yang_dir
        logLevel = args.verbose_level
        listTests = args.list_tests
        if logLevel:
            log.setLevel(logging.DEBUG)
        # Make a list
        if (tests):
            tests = tests.split(",")

        yTest = YangModelTesting(tests, yangDir, jsonFile)
        if (listTests):
            for key in yTest.ExceptionTests.keys():
                log.info(key)
            sys.exit(0)

        ret = yTest.run()
        if ret == 0:
            log.info("All Test Passed")
        sys.exit(ret)

    except Exception as e:
        printExceptionDetails()
        sys.exit(1)

    return
if __name__ == '__main__':
    main()
