# sonic broadcom one image installer

SONIC_ONE_IMAGE = sonic-broadcom.bin
$(SONIC_ONE_IMAGE)_MACHINE = broadcom
$(SONIC_ONE_IMAGE)_IMAGE_TYPE = onie
$(SONIC_ONE_IMAGE)_DEPENDS += $(BRCM_OPENNSL_KERNEL)
$(SONIC_ONE_IMAGE)_INSTALLS += $(DELL_S6000_PLATFORM_MODULE) \
                               $(DELL_Z9100_PLATFORM_MODULE) \
                               $(DELL_S6100_PLATFORM_MODULE) \
                               $(INGRASYS_S8900_54XC_PLATFORM_MODULE) \
                               $(INGRASYS_S8900_64XC_PLATFORM_MODULE) \
                               $(INGRASYS_S9100_PLATFORM_MODULE) \
                               $(ACCTON_AS7712_32X_PLATFORM_MODULE)
$(SONIC_ONE_IMAGE)_DOCKERS += $(SONIC_INSTALL_DOCKER_IMAGES)
SONIC_INSTALLERS += $(SONIC_ONE_IMAGE)
