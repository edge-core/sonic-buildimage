#!/usr/bin/python3

from datetime import datetime
import time
import datetime
import os
import subprocess
import sys
import threading
import syslog
import argparse
import multiprocessing as mp
from swsssdk import ConfigDBConnector
from swsssdk import SonicV2Connector
import socket
import json
import fcntl
import stat

SYSLOG_IDENTIFIER="system#monitor"
STATE_FEATURE_TABLE_NAME = "FEATURE"
REDIS_TIMEOUT_MS = 0
SYSTEM_STATE="DOWN"
logger = None
SYSTEM_CORESRV_STATE="DOWN"
SYSTEM_ALLSRV_STATE="DOWN"
SYSREADY_LOCKFILE="/var/run/sysready.lock"
core_dnsrvs_name_list=[]
dnsrvs_name_list=[]
allsrvs_dict={}
coresrvs_dict={}
allsrvs_status="DOWN"
coresrvs_status="DOWN"
spl_srv_list= ['database-chassis', 'gbsyncd']
core_srv_list = [
        'swss.service',
        'bgp.service',
        'teamd.service',
        'pmon.service',
        'syncd.service',
        'database.service',
        'mgmt-framework.service',
]

class FileLock:
   def __init__(self, lock_file):
      self.f = open(lock_file, 'w')

   def lock(self):
      fcntl.flock(self.f, fcntl.LOCK_EX)

   def unlock(self):
      fcntl.flock(self.f, fcntl.LOCK_UN)

sysready_lock = FileLock(SYSREADY_LOCKFILE)


class Logger(object):
    def __init__(self, syslog_identifier):
        syslog.openlog(ident=syslog_identifier, logoption=syslog.LOG_NDELAY, facility=syslog.LOG_DAEMON)

    #def __del__(self):
        #syslog.closelog()

    def log_emerg(self, msg, also_print_to_console=False):
        syslog.syslog(syslog.LOG_EMERG, msg)

        if also_print_to_console:
            print(msg)

    def log_crit(self, msg, also_print_to_console=False):
        syslog.syslog(syslog.LOG_CRIT, msg)

        if also_print_to_console:
            print(msg)

    def log_alert(self, msg, also_print_to_console=False):
        syslog.syslog(syslog.LOG_ALERT, msg)

        if also_print_to_console:
            print(msg)


    def log_error(self, msg, also_print_to_console=False):
        syslog.syslog(syslog.LOG_ERR, msg)

        if also_print_to_console:
            print(msg)

    def log_warning(self, msg, also_print_to_console=False):
        syslog.syslog(syslog.LOG_WARNING, msg)

        if also_print_to_console:
            print(msg)

    def log_notice(self, msg, also_print_to_console=False):
        syslog.syslog(syslog.LOG_NOTICE, msg)

        if also_print_to_console:
            print(msg)

    def log_info(self, msg, also_print_to_console=False):
        syslog.syslog(syslog.LOG_INFO, msg)

        if also_print_to_console:
            print(msg)

    def log_debug(self, msg, also_print_to_console=False):
        syslog.syslog(syslog.LOG_DEBUG, msg)

        if also_print_to_console:
            print(msg)

#Initalise the syslog infrastructure
logger = Logger(SYSLOG_IDENTIFIER)

class Dict2Obj(object):
    """dict to dict2obj
    d: data"""

    def __init__(self, d):
        for a, b in list(d.items()):
            if isinstance(b, (list, tuple)):
                setattr(self, a, [Dict2Obj(x) if isinstance(
                    x, dict) else x for x in b])
            else:
                setattr(self, a, Dict2Obj(b) if isinstance(b, dict) else b)


def print_console_message(message):
    with open('/dev/console', 'w') as console:
        console.write("\n{} {} \n ".format(datetime.datetime.now().strftime("%b %d %H:%M:%S.%f"), message))

def post_system_status_core(state, st_db):
    if st_db:
        st_db.set(st_db.STATE_DB, "SYSTEM_READY|SYSTEM_STATE_CORE", "status", state)

def post_system_status_all(state, st_db):
    if st_db:
        st_db.set(st_db.STATE_DB, "SYSTEM_READY|SYSTEM_STATE_ALL", "status", state)

def run_systemctl_show(service):
    a = subprocess.check_output(["systemctl", "show", service, "--property=Id,LoadState,UnitFileState,Type,ActiveState,SubState,Result"], universal_newlines=True).split('\n')
    json_dict = {}
    for e in a:
        kv = e.split("=", 1)
        if len(kv) == 2:
            json_dict[kv[0]] = kv[1]
    result = Dict2Obj(json_dict)
    return result

