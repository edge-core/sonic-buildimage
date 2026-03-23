DEVICE_DATA = {
    # Threshold definitions:
    # The `thresholds` is a list of lists.
    #   - Each element in the outer list corresponds to a sensor (by index).
    #   - Each inner list contains threshold pairs for different cooling levels.
    #     There are five threshold pairs per sensor. Each threshold pair is a string
    #     containing two values separated by a colon. The first value represents
    #     the low threshold, and the second represents the high threshold.
    #     When any sensor exceeds its high threshold, the cooling level for that
    #     sensor is increased. When the temperature falls below the low threshold,
    #     the cooling level for that sensor is decreased. Based on this logic,
    #     the cooling level for each sensor can range from 0 to 5.
    #
    # Notes:
    #   - The index order of `thresholds` must align with the sensor instances
    #     defined in `thermal.py`.
    #   - A threshold value of 'NA' indicates that the sensor is non-recoverable.
    #   - Updated threshold pairs for `PCB Top Front` and `PCB Bottom Front`
    #     ensure that cooling level index 0 corresponds to room temperature,
    #     equivalent to 38% fan speed (RPM).
    'thresholds': [
        ["00:00", "00:00", "00:00", "65:70", "NA:80"],     #  0: PCB VDD_Core
        ["19:31", "37:48", "45:53", "56:59", "NA:64"],     #  1: PCB FP Hotspot
        ["15:24", "25:32", "34:40", "45:48", "NA:53"],     #  2: PCB Top Front
        ["15:25", "28:37", "36:43", "48:51", "NA:56"],     #  3: PCB Bottom Front
        ["00:00", "00:00", "00:00", "65:70", "NA:80"],     #  4: PCB Bottom Rear
        ["00:00", "00:00", "00:00", "65:70", "NA:80"],     #  5: PCB OCXO
        ["00:00", "00:00", "00:00", "65:70", "NA:80"],     #  6: PCB ASIC
        ["00:00", "00:00", "00:00", "65:70", "NA:80"],     #  7: PCB Top Rear
        ["40:51", "54:64", "62:69", "100:108", "NA:115"],  #  8: ASIC Temp 1
        ["40:51", "54:64", "62:69", "100:108", "NA:115"],  #  9: ASIC Temp 2
        ["40:51", "54:64", "62:69", "100:108", "NA:115"],  # 10: ASIC Temp 3
        ["30:45", "48:60", "54:63", "63:66", "NA:71"]      # 11: CPU Temp
    ],
    # List of fan speeds, where each index corresponds to a cooling level index
    'fan_speed': [
        "38", "60", "80", "100", "100", "100" # RPM percentage
    ]
}

