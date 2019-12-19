/*
 * Copyright 2017-2019 Broadcom
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License, version 2, as
 * published by the Free Software Foundation (the "GPL").
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License version 2 (GPLv2) for more details.
 *
 * You should have received a copy of the GNU General Public License
 * version 2 (GPLv2) along with this source code.
 */
/*
 * $Id: psample_cb.c $
 * $Copyright: (c) 2019 Broadcom Corp.
 * All Rights Reserved.$
 */

/*
 * Driver for call-back functions for Linux KNET driver.
 *
 * This code is used to integrate packet sampling KNET callback to 
 * the psample infra for sending sampled pkts to userspace sflow 
 * applications such as Host Sflow (https://github.com/sflow/host-sflow) 
 * using genetlink interfaces.  
 *
 * The module can be built from the standard Linux user mode target
 * directories using the following command (assuming bash), e.g.
 *
 *   cd $SDK/systems/linux/user/<target>
 *   make BUILD_KNET_CB=1
 *
 */

#include <gmodule.h> /* Must be included first */
#include <kcom.h>
#include <bcm-knet.h>
#include <linux/if_vlan.h>
#include <linux/skbuff.h>
#include <linux/sched.h>
#include <linux/netdevice.h>
#include <net/net_namespace.h>
#include <net/psample.h>
#include "psample-cb.h"

#define PSAMPLE_CB_DBG
#ifdef PSAMPLE_CB_DBG 
extern int debug;
#define PSAMPLE_CB_DBG_PRINT(...) \
    if (debug & 0x1) {         \
        gprintk(__VA_ARGS__);  \
    }
#else
#define PSAMPLE_CB_DBG_PRINT(...)
#endif

/* HIGIG2 header fields */
#define SOC_HIGIG_SOP         (0xfb)
#define SOC_HIGIG_START(x)    ((x[0] >> 24) & 0xff)
#define SOC_HIGIG_DSTPORT(x)  ((x[1] >> 11) & 0x1f)
#define SOC_HIGIG_SRCPORT(x)  ((x[1] >> 16) & 0x1f)
#define SOC_HIGIG2_SOP        (0xfb) //0xfc - TODO: how can we differentiate between Higig and higig2?
#define SOC_HIGIG2_START(x)   ((x[0] >> 24) & 0xff)
#define SOC_HIGIG2_DSTPORT(x) ((x[0] >>  0) & 0xff)
#define SOC_HIGIG2_SRCPORT(x) ((x[1] >> 16) & 0xff)
#define SOC_DCB32_HG_OFFSET   (6)

#define FCS_SZ 4
#define PSAMPLE_NLA_PADDING 4

#define PSAMPLE_RATE_DFLT 1
#define PSAMPLE_SIZE_DFLT 128
static int psample_size = PSAMPLE_SIZE_DFLT;
LKM_MOD_PARAM(psample_size, "i", int, 0);
MODULE_PARM_DESC(psample_size,
"psample pkt size (default 128 bytes)");

/* driver proc entry root */
static struct proc_dir_entry *psample_proc_root = NULL;

/* psample general info */
typedef struct {
    struct list_head netif_list;
    knet_hw_info_t hw;
    struct net *netns;
    spinlock_t lock;
} psample_info_t;
static psample_info_t g_psample_info = {{0}};

/* Maintain sampled pkt statistics */
typedef struct psample_stats_s {
    unsigned long pkts_f_psample_cb;
    unsigned long pkts_f_psample_mod;
    unsigned long pkts_f_handled;
    unsigned long pkts_f_pass_through;
    unsigned long pkts_d_no_group;
    unsigned long pkts_d_sampling_disabled;
    unsigned long pkts_d_no_skb;
    unsigned long pkts_d_not_ready;
    unsigned long pkts_d_metadata;
    unsigned long pkts_d_meta_srcport;
    unsigned long pkts_d_meta_dstport;
    unsigned long pkts_d_invalid_size;
} psample_stats_t;
static psample_stats_t g_psample_stats = {0};

