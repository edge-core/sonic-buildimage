/*
 * Juniper PCI ID(s) - for devices on Juniper Boards
 *
 * Rajat Jain <rajatjain@juniper.net>
 * Copyright 2014 Juniper Networks
 *
 * This program is free software; you can redistribute  it and/or modify it
 * under  the terms of  the GNU General  Public License as published by the
 * Free Software Foundation;  either version 2 of the  License, or (at your
 * option) any later version.
 */

#ifndef __JNX_PCI_IDS_H__
#define __JNX_PCI_IDS_H__

#define PCI_VENDOR_ID_JUNIPER		0x1304
#define PCI_VENDOR_ID_ERICSSON		0x1519
#define PCI_VENDOR_ID_ERICSSON_AS       0x1a25

/*
 * PTX SAM FPGA, device ID as present on various Juniper boards, such as
 * - Sangria FPC
 * - Hendricks FPC
 * - Sangria 24x10GE PIC
 * - Gladiator FPC
 */
#define PCI_DEVICE_ID_JNX_SAM		0x0004

/* Juniper Broadway ASIC family */
#define PCI_DEVICE_ID_JNX_TF		0x003c
#define PCI_DEVICE_ID_JNX_TL		0x003d
#define PCI_DEVICE_ID_JNX_TQ		0x003e
#define PCI_DEVICE_ID_JNX_OTN_FRAMER	0x0055
#define PCI_DEVICE_ID_JNX_PE		0x005e
#define PCI_DEVICE_ID_JNX_PF		0x005f	/* Juniper Paradise ASIC */
#define PCI_DEVICE_ID_JNX_ZF		0x008d	/* Juniper ZF Fabric ASIC */
#define PCI_DEVICE_ID_JNX_ZX		0x008e	/* Juniper ZX ASIC */
#define PCI_DEVICE_ID_JNX_ZT		0x0090	/* Juniper ZT ASIC */
#define PCI_DEVICE_ID_JNX_BT		0x00B2	/* Juniper BT ASIC */

/* Juniper SAM FPGA - Omega SIB, Sochu SHAM, Gladiator SIB */
#define PCI_DEVICE_ID_JNX_SAM_OMEGA	0x006a

/* Juniper SAM FPGA - present on GLD FPC board */
#define PCI_DEVICE_ID_JNX_SAM_X		0x006b

/* Juniper PAM FPGA - present on PTX MLC board */
#define PCI_DEVICE_ID_JNX_PAM		0x006c
/* Juniper CBC FPGA - present on PTX1K RCB */
#define PCI_DEVICE_ID_JNX_CBC		0x006e
#define PCI_DEVICE_ID_JNX_CBC_P2	0x0079
#define PCI_DEVICE_ID_JNX_OMG_CBC	0x0083

/* Juniper Summit FPGA */
#define PCI_DEVICE_ID_JNX_SUMMIT	0x009B

/* Juniper DOON FPGA */
#define PCI_DEVICE_ID_JNX_DOON_RCB_CBC  0x0098

/* Juniper CBC FPGA in PTX-5K MTRCB */
#define PCI_DEVICE_ID_JNX_PTX5K_MTRCB_CBC	0x0071

/* Other Vendors' devices */
#define PCI_DEVICE_ID_IDT_PES12NT3_TRANS_AB	0x8058
#define PCI_DEVICE_ID_IDT_PES12NT3_TRANS_C	0x8059
#define PCI_DEVICE_ID_IDT_PES12NT3_INT_NTB_C	0x805a
#define PCI_DEVICE_ID_IDT_48H12G2		0x807a
#define PCI_DEVICE_ID_IDT_PES24NT24G2		0x808e
#define PCI_DEVICE_ID_IDT_PES16NT16G2		0x8090

#define PCI_DEVICE_ID_PLX_8614		0x8614
#define PCI_DEVICE_ID_PLX_8618		0x8618
#define PCI_DEVICE_ID_PLX_8713		0x8713
#define PCI_DEVICE_ID_PLX_8725		0x8725
#define PCI_DEVICE_ID_PLX_8749		0x8749
#define PCI_DEVICE_ID_PLX_8796		0x8796
#define PCI_DEVICE_ID_PLX_8608		0x8608

/*
 *  Juniper CBD FPGA Device ID(s)
 */
#define JNX_CBD_FPGA_DID_09B3           0x004D
#define JNX_CBD_FPGA_DID_0BA8           0x005A

/*
 * Juniper Brackla FPGA Device IDs
 * - UBAM, MBAM, PBAM, QBAM
 */
#define PCI_DEVICE_ID_JNX_UBAM		0x00A7
#define PCI_DEVICE_ID_JNX_PBAM		0x00A8
#define PCI_DEVICE_ID_JNX_MBAM		0x00A9
#define PCI_DEVICE_ID_JNX_QBAM		0x00AA

/*
 * Juniper MPC11E Supercon and WAN FPGA IDs
 */
#define PCI_DEVICE_ID_JNX_MPC11CON	0x00A1
#define PCI_DEVICE_ID_JNX_MPC11WAN	0x00C4

/*
 * Juniper Attella TMC and Supercon FPGA IDs
 */
#define PCI_DEVICE_ID_JNX_ARGUS     0x00B0
#define PCI_DEVICE_ID_JNX_ATIC      0x00C0
#define PCI_DEVICE_ID_JNX_ATMC_CHD  0x00C1
#define PCI_DEVICE_ID_JNX_ATMC_PFE  0x00C2
#define PCI_DEVICE_ID_JNX_AOHIO     0x00C3

/*
 * Juniper TMC FPGA Device IDs
 */
#define PCI_DEVICE_ID_JNX_TMC_CHD     0x007B
#define PCI_DEVICE_ID_JNX_TMC_PFE     0x007C

#define PCI_DEVICE_ID_XILINX_1588_FPGA	0x0505

/*
 * Juniper Scapa SIB/LC Supercon FPGA IDs
 */
#define PCI_DEVICE_ID_JNX_SCAPA_SIB_CTRL    0x00BA
#define PCI_DEVICE_ID_JNX_SDLC_CTRL         0x00BE
#define PCI_DEVICE_ID_JNX_LLC_CTRL          0x00C8

/*
 * Deanston WANIO FPGA
 */
#define PCI_DEVICE_ID_JNX_DEANSTON_WAN     0x00C6

/*
 * Juniper Ardbeg Supercon FPGA IDs
 */
#define PCI_DEVICE_ID_JNX_ARDBEG_CTRL      0x00C5

/*
 * Ericsson CCM FPGA ID used in Bolan (ACX753)
 */
#define PCI_DEVICE_ID_ERIC_CCM_FPGA	    0x0020

/*
 * Ericsson OAM FPGA ID used in Bolan (ACX753)
 */
#define PCI_DEVICE_ID_ERIC_OAM_FPGA        0x7021

#endif /* __JNX_PCI_IDS_H__ */
