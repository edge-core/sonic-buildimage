#ifndef __ETH_CMD_TYPES_H__
#define __ETH_CMD_TYPES_H__

typedef enum {
    ETH_START = 1,
    ETH_SHOW,
    ETH_SET,
    ETH_TEST,
    ETH_MAC_REG,
    ETH_PHY_REG,
} ether_dbg_top_cmd_t;

typedef enum {
    ETH_MAC_REG_READ = 1,
    ETH_MAC_REG_WRITE,
    ETH_MAC_REG_CHECK,
    ETH_MAC_REG_DUMP_ALL,
    ETH_MAC_REG_DUMP_PCI_CFG_ALL,
} ether_mac_reg_cmd_t;


#define ETH_DBG_TYPE(cmd1, cmd2, cmd3, cmd4) \
    ((cmd1) | ((cmd2) << 8) | ((cmd3) << 16) | ((cmd4) << 24))
#define ETH_DBG_PARSE_TYPE(type, cmd1, cmd2, cmd3, cmd4) \
    do {\
        (cmd1) = (type) & 0xff;\
        (cmd2) = ((type) >> 8) & 0xff;\
        (cmd3) = ((type) >> 16) & 0xff;\
        (cmd4) = ((type) >> 24) & 0xff;\
    } while (0)

typedef struct {
    int type;
    int length;
    unsigned char value[128];
} ether_msg_t;


#endif /* __ETH_CMD_TYPES_H__ */
