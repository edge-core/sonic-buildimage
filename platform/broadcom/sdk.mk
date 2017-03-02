BRCM_OPENNSL = libopennsl_3.2.1.5-7-20170301212550.23_amd64.deb
$(BRCM_OPENNSL)_URL = "https://sonicstorage.blob.core.windows.net/packages/libopennsl_3.2.1.5-7-20170301212550.23_amd64.deb?sv=2015-04-05&sr=b&sig=d18xevgySzJGCbD6I9M4SX1%2B291vIOMbMXPsbkDjuFA%3D&se=2030-11-08T22%3A36%3A21Z&sp=r"

BRCM_OPENNSL_KERNEL = opennsl-modules-3.16.0-4-amd64_3.2.1.5-7-20170301212550.23_amd64.deb
$(BRCM_OPENNSL_KERNEL)_URL = "https://sonicstorage.blob.core.windows.net/packages/opennsl-modules-3.16.0-4-amd64_3.2.1.5-7-20170301212550.23_amd64.deb?sv=2015-04-05&sr=b&sig=5iudeTcf3WNlNSYgJPfaj41CVh7n71GuV7v1hmuy0OI%3D&se=2030-11-08T22%3A36%3A58Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_OPENNSL) $(BRCM_OPENNSL_KERNEL)