def get_all_service_list(config_db):
    dir_list=[]

    #add the services from the below targets
    path= ["/etc/systemd/system/multi-user.target.wants", "/etc/systemd/system/sonic.target.wants"]
    for p in path:
        if os.path.exists(p):
            dir_list+= os.listdir(p)
    
    #add the enabled docker services from config db feature table
    feature_table = config_db.get_table("FEATURE")
    for srv in feature_table.keys():
        if feature_table[srv]["state"] not in ["disabled", "always_disabled"]:
            srvext=srv+".service"
            if srvext not in dir_list:
                dir_list.append(srvext)
    
    #Keep ZTP in exclusion list
    exclude_list= ['aaastatsd.service', 'aaastatsd.timer' , 'rasdaemon.service', 'ztp.service', 'sonic.target', 'sonic-delayed.target']
    for l in exclude_list:
        if l in dir_list:
            dir_list.remove(l)
    
    #sort it
    dir_list.sort()

    return dir_list


def get_app_ready_status(service, ap_db, st_db, config_db):
    #check FEATURE table from config db for the service' check_up_status flag
    #if marked to true, then read the service up_status field from FEATURE table of state db.
    #else, just return true (or) Up
    fail_reason=""
    configdb_feature_table = config_db.get_table('FEATURE')
    configdb_host_feature_table = config_db.get_table('HOST_FEATURE')
    service_name = service

    if service_name not in configdb_feature_table.keys() and service_name not in configdb_host_feature_table.keys():
        pstate = "Up"
    else:
        if service_name in configdb_feature_table.keys():
            check_app_up_status = configdb_feature_table[service_name].get('check_up_status')
        elif service_name in configdb_host_feature_table.keys():
            check_app_up_status = configdb_host_feature_table[service_name].get('check_up_status')

        if check_app_up_status == "true":
            up_status_flag = st_db.get(st_db.STATE_DB, 'FEATURE|{}'.format(service_name), 'up_status')
            if up_status_flag == "true":
                pstate = "Up"
            else:
                fail_reason = st_db.get(st_db.STATE_DB, 'FEATURE|{}'.format(service_name), 'fail_reason')
                if fail_reason is None:
                    fail_reason = "NA"
                pstate = "Down"
        else:
            #Either check_up_status marked false or entry does not exist
            pstate = "Up"

    return pstate,fail_reason


def get_unit_status(event, ap_db, st_db, config_db):
    """ Get a unit status"""
    global coresrvs_dict
    global core_srv_list
    global allsrvs_dict
    global spl_srv_list
    unit_status = "NOTOK"
    fail_reason="Unknown"
    try:
        service_status = "Not OK"
        service_up_status = "Not OK"
        service_name,last_name = event.split('.')
        sysctl_show = run_systemctl_show(event)
        load_state = sysctl_show.LoadState
        if load_state == "loaded":
            status = sysctl_show.UnitFileState
            fail_reason = sysctl_show.Result
            active_state = sysctl_show.ActiveState
            sub_state = sysctl_show.SubState
            srv_type = sysctl_show.Type

            #Raise syslog for service state change
            logger.log_info("{} service state changed to [{}/{}]".format(event, active_state, sub_state))

            if status == "enabled" or status == "enabled-runtime" or status == "static":
                if fail_reason == "success":
                    fail_reason = "-"
                if (active_state == "active" and sub_state == "exited"):
                    service_status = "OK"
                    service_up_status = "OK"
                    unit_status = "OK"
                elif active_state == "active" and sub_state == "running":
                    service_status = "OK"
                    init_state,app_fail_reason = get_app_ready_status(service_name, ap_db, st_db, config_db)
                    if init_state == "Up":
                        service_up_status = "OK"
                        unit_status = "OK"
                    else:
                        fail_reason = app_fail_reason
                        unit_status = "NOTOK"
                        if fail_reason == "docker start":
                            service_up_status = "Starting"
                            fail_reason = "-"
                elif active_state == "activating":
                    service_status = "Starting"
                    service_up_status = "Starting"
                elif active_state == "deactivating":
                    service_status = "Stopping"
                    service_up_status = "Stopping"
                elif active_state == "inactive":
                    if srv_type == "oneshot" or service_name in spl_srv_list:
                        service_status = "OK"
                        service_up_status = "OK"
                        unit_status = "OK"
                    else:
                        unit_status = "NOTOK"
                        if fail_reason == "-":
                            fail_reason = "Inactive"
                else:
                    unit_status = "NOTOK"

                if event in core_srv_list:
                    coresrvs_dict[service_name] = {"service_status":service_status, "service_up_status":service_up_status, "fail_reason":fail_reason}

                allsrvs_dict[service_name] = {"service_status":service_status, "service_up_status":service_up_status, "fail_reason":fail_reason}

                return unit_status

    except Exception as e:
        logger.log_error("Get unit status {}-{}".format(service_name, str(e)))


