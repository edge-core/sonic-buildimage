#!/usr/bin/env python
# Script to stop and start the respective platforms default services. 
# This will be used while switching the pddf->non-pddf mode and vice versa
import subprocess

def check_pddf_support():
    return True

def stop_platform_svc():
    
    status, output = subprocess.getstatusoutput("systemctl stop as9716-32d-platform-monitor-fan.service")
    if status:
        print("Stop as9716-32d-platform-fan.service failed %d"%status)
        return False
    
    status, output = subprocess.getstatusoutput("systemctl stop as9716-32d-platform-monitor-psu.service")
    if status:
        print("Stop as9716-32d-platform-psu.service failed %d"%status)
        return False
    
    status, output = subprocess.getstatusoutput("systemctl stop as9716-32d-platform-monitor.service")
    if status:
        print("Stop as9716-32d-platform-init.service failed %d"%status)
        return False
    status, output = subprocess.getstatusoutput("systemctl disable as9716-32d-platform-monitor.service")
    if status:
        print("Disable as9716-32d-platform-monitor.service failed %d"%status)
        return False
    
    status, output = subprocess.getstatusoutput("/usr/local/bin/accton_as9716_32d_util.py clean")
    if status:
        print("accton_as9716_32d_util.py clean command failed %d"%status)
        return False

    # HACK , stop the pddf-platform-init service if it is active
    status, output = subprocess.getstatusoutput("systemctl stop pddf-platform-init.service")
    if status:
        print("Stop pddf-platform-init.service along with other platform serives failed %d"%status)
        return False

    return True
    
def start_platform_svc():
    status, output = subprocess.getstatusoutput("/usr/local/bin/accton_as9716_32d_util.py install")
    if status:
        print("accton_as9716_32d_util.py install command failed %d"%status)
        return False

    status, output = subprocess.getstatusoutput("systemctl enable as9716-32d-platform-monitor.service")
    if status:
        print("Enable as9716-32d-platform-monitor.service failed %d"%status)
        return False
    status, output = subprocess.getstatusoutput("systemctl start as9716-32d-platform-monitor-fan.service")
    if status:
        print("Start as9716-32d-platform-monitor-fan.service failed %d"%status)
        return False
        
    status, output = subprocess.getstatusoutput("systemctl start as9716-32d-platform-monitor-psu.service")
    if status:
        print("Start as9716-32d-platform-monitor-psu.service failed %d"%status)
        return False

    return True

def start_platform_pddf():   

    status, output = subprocess.getstatusoutput("systemctl start pddf-platform-init.service")
    if status:
        print("Start pddf-platform-init.service failed %d"%status)
        return False
    
    return True

def stop_platform_pddf():   

    status, output = subprocess.getstatusoutput("systemctl stop pddf-platform-init.service")
    if status:
        print("Stop pddf-platform-init.service failed %d"%status)
        return False

    return True

