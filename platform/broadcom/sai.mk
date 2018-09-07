BRCM_SAI = libsaibcm_3.1.3.5-8_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/libsaibcm_3.1.3.5-8_amd64.deb?sv=2015-04-05&sr=b&sig=vM4LXDn4RIIxfK6lNL2mkEAnSPyaNgEH2QAfHSySMEg%3D&se=2155-07-31T18%3A43%3A06Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.1.3.5-8_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/libsaibcm-dev_3.1.3.5-8_amd64.deb?sv=2015-04-05&sr=b&sig=ehMedaC6GDviSVEhsCygfLS%2FG9gijkBjZT2y5WxByls%3D&se=2155-07-31T18%3A36%3A17Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
