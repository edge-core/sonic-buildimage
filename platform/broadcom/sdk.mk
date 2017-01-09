BRCM_OPENNSL = libopennsl_3.2.1.5-1_amd64.deb
$(BRCM_OPENNSL)_URL = "https://sonicstorage.blob.core.windows.net/packages/libopennsl_3.2.1.5-1_amd64.deb?sv=2015-04-05&sr=b&sig=9Mhm4cuju4P7TmVApXihECo1fHLbANWNWTKYLnHcrOk%3D&se=2030-09-18T19%3A19%3A46Z&sp=r"

BRCM_OPENNSL_KERNEL = opennsl-modules-3.16.0-4-amd64_3.2.1.5-1_amd64.deb
$(BRCM_OPENNSL_KERNEL)_URL = "https://sonicstorage.blob.core.windows.net/packages/opennsl-modules-3.16.0-4-amd64_3.2.1.5-1_amd64.deb?sv=2015-04-05&sr=b&sig=iakUQ4CdHYbKc9ikiNNVrrLe0K8cMrez5vex7L%2BWD2o%3D&se=2030-09-18T19%3A20%3A14Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_OPENNSL) $(BRCM_OPENNSL_KERNEL)