typedef struct psample_meta_s {
    int trunc_size;
    int src_ifindex;
    int dst_ifindex;
    int sample_rate;
} psample_meta_t;


static psample_netif_t*
psample_netif_lookup_by_port(int unit, int port)
{
    struct list_head *list;
    psample_netif_t *psample_netif = NULL;
    unsigned long flags;

    /* look for port from list of available net_devices */
    spin_lock_irqsave(&g_psample_info.lock, flags);
    list_for_each(list, &g_psample_info.netif_list) {
        psample_netif = (psample_netif_t*)list;
        if (psample_netif->port == port) {
            spin_unlock_irqrestore(&g_psample_info.lock, flags);
            return psample_netif;
        }
    }
    spin_unlock_irqrestore(&g_psample_info.lock, flags);
    return (NULL);
}
        
static int
psample_info_get (int unit, psample_info_t *psample_info)
{
    int rv = 0;
    if (!psample_info) {
        gprintk("%s: psample_info is NULL\n", __func__);
        return (-1);
    }

    /* get hw info */
    rv = bkn_hw_info_get(unit, &psample_info->hw);
    if (rv < 0) {
        gprintk("%s: failed to get hw info\n", __func__);
        return (-1);
    }

    PSAMPLE_CB_DBG_PRINT("%s: DCB type %d\n",
            __func__, psample_info->hw.dcb_type);
    return (0);
}

static int
psample_meta_srcport_get(uint8_t *pkt, void *pkt_meta)
{
    int srcport = 0;
    uint32_t *metadata = (uint32_t*)pkt_meta;

    switch(g_psample_info.hw.dcb_type) {
        case 36: /* TD3 */
        case 38: /* TH3 */
            break;
        case 32: /* TH1/TH2 */
        case 26: /* TD2 */
        case 23: /* HX4 */
            metadata += SOC_DCB32_HG_OFFSET;
            break;
        default:
            break;
    }

    if (SOC_HIGIG2_START(metadata) == SOC_HIGIG2_SOP) 
    {
        srcport = SOC_HIGIG2_SRCPORT(metadata);
    } 
    else if (SOC_HIGIG_START(metadata) == SOC_HIGIG_SOP) 
    {
        srcport = SOC_HIGIG_SRCPORT(metadata);
    } 
    else 
    {
        PSAMPLE_CB_DBG_PRINT("%s: Could not detect metadata sop type: 0x%02x (w[0]: 0x%04x)\n", __func__, 
                SOC_HIGIG_START(metadata), metadata[0]);
        return -1;
    }
    return srcport;
}

static int
psample_meta_dstport_get(uint8_t *pkt, void *pkt_meta)
{
    int dstport = 0;
    uint32_t *metadata = (uint32_t*)pkt_meta;

    switch(g_psample_info.hw.dcb_type) {
        case 36: /* TD3 */
        case 38: /* TH3 */
            break;
        case 32: /* TH1/TH2 */
        case 26: /* TD2 */
        case 23: /* HX4 */
            metadata += SOC_DCB32_HG_OFFSET;
            break;
        default:
            break;
    }
    
    if (SOC_HIGIG2_START(metadata) == SOC_HIGIG2_SOP) 
    {
        dstport = SOC_HIGIG2_DSTPORT(metadata);
    } 
    else if (SOC_HIGIG_START(metadata) == SOC_HIGIG_SOP) 
    {
        dstport = SOC_HIGIG_DSTPORT(metadata);
    } 
    else 
    {
        PSAMPLE_CB_DBG_PRINT("%s: Could not detect metadata sop type: 0x%02x (w[0]: 0x%04x)\n", __func__, 
                SOC_HIGIG_START(metadata), metadata[0]);
        return (-1);
    }
    return dstport;
}