def get_all_system_status(ap_db, st_db, config_db):
    """ Shows the system ready status"""
    global dnsrvs_name_list
    global allsrvs_status
    scan_srv_list=[]
    overall_ok_flag = 1
    
    scan_srv_list=get_all_service_list(config_db)
    #logger.log_info("scan_srv_list:[{}]".format(scan_srv_list))

    for service in scan_srv_list:
        ustate = get_unit_status(service,ap_db,st_db,config_db)
        if ustate == "NOTOK":
            overall_ok_flag &= 0
            dnsrvs_name_list.append(service)

    if overall_ok_flag == 1:
        allsrvs_status = "UP"
        return ("UP", "System is ready with all the services")
    else:
        allsrvs_status = "DOWN"
        return ("DOWN", "System is not ready - one or more services are not up")


def get_core_system_status(ap_db, st_db,config_db):
    """ Shows the core system ready status"""
    global core_srv_list
    global core_dnsrvs_name_list
    global coresrvs_status
    core_ok_flag = 1

    for service in core_srv_list:
        ustate = get_unit_status(service,ap_db,st_db,config_db)
        if ustate == "NOTOK":
            core_ok_flag &= 0
            core_dnsrvs_name_list.append(service)

    if core_ok_flag == 1:
        coresrvs_status = "UP"
        return ("UP", "System is ready")
    else:
        coresrvs_status = "DOWN"
        return ("DOWN", "System is not ready - core services are not ok")


#Checks current system status
def check_system_status(event, st_db, ap_db, config_db):
    global SYSTEM_STATE
    (cstate, msg) = get_core_system_status(ap_db, st_db,config_db)
    if SYSTEM_STATE != cstate:
        SYSTEM_STATE=cstate
        logger.log_notice(msg)
        print_console_message(msg)
        post_system_status_core(cstate, st_db)


    global SYSTEM_ALLSRV_STATE
    (astate, msg) = get_all_system_status(ap_db, st_db, config_db)
    if SYSTEM_ALLSRV_STATE != astate:
        SYSTEM_ALLSRV_STATE=astate
        logger.log_info(msg)
        print_console_message(msg)
        post_system_status_all(astate, st_db)

#Checks the unit status and updates the system status
def check_unit_status(event, st_db, ap_db, config_db):
    global SYSTEM_STATE
    global SYSTEM_ALLSRV_STATE
    global core_dnsrvs_name_list
    global dnsrvs_name_list
    global core_srv_list
    global coresrvs_status
    global allsrvs_status
    global allsrvs_dict

    #astate="DOWN"
    #cstate="DOWN"
    #msg=""

    #check for core status
    if event in core_srv_list:
        ustate = get_unit_status(event,ap_db,st_db,config_db)
        if ustate == "OK" and SYSTEM_STATE == "UP":
            cstate = "UP"
        elif ustate == "OK" and SYSTEM_STATE == "DOWN":
            if event in core_dnsrvs_name_list:
                core_dnsrvs_name_list.remove(event)
                #need to check if need to set cstate to UP if this was the only down service before, which became UP now.
                if len(core_dnsrvs_name_list) == 0:
                    cstate = "UP"
                else:
                    cstate = "DOWN"
        else:
            if event not in core_dnsrvs_name_list:
                core_dnsrvs_name_list.append(event)
            cstate = "DOWN"

        if cstate == "DOWN":
            msg = "System is not ready - core services are not ok"
            coresrvs_status = "DOWN"
        else:
            msg = "System is ready with core services"
            coresrvs_status = "UP"

        #logger.log_info("core - event:{}  ustate:{} cstate:{} dnsrv:{}".format(event,ustate,cstate,core_dnsrvs_name_list))

        if SYSTEM_STATE != cstate:
            SYSTEM_STATE=cstate
            logger.log_notice(msg)
            print_console_message(msg)
            post_system_status_core(cstate, st_db)

    #check for all status
    full_srv_list=get_all_service_list(config_db)
    #logger.log_info("full srv list:{}".format(full_srv_list))
    if event in full_srv_list:
        ustate = get_unit_status(event,ap_db,st_db,config_db)
        if ustate == "OK" and SYSTEM_ALLSRV_STATE == "UP":
            astate = "UP"
        elif ustate == "OK" and SYSTEM_ALLSRV_STATE == "DOWN":
            if event in dnsrvs_name_list:
                dnsrvs_name_list.remove(event)
                #need to check if need to set cstate to UP if this was the only down service before, which became UP now.
                if len(dnsrvs_name_list) == 0:
                    astate = "UP"
                else:
                    astate = "DOWN"
        else:
            if event not in dnsrvs_name_list:
                dnsrvs_name_list.append(event)
            astate = "DOWN"

        if astate == "DOWN":
            msg = "System is not ready - one or more services are not ok"
            allsrvs_status = "DOWN"
        else:
            msg = "System is ready with all the services"
            allsrvs_status = "UP"

        #logger.log_info("all - event:{}  ustate:{} astate:{} dnsrvs:{}".format(event,ustate,astate,dnsrvs_name_list))

        if SYSTEM_ALLSRV_STATE != astate:
            SYSTEM_ALLSRV_STATE=astate
            logger.log_info(msg)
            print_console_message(msg)
            post_system_status_all(astate, st_db)

    else:
        #if received event is not in current full service list but exists in global dictionary & list, then it should be removed from dictionary & list
        srv_name,last_name = event.split('.')
        if allsrvs_dict.__contains__(srv_name):
            allsrvs_dict.pop(srv_name)

        #also remove from dnsrvslist
        if event in dnsrvs_name_list:
            dnsrvs_name_list.remove(event)




