BRCM_OPENNSL = libopennsl_3.2.2.2-2-20170413185612.27_amd64.deb
$(BRCM_OPENNSL)_URL = "https://sonicstorage.blob.core.windows.net/packages/libopennsl_3.2.2.2-2-20170413185612.27_amd64.deb?sv=2015-04-05&sr=b&sig=xEbASK6Jiug8I%2BaJFphRnuH4cOEgxIyAkhj6rGKfsOE%3D&se=2030-12-21T22%3A05%3A31Z&sp=r"

BRCM_OPENNSL_KERNEL = opennsl-modules-3.16.0-4-amd64_3.2.2.2-2-20170413185612.27_amd64.deb
$(BRCM_OPENNSL_KERNEL)_URL = "https://sonicstorage.blob.core.windows.net/packages/opennsl-modules-3.16.0-4-amd64_3.2.2.2-2-20170413185612.27_amd64.deb?sv=2015-04-05&sr=b&sig=i%2F4NXu0wzMSAQjDcQTg%2FtpULn5%2Fn%2FVgLu3Lg24QMQM0%3D&se=2030-12-21T22%3A06%3A49Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_OPENNSL) $(BRCM_OPENNSL_KERNEL)