static int
psample_meta_sample_reason(uint8_t *pkt, void *pkt_meta)
{
    uint32_t *metadata = (uint32_t*)pkt_meta;
    uint32_t reason = 0;
    uint32_t reason_hi = 0;
    uint32_t sample_rx_reason_mask = 0;

    /* Sample Pkt reason code (bcmRxReasonSampleSource) */
    switch(g_psample_info.hw.dcb_type) {
        case 36: /* TD3 */
        case 38: /* TH3 */
            reason_hi = *(metadata + 4);
            reason    = *(metadata + 5);
            sample_rx_reason_mask = (1 << 3);
            break;
        case 32: /* TH1/TH2 */
        case 26: /* TD2 */
        case 23: /* HX4 */
        default:
            reason_hi = *(metadata + 2);
            reason    = *(metadata + 3);
            sample_rx_reason_mask = (1 << 5);
            break;
    }
        
    PSAMPLE_CB_DBG_PRINT("%s: DCB%d sample_rx_reason_mask: 0x%08x, reason: 0x%08x, reason_hi: 0x%08x\n", 
            __func__, g_psample_info.hw.dcb_type, sample_rx_reason_mask, reason, reason_hi);

    /* Check if only sample reason code is set.
     * If only sample reason code, then consume pkt.
     * If other reason codes exist, then pkt should be 
     * passed through to Linux network stack.
     */
    if ((reason & ~sample_rx_reason_mask) || reason_hi) {
        return 0; /* multiple reasons set, pass through */
    }

    /* only sample rx reason set, consume pkt */
    return (1);
}

static int
psample_meta_get(int unit, uint8_t *pkt, void *pkt_meta, psample_meta_t *sflow_meta)
{
    int srcport, dstport;
    int src_ifindex = 0;
    int dst_ifindex = 0;
    int sample_rate = PSAMPLE_RATE_DFLT;
    int sample_size = PSAMPLE_SIZE_DFLT;
    psample_netif_t *psample_netif = NULL;

#ifdef PSAMPLE_CB_DBG
    if (debug & 0x1) {
        int i=0;
        uint8_t *meta = (uint8_t*)pkt_meta;
        PSAMPLE_CB_DBG_PRINT("%s: psample pkt metadata\n", __func__);
        for (i=0; i<64; i+=16) {
            PSAMPLE_CB_DBG_PRINT("%02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x\n", 
                    meta[i+0], meta[i+1], meta[i+2], meta[i+3], meta[i+4], meta[i+5], meta[i+6], meta[i+7],
                    meta[i+8], meta[i+9], meta[i+10], meta[i+11], meta[i+12], meta[i+13], meta[i+14], meta[i+15]);
        }
    }
#endif

    /* parse pkt metadata for src and dst ports */
    srcport = psample_meta_srcport_get(pkt, pkt_meta);
    dstport = psample_meta_dstport_get(pkt, pkt_meta);
    if ((srcport == -1) || (dstport == -1)) {
        gprintk("%s: invalid srcport %d or dstport %d\n", __func__, srcport, dstport);
        return (-1);
    }

    /* find src port netif (no need to lookup CPU port) */
    if (srcport != 0) {
        if ((psample_netif = psample_netif_lookup_by_port(unit, srcport))) {
            src_ifindex = psample_netif->dev->ifindex;
            sample_rate = psample_netif->sample_rate;
            sample_size = psample_netif->sample_size;
        } else {
            g_psample_stats.pkts_d_meta_srcport++;
            PSAMPLE_CB_DBG_PRINT("%s: could not find srcport(%d)\n", __func__, srcport);
        }
    }

    /* find dst port netif (no need to lookup CPU port) */
    if (dstport != 0) {
        if ((psample_netif = psample_netif_lookup_by_port(unit, dstport))) {
            dst_ifindex = psample_netif->dev->ifindex;
        } else {
            g_psample_stats.pkts_d_meta_dstport++;
            PSAMPLE_CB_DBG_PRINT("%s: could not find dstport(%d)\n", __func__, dstport);
        }
    }

    PSAMPLE_CB_DBG_PRINT("%s: srcport %d, dstport %d, src_ifindex %d, dst_ifindex %d, trunc_size %d, sample_rate %d\n", 
            __func__, srcport, dstport, src_ifindex, dst_ifindex, sample_size, sample_rate);

    sflow_meta->src_ifindex = src_ifindex;
    sflow_meta->dst_ifindex = dst_ifindex;
    sflow_meta->trunc_size  = sample_size;
    sflow_meta->sample_rate = sample_rate;

    return (0);
}