##############################################################
#             Listen for STATEDB state event                 #
##############################################################

def subscribe_statedb(queue):
    from swsscommon import swsscommon

    while True:
        try:
            logger.log_info( "Listening for StateDB event, Pid:{}".format(os.getpid()))
            SELECT_TIMEOUT_MS = 1000 * 2

            db = swsscommon.DBConnector("STATE_DB", REDIS_TIMEOUT_MS, True)
            sel = swsscommon.Select()
            cst = swsscommon.SubscriberStateTable(db, STATE_FEATURE_TABLE_NAME)
            sel.addSelectable(cst)

            while True:
                (state, c) = sel.select(SELECT_TIMEOUT_MS)
                if state == swsscommon.Select.OBJECT:
                    (key, op, cfvs) = cst.pop()
                    #logger.log_info(key+"featureevent")
                    key_ext = key+".service"
                    queue.put(key_ext)
        except Exception as e:
            logger.log_error( str(e))

        time.sleep(2)


def subscribe_statedb_event_thread(queue):
    while True:
        try:
            process_statedb_event = mp.Process(target=subscribe_statedb, args=(queue,) )
            process_statedb_event.start()
            process_statedb_event.join()
        except Exception as e:
            logger.log_error( str(e))

        time.sleep(1)

##############################################################
#             Listening for System service event             #
##############################################################

QUEUE=None
def OnJobRemoved(id, job, unit, result):

    global QUEUE

    #logger.log_debug('{}: Job Removed: {}, {}, {} '.format( id, job, unit, result))
    if result == "done":
        QUEUE.put(unit)
        return


