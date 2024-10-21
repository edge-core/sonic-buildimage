"""
This module defines all of the syslog messages to be printed by i2c health daemon
"""

# NOTE: msg index 0 is reserved for the internal error when the given index is illegal
i2c_health_msg_list = [
    "[I2CHEALTH-000] Internal Error: invalid msg id:{}", # 000: reserved for i2c_health_msgs.py internal error. Example: "[I2CHEALTH-000] Internal Error: invalid msg id:0"
    "I2c bus lock is detected.", # 001
    "I2c bus lock is recovered.", # 002
    "Isolate i2c device: {} ({}:{})", # 003: device name, region id, device addr. Example: "[I2CHEALTH-003] Isolate i2c devices: Ethernet1(77-2-72-1:25-0050)."
    "Remove {}({}:{}) from the isolation list.", # 004: device name, region id, device addr. Example: "Remove Ethernet1(77-2-72-1:25-0050) from the isolation list."
    "Reset all i2x mux devices to recover i2c bus lock.", # 005
    "Set all of the fans to full speed.", # 006
    "Stop all i2c daemons.", # 007
    "Start scanning for i2c faulty devices.", # 008
    "Finish scanning for i2c faulty devices.The isolation list is updated.", # 009
    "Resume all i2c daemons.", # 010
    "Fatal error! Fail to stop all i2c daemons.", # 011
    "Fatal error! Fail to reset all i2c mux devices.", #012
    "Fatal error! Fail to set all of the fans to full speed.", #013
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