int 
psample_filter_cb(uint8_t * pkt, int size, int dev_no, void *pkt_meta,
                  int chan, kcom_filter_t *kf)
{
    struct psample_group *group;
    psample_meta_t meta;   
    struct sk_buff skb;
    int rv = 0;
    static int info_get = 0;

    if (!info_get) {
        rv = psample_info_get (dev_no, &g_psample_info);
        if (rv < 0) {
            gprintk("%s: failed to get psample info\n", __func__);
            goto PSAMPLE_FILTER_CB_PKT_HANDLED;
        }
        info_get = 1;
    }

    PSAMPLE_CB_DBG_PRINT("%s: pkt size %d, kf->dest_id %d, kf->cb_user_data %d\n",
            __func__, size, kf->dest_id, kf->cb_user_data);
    g_psample_stats.pkts_f_psample_cb++;

    /* get psample group info. psample genetlink group ID passed in kf->dest_id */
    group = psample_group_get(g_psample_info.netns, kf->dest_id);
    if (!group) {
        gprintk("%s: Could not find psample genetlink group %d\n", __func__, kf->cb_user_data);
        g_psample_stats.pkts_d_no_group++;
        goto PSAMPLE_FILTER_CB_PKT_HANDLED;
    }

    /* get psample metadata */
    rv = psample_meta_get(dev_no, pkt, pkt_meta, &meta);
    if (rv < 0) {
        gprintk("%s: Could not parse pkt metadata\n", __func__);
        g_psample_stats.pkts_d_metadata++;
        goto PSAMPLE_FILTER_CB_PKT_HANDLED;
    }

    /* Adjust original pkt size to remove 4B FCS */
    if (size < FCS_SZ) {
        g_psample_stats.pkts_d_invalid_size++;
        goto PSAMPLE_FILTER_CB_PKT_HANDLED;
    } else {
       size -= FCS_SZ; 
    }

    /* Account for padding in libnl used by psample */
    if (meta.trunc_size >= size) {
        meta.trunc_size = size - PSAMPLE_NLA_PADDING;
    }

    PSAMPLE_CB_DBG_PRINT("%s: group 0x%x, trunc_size %d, src_ifdx %d, dst_ifdx %d, sample_rate %d\n",
            __func__, group->group_num, meta.trunc_size, meta.src_ifindex, meta.dst_ifindex, meta.sample_rate);

    /* drop if configured sample rate is 0 */
    if (meta.sample_rate > 0) {
        /* setup skb to point to pkt */
        memset(&skb, 0, sizeof(struct sk_buff));
        skb.len = size;
        skb.data = pkt;

        psample_sample_packet(group, 
                              &skb, 
                              meta.trunc_size,
                              meta.src_ifindex,
                              meta.dst_ifindex,
                              meta.sample_rate);

        g_psample_stats.pkts_f_psample_mod++;
    } else {
        g_psample_stats.pkts_d_sampling_disabled++;
    }    

PSAMPLE_FILTER_CB_PKT_HANDLED:
    /* if sample reason only, consume pkt. else pass through */
    rv = psample_meta_sample_reason(pkt, pkt_meta);
    if (rv) {
        g_psample_stats.pkts_f_handled++;
    } else {
        g_psample_stats.pkts_f_pass_through++;
    }
    return rv;
}