#Sub process for listening the systemd event on dbus
def subscribe_service_event(queue):
    import dbus
    from gi.repository import GObject
    from dbus.mainloop.glib import DBusGMainLoop

    #logger.log_info( "Listening for systemd service event, Pid:{}".format(os.getpid()))
    DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()
    systemd = bus.get_object('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
    manager = dbus.Interface(systemd, 'org.freedesktop.systemd1.Manager')

    manager.Subscribe()
    manager.connect_to_signal('JobRemoved', OnJobRemoved)

    loop = GObject.MainLoop()
    loop.run()


#Start the subprocess to listen the systemd service state change event
def subscribe_service_event_thread(queue):
    retry_count=0
    while True:
        try:
            process_service_event = mp.Process(target=subscribe_service_event, args=(queue,) )
            process_service_event.start()
            process_service_event.join()
        except Exception as e:
            logger.log_error( str(e))

        time.sleep(60)
        retry_count+=1
        if retry_count > 10:
            logger.log_error("dbus subscription for systemd1 failed multiple times, exiting the subscription")
            break


def status_core(req):
    """shows the system status core"""
    global coresrvs_dict
    global coresrvs_status
    coresrvs=""
    
    sysready_lock.lock()
    if coresrvs_status == "UP":
        msg = "System is ready with core services"
    else:
        msg = "System is not ready - core services are not ok"

    coresrvs+="{:30s} {:20s} {:20s} {:20s}\n".format("Service-Name","Service-Status","App-Ready-Status", "Fail-Reason")
    for srv in coresrvs_dict.keys():
        coresrvs+="{:30s} {:20s} {:20s} {:20s}\n".format(srv, coresrvs_dict[srv]['service_status'], 
                coresrvs_dict[srv]['service_up_status'],
                coresrvs_dict[srv]['fail_reason'])
    sysready_lock.unlock()

    return {"status":msg, "coresrvs":coresrvs}


def status_all(req):
    """shows the system status all"""
    global allsrvs_dict
    global allsrvs_status
    global dnsrvs_name_list
    str1=" "
    allsrvs=""
    dnsrvs_name=""
    
    sysready_lock.lock()
    if allsrvs_status == "UP":
        msg = "System is ready with all the services"
    else:
        msg = "System is not ready - one or more services are not ok"

    allsrvs+="{:30s} {:20s} {:20s} {:20s}\n".format("Service-Name","Service-Status","App-Ready-Status", "Fail-Reason")
    for srv in allsrvs_dict.keys():
        allsrvs+="{:30s} {:20s} {:20s} {:20s}\n".format(srv, allsrvs_dict[srv]['service_status'], 
                allsrvs_dict[srv]['service_up_status'],
                allsrvs_dict[srv]['fail_reason'])
    
    dnsrvs_name=str1.join(dnsrvs_name_list)
    sysready_lock.unlock()
    
    return {"status":msg, "allsrvs":allsrvs, "dnsrvs_name":dnsrvs_name}


def sysready_listen():
    SERVER_ADDRESS = '/var/run/sysready.socket'

    if os.path.exists(SERVER_ADDRESS):
        os.remove(SERVER_ADDRESS)

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(SERVER_ADDRESS)
    os.chmod(SERVER_ADDRESS, stat.S_IRWXU |stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)
    sock.listen(1)
    fail_res={"status":False, "msg":None}
    while True:
        connection, client_address = sock.accept()
        try:
            request = connection.recv(10240)
            #logger.log_info("sysready [ REQ ] {}".format(request))
            if request is None:
                continue

            req=Dict2Obj(json.loads(request.decode('utf-8')))

            response = globals()[req.command](req)
            res=json.dumps(response)
            #logger.log_info("sysready [ RES ] {}".format(res))
            connection.sendall(res.encode('utf-8'))
        except Exception as e:
            logger.log_error("sysready {}".format(str(e)))
            fail_res['msg']=str(e)
            connection.sendall(json.dumps(fail_res).encode('utf-8'))

        connection.close()

    #sock.close() #lgtm [py/unreachable-statement]


def db_connect():
    try:
        st_db = SonicV2Connector()
        st_db.connect(st_db.STATE_DB,True)
        ap_db = SonicV2Connector()
        ap_db.connect(ap_db.APPL_DB,True)
        config_db = ConfigDBConnector()
        config_db.connect()
    except Exception as e:
        logger.log_error("Error: Connection to the DB failed {}".format(str(e)))
        sys.exit(1)

    return st_db,ap_db,config_db


def system_service():

    global QUEUE
    QUEUE = mp.Queue()

    st_db,ap_db,config_db = db_connect()

    thread_service_event = threading.Thread(target=subscribe_service_event_thread, name='service', args=(QUEUE,))
    thread_service_event.start()

    thread_sysready = threading.Thread(target=sysready_listen, name='sysready', args=())
    thread_sysready.start()

    thread_statedb = threading.Thread(target=subscribe_statedb_event_thread, name='statedb', args=(QUEUE,))
    thread_statedb.start()

    event = 'SERVICE_EVENT'
    sysready_lock.lock()
    #This is run only once when sysmonitor bootsup
    check_system_status(event, st_db, ap_db, config_db)
    sysready_lock.unlock()

    # Queue to receive the STATEDB and Systemd state change event
    while True:
        event = QUEUE.get()
        #logger.log_info( "System event [ "+event+" ] is received")
        try:
            sysready_lock.lock()
            check_unit_status(event, st_db, ap_db, config_db)
            sysready_lock.unlock()
        except Exception as e:
            logger.log_error( str(e))
            time.sleep(2)


#Main method to lanch the process in background
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--daemon", action='store_true', help="Start with daemon mode")
    args = parser.parse_args()

    if args.daemon:
        try:
            pid = os.fork()
        except OSError:
            logger.log_error("Could not create a child process\n")
        #parent
        if pid != 0:
            exit()

    system_service()

