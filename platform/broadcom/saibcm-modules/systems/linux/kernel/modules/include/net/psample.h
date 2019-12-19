#ifndef __NET_PSAMPLE_H
#define __NET_PSAMPLE_H

#include <gmodule.h>
#include <uapi/linux/psample.h>
#include <linux/module.h>
#include <linux/list.h>

struct psample_group {
	struct list_head list;
	struct net *net;
	u32 group_num;
	u32 refcount;
	u32 seq;
};

extern struct psample_group *psample_group_get(struct net *net, u32 group_num);
extern void psample_group_put(struct psample_group *group);

extern void psample_sample_packet(struct psample_group *group, struct sk_buff *skb,
			   u32 trunc_size, int in_ifindex, int out_ifindex,
			   u32 sample_rate);

#endif /* __NET_PSAMPLE_H */