int 
psample_netif_create_cb(int unit, kcom_netif_t *netif, struct net_device *dev)
{
    int found;
    struct list_head *list;
    psample_netif_t *psample_netif, *lpsample_netif;
    unsigned long flags;

    if ((psample_netif = kmalloc(sizeof(psample_netif_t), GFP_KERNEL)) == NULL) {
        gprintk("%s: failed to alloc psample mem for netif '%s'\n", 
                __func__, dev->name);
        return (-1);
    }

    spin_lock_irqsave(&g_psample_info.lock, flags);

    psample_netif->dev = dev;
    psample_netif->id = netif->id;
    psample_netif->port = netif->port;
    psample_netif->vlan = netif->vlan;
    psample_netif->qnum = netif->qnum;
    psample_netif->sample_rate = PSAMPLE_RATE_DFLT;
    psample_netif->sample_size = PSAMPLE_SIZE_DFLT;

    /* insert netif sorted by ID similar to bkn_knet_netif_create() */
    found = 0;
    list_for_each(list, &g_psample_info.netif_list) {
        lpsample_netif = (psample_netif_t*)list;
        if (netif->id < lpsample_netif->id) {
            found = 1;
            break;
        }
    }

    if (found) {
        /* Replace previously removed interface */
        list_add_tail(&psample_netif->list, &lpsample_netif->list);
    } else {
        /* No holes - add to end of list */
        list_add_tail(&psample_netif->list, &g_psample_info.netif_list);
    }
    
    spin_unlock_irqrestore(&g_psample_info.lock, flags);

    PSAMPLE_CB_DBG_PRINT("%s: added psample netif '%s'\n", __func__, dev->name);
    return (0);
}

int
psample_netif_destroy_cb(int unit, kcom_netif_t *netif, struct net_device *dev)
{
    int found;
    struct list_head *list;
    psample_netif_t *psample_netif;
    unsigned long flags; 

    if (!netif || !dev) {
        gprintk("%s: netif or net_device is NULL\n", __func__);
        return (-1);
    }

    spin_lock_irqsave(&g_psample_info.lock, flags);
    
    list_for_each(list, &g_psample_info.netif_list) {
        psample_netif = (psample_netif_t*)list;
        if (netif->id == psample_netif->id) {
            found = 1; 
            list_del(&psample_netif->list);
            PSAMPLE_CB_DBG_PRINT("%s: removing psample netif '%s'\n", __func__, dev->name);
            kfree(psample_netif);
            break;
        }
    }

    spin_unlock_irqrestore(&g_psample_info.lock, flags);
    
    if (!found) {    
        gprintk("%s: netif ID %d not found!\n", __func__, netif->id);
        return (-1);
    }
    return (0);
}

/*
 * psample rate Proc Read Entry
 */
static int
psample_proc_rate_show(struct seq_file *m, void *v)
{
    struct list_head *list;
    psample_netif_t *psample_netif;
    unsigned long flags; 

    spin_lock_irqsave(&g_psample_info.lock, flags);
    
    list_for_each(list, &g_psample_info.netif_list) {
        psample_netif = (psample_netif_t*)list;
        seq_printf(m, "  %-14s %d\n", psample_netif->dev->name, psample_netif->sample_rate);
    }

    spin_unlock_irqrestore(&g_psample_info.lock, flags);
 
    return 0;
}

static int
psample_proc_rate_open(struct inode * inode, struct file * file)
{
    return single_open(file, psample_proc_rate_show, NULL);
}

/*
 * psample rate Proc Write Entry
 *
 *   Syntax:
 *   <netif>=<pkt sample rate>
 *
 *   Where <netif> is a virtual network interface name.
 *
 *   Examples:
 *   eth4=1000
 */
