"""
This module defines all of the syslog messages to be printed by i2c health daemon
"""

# NOTE: msg index 0 is reserved for the internal error when the given index is illegal
i2c_health_msg_list = [
    "[I2CHEALTH-000] Internal Error: invalid msg id:{}.", # 000: reserved for i2c_health_msgs.py internal error. Example: "[I2CHEALTH-000] Internal Error: invalid msg id:0."
    "I2c bus lock is detected.", # 001(ERROR)
    "I2c bus lock is recovered.", # 002(NOTICE)
    "Isolate i2c device: {} ({}:{}).", # 003(NOTICE): device name, region id, device addr. Example: "[I2CHEALTH-003] Isolate i2c devices: Ethernet1(77-2-72-1:25-0050)."
    "Remove {}({}:{}) from the isolation list.", # 004(NOTICE): device name, region id, device addr. Example: "Remove Ethernet1(77-2-72-1:25-0050) from the isolation list."
    "Reset all i2c mux devices to recover i2c bus lock.", # 005(NOTICE)
    "Set all of the fans to full speed.", # 006(NOTICE)
    "Stop all i2c daemons.", # 007(NOTICE)
    "Start scanning for i2c faulty devices.", # 008(NOTICE)
    "Finish scanning for i2c faulty devices.The isolation list is updated.", # 009(NOTICE)
    "Resume all i2c daemons.", # 010(NOTICE)
    "Fatal error! Fail to stop all i2c daemons.", # 011(ERROR)
    "Fatal error! Fail to reset all i2c mux devices.", # 012(ERROR)
    "Fatal error! Fail to set all of the fans to full speed.", # 013(ERROR)
    "Init representative devices list error.", # 014(WARNING)
    "Detect i2c bus health with I2C cmd '{}'.", # 015(INFO): i2c cmd. Example "Detect i2c bus health with I2C cmd 'sudo i2cget -f -y 0 0x77 0x0'."
    "{}: i2c get successfully on attempt {}/{}.", # 016(DEBUG): device name, attempt number, max retry count. Example "EEPROM: i2c get successfully on attempt 1/3."
    "{}: i2c get failed on attempt {}/{}.", # 017(NOTICE): device name, attempt number, max retry count. Example "EEPROM: i2c get failed on attempt 1/3."
    "{}: an internal error occurs on attempt {}/{}.", # 018(WARNING): device name, attempt number, max retry count. Example "EEPROM: an internal error occurs on attempt 1/3."
    "Execute cmd to stop i2c daemon: '{}'.", # 019(NOTICE): i2c daemon service. Example "Execute cmd to stop i2c daemon: 'sudo systemctl stop as9716-32d-platform-monitor-fan.service'."
    "Failed to execute cmd to stop i2c daemon: '{}'.", # 020(ERROR): i2c daemon service. Example "Failed to execute cmd to stop i2c daemon: 'sudo systemctl stop as9716-32d-platform-monitor-fan.service'."
    "Execute cmd to start i2c daemon: '{}'.", # 021(NOTICE): i2c daemon service. Example "Execute cmd to start i2c daemon: 'sudo systemctl start as9716-32d-platform-monitor-fan.service'."
    "Failed to execute cmd to start i2c daemon: '{}'.", # 022(ERROR): i2c daemon service. Example "Failed to execute cmd to start i2c daemon: 'sudo systemctl start as9716-32d-platform-monitor-fan.service'."
    "Failed to add {}({}:{}) into the isolation list.", # 023(ERROR): device name, region id, device addr. Example: "Failed to add Ethernet1(77-2-72-1:25-0050) into the isolation list."
    "Failed to remove {}({}:{}) into the isolation list.", # 024(ERROR): device name, region id, device addr. Example: "Failed to remove Ethernet1(77-2-72-1:25-0050) into the isolation list."
    "Abnormal condition in handling cached_data during the STATE DB restore operation. ", # 025(WARNING)
    "These devices are unfinished during the restoration: {}.", # 025(NOTICE): Uncleared cached device names, Example: "These devices are unfinished during the restoration: ['Ethernet24', 'Ethernet144', 'Ethernet64, ...]."
]

def get_i2c_health_msg(msg_idx):
    """
    input arg:
        msg_idx: 1-based message index
    returns:
        message string of the given msg_idx.
    """
    if isinstance(msg_idx, int) and (msg_idx > 0 and msg_idx < len(i2c_health_msg_list)):
        msg_str = f"[I2CHEALTH-{msg_idx:03d}] " + i2c_health_msg_list[msg_idx]
    else:
        msg_str = i2c_health_msg_list[0].format(msg_idx)

    return msg_str
