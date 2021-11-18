#ifndef _FPGA_PCIE_I2C_H_
#define _FPGA_PCIE_I2C_H_

#ifdef __KERNEL__
#include <linux/types.h>
#else
#include <stdint.h>
#endif

#define ENUM_MAX_DEVS   (255)

typedef enum {
    CHIP_NONE,
    CHIP_PC,
} chiptype_t;

/* bitmap for ports, 256 ports for now. */
typedef struct portbitmap_s {
    uint8_t bit[32];
} portbitmap_t;

typedef struct pc_info_s {
    uint8_t ntables;    /* number of flow tables */
    uint8_t ncores;     /* number of cores */
    uint8_t npipelines; /* number of pipelines */
    uint8_t nports;     /* number of ports */
    portbitmap_t pbm_caui;  /* bitmap for CAUI ports */
    portbitmap_t pbm_ge;    /* bitmap for GE ports */
} pc_info_t;

/**
 * A structure describing a PCI resource.
 */
struct pci_resource {
    uint64_t phys_addr;   /**< Physical address, 0 if no resource. */
    uint64_t len;         /**< Length of the resource. */
    void *addr;           /**< Virtual address, NULL when not mapped. */
};

/** Maximum number of PCI resources. */
#define PCI_MAX_RESOURCE 6

/** Nb. of values in PCI resource format. */
#define PCI_RESOURCE_FMT_NVAL 3

#if 0
/** IO resource type: memory address space */
#define IORESOURCE_MEM        0x00000200
#endif

typedef struct chipinfo_s {
    /* PCI ID */
    uint16_t vendor;
    uint16_t dev;
    uint8_t rev;

    /* chip properties */
    chiptype_t type;
    pc_info_t pc_info;  /* if type == CHIP_PC */
} chipinfo_t;

typedef struct devinfo_s {
    /* static info */
    chipinfo_t  chipinfo;

    /* running states */
    uint32_t uiono; /* the "X" in /dev/uioX */
    char *pci_conf_file;    /* /sys/devices/ */
    char *dev_file; /* /dev/uioX */

    struct pci_resource mem_resource[PCI_MAX_RESOURCE];   /**< PCI Memory Resource */

    uint32_t n_mems; /* no of mem-mapped regions, MUST BE 1 for now */
    uint32_t n_ports;/* no of port-maped regions, MUST BE 0 for now  */
} devinfo_t;


#ifdef __KERNEL__
#include <linux/pci.h>

struct pci_dev *rgde_to_pci_device(int index);

int rgde_reg32_read(int minor, uint64_t offset, uint32_t *data);

int rgde_reg32_write(int minor, uint64_t offset, uint32_t data);

int pkt_get_mod(int logic_dev, int *mod);

int pkt_get_port(int logic_dev, int *port);

/* interrupt mode */
enum xdk_intr_mode {
    XDK_INTR_MODE_NONE = 0,
    XDK_INTR_MODE_LEGACY,
    XDK_INTR_MODE_MSI,
    XDK_INTR_MODE_MSIX
};

#define INTR_MODE_NONE_NAME     "none"
#define INTR_MODE_LEGACY_NAME   "legacy"
#define INTR_MODE_MSI_NAME      "msi"
#define INTR_MODE_MSIX_NAME     "msix"

#endif /*__KERNEL__ */


#endif /* _FPGA_PCIE_I2C_H_ */