static ssize_t
psample_proc_rate_write(struct file *file, const char *buf,
                    size_t count, loff_t *loff)
{
    int found;
    struct list_head *list;
    psample_netif_t *psample_netif;
    char sample_str[40], *ptr, *newline;
    unsigned long flags;


    if (count > sizeof(sample_str)) {
        count = sizeof(sample_str) - 1;
        sample_str[count] = '\0';
    }
    if (copy_from_user(sample_str, buf, count)) {
        return -EFAULT;
    }
    sample_str[count] = 0;
    newline = strchr(sample_str, '\n');
    if (newline) {
        /* Chop off the trailing newline */
        *newline = '\0';
    }

    if ((ptr = strchr(sample_str, '=')) == NULL &&
        (ptr = strchr(sample_str, ':')) == NULL) {
        gprintk("Error: Pkt sample rate syntax not recognized: '%s'\n", sample_str);
        return count;
    }
    *ptr++ = 0;

    spin_lock_irqsave(&g_psample_info.lock, flags);
   
    found = 0; 
    list_for_each(list, &g_psample_info.netif_list) {
        psample_netif = (psample_netif_t*)list;
        if (strcmp(psample_netif->dev->name, sample_str) == 0) {
            psample_netif->sample_rate = simple_strtol(ptr, NULL, 10);
            // TODO MLI@BRCM - check valid sample rate
            found = 1; 
            break;
        }
    }
    
    spin_unlock_irqrestore(&g_psample_info.lock, flags);

    if (!found) {
        gprintk("Warning: Failed setting psample rate on unknown network interface: '%s'\n", sample_str);
    }
    return count;
}

struct file_operations psample_proc_rate_file_ops = {
    owner:      THIS_MODULE,
    open:       psample_proc_rate_open,
    read:       seq_read,
    llseek:     seq_lseek,
    write:      psample_proc_rate_write,
    release:    single_release,
};

/*
 * psample size Proc Read Entry
 */
static int
psample_proc_size_show(struct seq_file *m, void *v)
{
    struct list_head *list;
    psample_netif_t *psample_netif;
    unsigned long flags;

    spin_lock_irqsave(&g_psample_info.lock, flags);
    
    list_for_each(list, &g_psample_info.netif_list) {
        psample_netif = (psample_netif_t*)list;
        seq_printf(m, "  %-14s %d\n", psample_netif->dev->name, psample_netif->sample_size);
    }

    spin_unlock_irqrestore(&g_psample_info.lock, flags);
    return 0;
}

static int
psample_proc_size_open(struct inode * inode, struct file * file)
{
    return single_open(file, psample_proc_size_show, NULL);
}

/*
 * psample size Proc Write Entry
 *
 *   Syntax:
 *   <netif>=<pkt sample size in bytes>
 *
 *   Where <netif> is a virtual network interface name.
 *
 *   Examples:
 *   eth4=128
 */
static ssize_t
psample_proc_size_write(struct file *file, const char *buf,
                    size_t count, loff_t *loff)
{
    int found;
    struct list_head *list;
    psample_netif_t *psample_netif;
    char sample_str[40], *ptr, *newline;
    unsigned long flags;

    if (count > sizeof(sample_str)) {
        count = sizeof(sample_str) - 1;
        sample_str[count] = '\0';
    }
    if (copy_from_user(sample_str, buf, count)) {
        return -EFAULT;
    }
    sample_str[count] = 0;
    newline = strchr(sample_str, '\n');
    if (newline) {
        /* Chop off the trailing newline */
        *newline = '\0';
    }

    if ((ptr = strchr(sample_str, '=')) == NULL &&
        (ptr = strchr(sample_str, ':')) == NULL) {
        gprintk("Error: Pkt sample size syntax not recognized: '%s'\n", sample_str);
        return count;
    }
    *ptr++ = 0;

    spin_lock_irqsave(&g_psample_info.lock, flags);
   
    found = 0; 
    list_for_each(list, &g_psample_info.netif_list) {
        psample_netif = (psample_netif_t*)list;
        if (strcmp(psample_netif->dev->name, sample_str) == 0) {
            psample_netif->sample_size = simple_strtol(ptr, NULL, 10);
            // TODO MLI@BRCM - check valid sample size
            found = 1;
            break; 
        }
    }
    
    spin_unlock_irqrestore(&g_psample_info.lock, flags);

    if (!found) {
        gprintk("Warning: Failed setting psample size on unknown network interface: '%s'\n", sample_str);
    }
    return count;
}

