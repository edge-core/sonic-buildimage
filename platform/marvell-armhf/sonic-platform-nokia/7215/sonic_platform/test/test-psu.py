#!/usr/bin/python

from sonic_platform.chassis import Chassis


def main():
    print("---------------------")
    print("Chassis PSU Unit Test")
    print("---------------------")

    chassis = Chassis()

    for psu in chassis.get_all_psus():
        print("    Name:", psu.get_name())
        print("        Presence: {}, Status: {}, LED: {}".format(psu.get_presence(),
                                                                 psu.get_status(),
                                                                 psu.get_status_led()))
        print("        Model: {}, Serial: {}".format(psu.get_model(),
                                                     psu.get_serial()))
        print("        Voltage: {}, Current: {}, Power: {}\n".format(psu.get_voltage(),
                                                                     psu.get_current(),
                                                                     psu.get_power()))
    return


if __name__ == '__main__':
    main()
