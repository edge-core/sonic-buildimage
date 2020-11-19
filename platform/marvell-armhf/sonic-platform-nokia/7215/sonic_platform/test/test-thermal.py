#!/usr/bin/python

from sonic_platform.chassis import Chassis


def main():
    print("-------------------------")
    print("Chassis Thermal Unit Test")
    print("-------------------------")

    chassis = Chassis()

    for thermal in chassis.get_all_thermals():
        print("    Name:", thermal.get_name())
        print("        Presence: {}, Status: {}".format(thermal.get_presence(),
                                                        thermal.get_status()))
        print("        Model: {}, Serial: {}".format(thermal.get_model(),
                                                     thermal.get_serial()))
        print("        Temperature: {}C, Low Threshold: {}C, High Threshold: {}C\n".format(thermal.get_temperature(),
                                                                                           thermal.get_low_threshold(),
                                                                                           thermal.get_high_threshold()))
    return


if __name__ == '__main__':
    main()