struct file_operations psample_proc_size_file_ops = {
    owner:      THIS_MODULE,
    open:       psample_proc_size_open,
    read:       seq_read,
    llseek:     seq_lseek,
    write:      psample_proc_size_write,
    release:    single_release,
};

/*
 * psample debug Proc Read Entry
 */
static int
psample_proc_debug_show(struct seq_file *m, void *v)
{
    seq_printf(m, "BCM KNET %s Callback Config\n", PSAMPLE_CB_NAME);
    seq_printf(m, "  debug:           0x%x\n", debug);
    seq_printf(m, "  cmic_type:       %d\n",   g_psample_info.hw.cmic_type);
    seq_printf(m, "  dcb_type:        %d\n",   g_psample_info.hw.dcb_type);
    seq_printf(m, "  dcb_size:        %d\n",   g_psample_info.hw.dcb_size);
    seq_printf(m, "  pkt_hdr_size:    %d\n",   g_psample_info.hw.pkt_hdr_size);
    seq_printf(m, "  cdma_channels:   %d\n",   g_psample_info.hw.cdma_channels);

    return 0;
}

static int
psample_proc_debug_open(struct inode * inode, struct file * file)
{
    return single_open(file, psample_proc_debug_show, NULL);
}

/*
 * psample debug Proc Write Entry
 *
 *   Syntax:
 *   debug=<mask>
 *
 *   Where <mask> corresponds to the debug module parameter.
 *
 *   Examples:
 *   debug=0x1
 */
static ssize_t
psample_proc_debug_write(struct file *file, const char *buf,
                    size_t count, loff_t *loff)
{
    char debug_str[40];
    char *ptr;

    if (count > sizeof(debug_str)) {
        count = sizeof(debug_str) - 1;
        debug_str[count] = '\0';
    }
    if (copy_from_user(debug_str, buf, count)) {
        return -EFAULT;
    }

    if ((ptr = strstr(debug_str, "debug=")) != NULL) {
        ptr += 6;
        debug = simple_strtol(ptr, NULL, 0);
    } else {
        gprintk("Warning: unknown configuration setting\n");
    }

    return count;
}

struct file_operations psample_proc_debug_file_ops = {
    owner:      THIS_MODULE,
    open:       psample_proc_debug_open,
    read:       seq_read,
    llseek:     seq_lseek,
    write:      psample_proc_debug_write,
    release:    single_release,
};

static int
psample_proc_stats_show(struct seq_file *m, void *v)
{
    seq_printf(m, "BCM KNET %s Callback Stats\n", PSAMPLE_CB_NAME);
    seq_printf(m, "  DCB type %d\n",                          g_psample_info.hw.dcb_type);
    seq_printf(m, "  pkts filter psample cb         %10lu\n", g_psample_stats.pkts_f_psample_cb);
    seq_printf(m, "  pkts sent to psample module    %10lu\n", g_psample_stats.pkts_f_psample_mod);
    seq_printf(m, "  pkts handled by psample        %10lu\n", g_psample_stats.pkts_f_handled);
    seq_printf(m, "  pkts pass through              %10lu\n", g_psample_stats.pkts_f_pass_through);
    seq_printf(m, "  pkts drop no psample group     %10lu\n", g_psample_stats.pkts_d_no_group);
    seq_printf(m, "  pkts drop sampling disabled    %10lu\n", g_psample_stats.pkts_d_sampling_disabled);
    seq_printf(m, "  pkts drop no skb               %10lu\n", g_psample_stats.pkts_d_no_skb);
    seq_printf(m, "  pkts drop psample not ready    %10lu\n", g_psample_stats.pkts_d_not_ready);
    seq_printf(m, "  pkts drop metadata parse error %10lu\n", g_psample_stats.pkts_d_metadata);
    seq_printf(m, "  pkts with invalid src port     %10lu\n", g_psample_stats.pkts_d_meta_srcport);
    seq_printf(m, "  pkts with invalid dst port     %10lu\n", g_psample_stats.pkts_d_meta_dstport);
    seq_printf(m, "  pkts with invalid orig pkt sz  %10lu\n", g_psample_stats.pkts_d_invalid_size);
    return 0;
}

static int
psample_proc_stats_open(struct inode * inode, struct file * file)
{
    return single_open(file, psample_proc_stats_show, NULL);
}

struct file_operations psample_proc_stats_file_ops = {
    owner:      THIS_MODULE,
    open:       psample_proc_stats_open,
    read:       seq_read,
    llseek:     seq_lseek,
    write:      NULL,
    release:    single_release,
};

int psample_cleanup(void)
{
    remove_proc_entry("stats", psample_proc_root);
    remove_proc_entry("rate",  psample_proc_root);
    remove_proc_entry("size",  psample_proc_root);
    remove_proc_entry("debug", psample_proc_root);
    return 0;
}

int psample_init(void)
{
    #define PROCFS_MAX_PATH 1024
    char psample_procfs_path[PROCFS_MAX_PATH];
    struct proc_dir_entry *entry;

    /* create procfs for psample */
    snprintf(psample_procfs_path, PROCFS_MAX_PATH, "bcm/knet-cb");
    proc_mkdir(psample_procfs_path, NULL);
    snprintf(psample_procfs_path, PROCFS_MAX_PATH, "%s/%s", psample_procfs_path, PSAMPLE_CB_NAME);
    psample_proc_root = proc_mkdir(psample_procfs_path, NULL);

    /* create procfs for psample stats */
    PROC_CREATE(entry, "stats", 0666, psample_proc_root, &psample_proc_stats_file_ops);
    if (entry == NULL) {
        gprintk("%s: Unable to create procfs entry '/procfs/%s/stats'\n", __func__, psample_procfs_path);
        return -1;
    }

    /* create procfs for setting sample rates */
    PROC_CREATE(entry, "rate", 0666, psample_proc_root, &psample_proc_rate_file_ops);
    if (entry == NULL) {
        gprintk("%s: Unable to create procfs entry '/procfs/%s/rate'\n", __func__, psample_procfs_path);
        return -1;
    }
    
    /* create procfs for setting sample size */
    PROC_CREATE(entry, "size", 0666, psample_proc_root, &psample_proc_size_file_ops);
    if (entry == NULL) {
        gprintk("%s: Unable to create procfs entry '/procfs/%s/size'\n", __func__, psample_procfs_path);
        return -1;
    }

    /* create procfs for debug log */
    PROC_CREATE(entry, "debug", 0666, psample_proc_root, &psample_proc_debug_file_ops);
    if (entry == NULL) {
        gprintk("%s: Unable to create procfs entry '/procfs/%s/debug'\n", __func__, psample_procfs_path);
        return -1;
    }

    /* clear data structs */
    memset(&g_psample_stats, 0, sizeof(psample_stats_t));
    memset(&g_psample_info, 0, sizeof(psample_info_t));

    /* setup psample_info struct */
    INIT_LIST_HEAD(&g_psample_info.netif_list); 
    spin_lock_init(&g_psample_info.lock);

    /* get net namespace */ 
    g_psample_info.netns = get_net_ns_by_pid(current->pid);
    if (!g_psample_info.netns) {
        gprintk("%s: Could not get network namespace for pid %d\n", __func__, current->pid);
        return (-1);
    }
    PSAMPLE_CB_DBG_PRINT("%s: current->pid %d, netns 0x%p, sample_size %d\n", __func__, 
            current->pid, g_psample_info.netns, psample_size);
   
    return 0;
}
