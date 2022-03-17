#include <errno.h>
#include <unistd.h>
#include <event.h>
#include <sstream>
#include <event2/event.h>
#include <event2/bufferevent.h>
#include <syslog.h>
#include <signal.h>

#include "dbconnector.h" 
#include "configInterface.h"
#include "redisclient.h"


struct event *listen_event;
struct event *server_listen_event;
struct event_base *base;
struct event *ev_sigint;
struct event *ev_sigterm;
static std::string counter_table = "DHCPv6_COUNTER_TABLE|";
swss::DBConnector state_db(6, "localhost", 6379, 0);
swss::RedisClient m_stateDbRedisClient(&state_db);

/* DHCPv6 filter */
/* sudo tcpdump -dd "ip6 dst ff02::1:2 && udp dst port 547" */

static struct sock_filter ether_relay_filter[] = {
	
	{ 0x28, 0, 0, 0x0000000c },
	{ 0x15, 0, 13, 0x000086dd },
	{ 0x20, 0, 0, 0x00000026 },
	{ 0x15, 0, 11, 0xff020000 },
	{ 0x20, 0, 0, 0x0000002a },
	{ 0x15, 0, 9, 0x00000000 },
	{ 0x20, 0, 0, 0x0000002e },
	{ 0x15, 0, 7, 0x00000000 },
	{ 0x20, 0, 0, 0x00000032 },
	{ 0x15, 0, 5, 0x00010002 },
	{ 0x30, 0, 0, 0x00000014 },
	{ 0x15, 0, 3, 0x00000011 },
	{ 0x28, 0, 0, 0x00000038 },
	{ 0x15, 0, 1, 0x00000223 },
	{ 0x6, 0, 0, 0x00040000 },
	{ 0x6, 0, 0, 0x00000000 },
};
const struct sock_fprog ether_relay_fprog = {
	lengthof(ether_relay_filter),
	ether_relay_filter
};

/* DHCPv6 Counter */
uint64_t counters[DHCPv6_MESSAGE_TYPE_COUNT];
std::map<int, std::string> counterMap = {{0, "Unknown"},
                                      {1, "Solicit"},
                                      {2, "Advertise"},
                                      {3, "Request"},
                                      {4, "Confirm"},
                                      {5, "Renew"},
                                      {6, "Rebind"},
                                      {7, "Reply"},
                                      {8, "Release"},
                                      {9, "Decline"},
                                      {12, "Relay-Forward"},
                                      {13, "Relay-Reply"}};

/**
 * @code                void initialize_counter(std::string counterVlan);
 *
 * @brief               initialize the counter by each Vlan
 *
 * @param counterVlan   counter table with interface name
 * 
 * @return              none
 */
void initialize_counter(std::string counterVlan) {
    m_stateDbRedisClient.hset(counterVlan, "Unknown", toString(counters[DHCPv6_MESSAGE_TYPE_UNKNOWN]));
    m_stateDbRedisClient.hset(counterVlan, "Solicit", toString(counters[DHCPv6_MESSAGE_TYPE_SOLICIT]));
    m_stateDbRedisClient.hset(counterVlan, "Advertise", toString(counters[DHCPv6_MESSAGE_TYPE_ADVERTISE]));
    m_stateDbRedisClient.hset(counterVlan, "Request", toString(counters[DHCPv6_MESSAGE_TYPE_REQUEST]));
    m_stateDbRedisClient.hset(counterVlan, "Confirm", toString(counters[DHCPv6_MESSAGE_TYPE_CONFIRM]));
    m_stateDbRedisClient.hset(counterVlan, "Renew", toString(counters[DHCPv6_MESSAGE_TYPE_RENEW]));
    m_stateDbRedisClient.hset(counterVlan, "Rebind", toString(counters[DHCPv6_MESSAGE_TYPE_REBIND]));
    m_stateDbRedisClient.hset(counterVlan, "Reply", toString(counters[DHCPv6_MESSAGE_TYPE_REPLY]));
    m_stateDbRedisClient.hset(counterVlan, "Release", toString(counters[DHCPv6_MESSAGE_TYPE_RELEASE]));
    m_stateDbRedisClient.hset(counterVlan, "Decline", toString(counters[DHCPv6_MESSAGE_TYPE_DECLINE]));
    m_stateDbRedisClient.hset(counterVlan, "Relay-Forward", toString(counters[DHCPv6_MESSAGE_TYPE_RELAY_FORW]));
    m_stateDbRedisClient.hset(counterVlan, "Relay-Reply", toString(counters[DHCPv6_MESSAGE_TYPE_RELAY_REPL]));
}

/**
 * @code                void update_counter(std::string CounterVlan, uint8_t msg_type);
 *
 * @brief               update the counter in state_db with count of each DHCPv6 message type
 *
 * @param counterVlan   counter table with interface name
 * @param msg_type      dhcpv6 message type to be updated in counter
 * 
 * @return              none
 */
void update_counter(std::string counterVlan, uint8_t msg_type) {
    m_stateDbRedisClient.hset(counterVlan, counterMap.find(msg_type)->second, toString(counters[msg_type]));
}

/**
 * @code                std::string toString(uint16_t count);
 *
 * @brief               convert uint16_t to string
 *
 * @param count         count of messages in counter
 * 
 * @return              count in string
 */
std::string toString(uint16_t count) {
    std::stringstream ss;
    ss << count;
    std::string countValue = ss.str();
    return countValue;
}

/**
 * @code                const struct ether_header *parse_ether_frame(const uint8_t *buffer, const uint8_t **out_end);
 *
 * @brief               parse through ethernet frame
 *
 * @param *buffer       message buffer
 * @param **out_end     pointer
 * 
 * @return ether_header end of ethernet header position
 */
const struct ether_header *parse_ether_frame(const uint8_t *buffer, const uint8_t **out_end) {
    (*out_end) = buffer + sizeof(struct ether_header);
    return (const struct ether_header *)buffer;
}

/**
 * @code                const struct ip6_hdr *parse_ip6_hdr(const uint8_t *buffer, const uint8_t **out_end);
 *
 * @brief               parse through ipv6 header
 *
 * @param *buffer       message buffer
 * @param **out_end     pointer
 * 
 * @return ip6_hdr      end of ipv6 header position
 */
const struct ip6_hdr *parse_ip6_hdr(const uint8_t *buffer, const uint8_t **out_end) {
    (*out_end) = buffer + sizeof(struct ip6_hdr);
    return (struct ip6_hdr *)buffer;
}

/**
 * @code                const struct udphdr *parse_udp(const uint8_t *buffer, const uint8_t **out_end);
 *
 * @brief               parse through udp header
 *
 * @param *buffer       message buffer
 * @param **out_end     pointer
 * 
 * @return udphdr      end of udp header position
 */
const struct udphdr *parse_udp(const uint8_t *buffer, const uint8_t **out_end) {
    (*out_end) = buffer + sizeof(struct udphdr);
    return (const struct udphdr *)buffer;
}

/**
 * @code                const struct dhcpv6_msg *parse_dhcpv6_hdr(const uint8_t *buffer);
 *
 * @brief               parse through dhcpv6 header
 *
 * @param *buffer       message buffer
 * @param **out_end     pointer
 * 
 * @return dhcpv6_msg   end of dhcpv6 header position
 */
const struct dhcpv6_msg *parse_dhcpv6_hdr(const uint8_t *buffer) {
    return (const struct dhcpv6_msg *)buffer;
}

/**
 * @code                const struct dhcpv6_relay_msg *parse_dhcpv6_relay(const uint8_t *buffer);
 *
 * @brief               parse through dhcpv6 relay message
 *
 * @param *buffer       message buffer
 * @param **out_end     pointer
 * 
 * @return dhcpv6_relay_msg   start of dhcpv6 relay message or end of dhcpv6 message type position
 */
const struct dhcpv6_relay_msg *parse_dhcpv6_relay(const uint8_t *buffer) {
    return (const struct dhcpv6_relay_msg *)buffer;
}

/**
 * @code                const struct dhcpv6_option *parse_dhcpv6_opt(const uint8_t *buffer, const uint8_t **out_end);
 *
 * @brief               parse through dhcpv6 option
 *
 * @param *buffer       message buffer
 * @param **out_end     pointer
 * 
 * @return dhcpv6_option   end of dhcpv6 message option
 */
const struct dhcpv6_option *parse_dhcpv6_opt(const uint8_t *buffer, const uint8_t **out_end) {
    uint32_t size = 4; // option-code + option-len
    size += ntohs(*(uint16_t *)(buffer + 2));
    (*out_end) = buffer + size;

    return (const struct dhcpv6_option *)buffer;
}

/**
 * @code                            void send_udp(int sock, uint8_t *buffer, struct sockaddr_in6 target, uint32_t n, relay_config *config, uint8_t msg_type);
 *
 * @brief                           send udp packet
 *
 * @param *buffer                   message buffer
 * @param sockaddr_in6 target       target socket
 * @param n                         length of message
 * @param relay_config *config      pointer to relay_config
 * @param uint8_t msg_type          message type of dhcpv6 option of relayed message
 * 
 * @return dhcpv6_option   end of dhcpv6 message option
 */
void send_udp(int sock, uint8_t *buffer, struct sockaddr_in6 target, uint32_t n, relay_config *config, uint8_t msg_type) {
    std::string counterVlan = counter_table;
    if(sendto(sock, buffer, n, 0, (const struct sockaddr *)&target, sizeof(target)) == -1)
        syslog(LOG_ERR, "sendto: Failed to send to target address\n");
    else if (counterMap.find(msg_type) != counterMap.end()) {
        counters[msg_type]++;
        update_counter(counterVlan.append(config->interface), msg_type);
    } else {
        syslog(LOG_WARNING, "unexpected message type %d(0x%x)\n", msg_type, msg_type);
    }
}

/**
 * @code                relay_forward(uint8_t *buffer, const struct dhcpv6_msg *msg, uint16_t msg_length);
 *
 * @brief               embed the DHCPv6 message received into DHCPv6 relay forward message
 *
 * @param buffer        pointer to buffer
 * @param msg           pointer to parsed DHCPv6 message
 * @param msg_length    length of DHCPv6 message
 *
 * @return              none
 */
void relay_forward(uint8_t *buffer, const struct dhcpv6_msg *msg, uint16_t msg_length) {
    struct dhcpv6_option option;
    option.option_code = htons(OPTION_RELAY_MSG);
    option.option_length = htons(msg_length);
    memcpy(buffer, &option, sizeof(struct dhcpv6_option));
    memcpy(buffer + sizeof(struct dhcpv6_option), msg, msg_length);
}

/**
 * @code                sock_open(int ifindex, const struct sock_fprog *fprog);
 *
 * @brief               prepare L2 socket to attach to "udp and port 547" filter 
 *
 * @param ifindex       interface index
 * @param fprog         bpf filter "udp and port 547"
 *
 * @return              socket descriptor
 */
int sock_open(int ifindex, const struct sock_fprog *fprog)
{
	if (!ifindex) {
		errno = EINVAL;
		return -1;
	}

	int s = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL));
	if (s == -1) {
		syslog(LOG_ERR, "socket: Failed to create socket\n");
		return -1;
	}

	struct sockaddr_ll sll = {
	    .sll_family = AF_PACKET,
	    .sll_protocol = htons(ETH_P_ALL),
	    .sll_ifindex = ifindex
	};

	if (bind(s, (struct sockaddr *)&sll, sizeof sll) == -1) {
		syslog(LOG_ERR, "bind: Failed to bind to specified interface\n");
		(void) close(s);
	    return -1;
	}

	if (fprog && setsockopt(s, SOL_SOCKET, SO_ATTACH_FILTER, fprog, sizeof *fprog) == -1)
	{
		syslog(LOG_ERR, "setsockopt: Failed to attach filter\n");
		(void) close(s);
	    return -1;
	}

	return s;
}

/**
 * @code                        prepare_relay_config(relay_config *interface_config, int local_sock, int filter);
 * 
 * @brief                       prepare for specified relay interface config: server and link address
 *
 * @param interface_config      pointer to relay config to be prepared
 * @param local_sock            L3 socket used for relaying messages
 * @param filter                socket attached with filter
 *
 * @return                      none
 */
void prepare_relay_config(relay_config *interface_config, int *local_sock, int filter) {
    struct ifaddrs *ifa, *ifa_tmp;
    sockaddr_in6 non_link_local;
    sockaddr_in6 link_local;
    
    interface_config->local_sock = *local_sock;
    interface_config->filter = filter; 

    for(auto server: interface_config->servers) {
        sockaddr_in6 tmp;
        if(inet_pton(AF_INET6, server.c_str(), &tmp.sin6_addr) != 1)
        {
            syslog(LOG_WARNING, "inet_pton: Failed to convert IPv6 address\n");
        }
        tmp.sin6_family = AF_INET6;
        tmp.sin6_flowinfo = 0;
        tmp.sin6_port = htons(RELAY_PORT);
        tmp.sin6_scope_id = 0; 
        interface_config->servers_sock.push_back(tmp);
    }

    if (getifaddrs(&ifa) == -1) {
        syslog(LOG_WARNING, "getifaddrs: Unable to get network interfaces\n");
        exit(1);
    }

    ifa_tmp = ifa;
    while (ifa_tmp) {
        if (ifa_tmp->ifa_addr->sa_family == AF_INET6) {
            struct sockaddr_in6 *in6 = (struct sockaddr_in6*) ifa_tmp->ifa_addr;
            if((strcmp(ifa_tmp->ifa_name, interface_config->interface.c_str()) == 0) && !IN6_IS_ADDR_LINKLOCAL(&in6->sin6_addr)) {    
                non_link_local = *in6;
                break;
            }
            if((strcmp(ifa_tmp->ifa_name, interface_config->interface.c_str()) == 0) && IN6_IS_ADDR_LINKLOCAL(&in6->sin6_addr)) {    
                link_local = *in6;
            }   
        }
    ifa_tmp = ifa_tmp->ifa_next;
    }
    freeifaddrs(ifa); 
    
    if(!IN6_IS_ADDR_LINKLOCAL(&non_link_local.sin6_addr)) {
        interface_config->link_address = non_link_local;
    }
    else {
        interface_config->link_address = link_local;
    }
}

/**
 * @code                prepare_socket(int *local_sock, int *server_sock, relay_config *config, int index);
 * 
 * @brief               prepare L3 socket for sending
 *
 * @param local_sock    pointer to socket binded to global address for relaying client message to server and listening for server message
 * @param server_sock       pointer to socket binded to link_local address for relaying server message to client
 * @param index         scope id of interface
 *
 * @return              none
 */
void prepare_socket(int *local_sock, int *server_sock, relay_config *config, int index) {
    struct ifaddrs *ifa, *ifa_tmp;
    sockaddr_in6 addr;
    sockaddr_in6 ll_addr;
    memset(&addr, 0, sizeof(addr));
    memset(&ll_addr, 0, sizeof(ll_addr));

    if ((*local_sock = socket(AF_INET6, SOCK_DGRAM, 0)) == -1) {
        syslog(LOG_ERR, "socket: Failed to create socket\n");
    }

    if ((*server_sock= socket(AF_INET6, SOCK_DGRAM, 0)) == -1) {
        syslog(LOG_ERR, "socket: Failed to create socket\n");
    }

    
    if (getifaddrs(&ifa) == -1) {
        syslog(LOG_WARNING, "getifaddrs: Unable to get network interfaces\n");
        exit(1);
    }

    ifa_tmp = ifa;
    while (ifa_tmp) {
        if (ifa_tmp->ifa_addr->sa_family == AF_INET6) {
            struct sockaddr_in6 *in6 = (struct sockaddr_in6*) ifa_tmp->ifa_addr;
            if((strcmp(ifa_tmp->ifa_name, config->interface.c_str()) == 0) && !IN6_IS_ADDR_LINKLOCAL(&in6->sin6_addr)) {   
                in6->sin6_family = AF_INET6;
                in6->sin6_port = htons(RELAY_PORT);
                addr = *in6;
            }
            if((strcmp(ifa_tmp->ifa_name, config->interface.c_str()) == 0) && IN6_IS_ADDR_LINKLOCAL(&in6->sin6_addr)) {   
                in6->sin6_family = AF_INET6;
                in6->sin6_port = htons(RELAY_PORT);
                ll_addr = *in6;
            }
        }
        ifa_tmp = ifa_tmp->ifa_next;
    }
    freeifaddrs(ifa); 
    
    if (bind(*local_sock, (sockaddr *)&addr, sizeof(addr)) == -1) {
        syslog(LOG_ERR, "bind: Failed to bind to socket\n");
    } 

    if (bind(*server_sock, (sockaddr *)&ll_addr, sizeof(addr)) == -1) {
        syslog(LOG_ERR, "bind: Failed to bind to socket\n");
    }       
}


/**
 * @code                 relay_client(int sock, const uint8_t *msg, int32_t len, ip6_hdr *ip_hdr, const ether_header *ether_hdr, relay_config *config);
 * 
 * @brief                construct relay-forward message
 *
 * @param sock           L3 socket for sending data to servers
 * @param msg            pointer to dhcpv6 message header position
 * @param len            size of data received
 * @param ip_hdr         pointer to IPv6 header
 * @param ether_hdr      pointer to Ethernet header
 * @param config         pointer to the relay interface config
 *
 * @return none
 */
void relay_client(int sock, const uint8_t *msg, int32_t len, const ip6_hdr *ip_hdr, const ether_header *ether_hdr, relay_config *config) {    
    static uint8_t buffer[4096];
    auto current_buffer_position = buffer;
    dhcpv6_relay_msg new_message;
    new_message.msg_type = DHCPv6_MESSAGE_TYPE_RELAY_FORW;
    memcpy(&new_message.peer_address, &ip_hdr->ip6_src, sizeof(in6_addr));
    new_message.hop_count = 0;

    memcpy(&new_message.link_address, &config->link_address.sin6_addr, sizeof(in6_addr));
    memcpy(current_buffer_position, &new_message, sizeof(dhcpv6_relay_msg));
    current_buffer_position += sizeof(dhcpv6_relay_msg);

    if(config->is_option_79) {
        linklayer_addr_option option79;
        option79.link_layer_type = htons(1);
        option79.option_code = htons(OPTION_CLIENT_LINKLAYER_ADDR);
        option79.option_length = htons(2 + 6); // link_layer_type field + address
        
        memcpy(current_buffer_position, &option79, sizeof(linklayer_addr_option));
        current_buffer_position += sizeof(linklayer_addr_option);

        memcpy(current_buffer_position, &ether_hdr->ether_shost, sizeof(ether_hdr->ether_shost));
        current_buffer_position += sizeof(ether_hdr->ether_shost);
    }

    auto dhcp_message_length = len;
    relay_forward(current_buffer_position, parse_dhcpv6_hdr(msg), dhcp_message_length);
    current_buffer_position += dhcp_message_length + sizeof(dhcpv6_option);

    for(auto server: config->servers_sock) {
        send_udp(sock, buffer, server, current_buffer_position - buffer, config, new_message.msg_type);
    }
}

/**
 * @code                 relay_relay_forw(int sock, const uint8_t *msg, int32_t len, const ip6_hdr *ip_hdr, relay_config *config)
 *
 * @brief                construct a relay-forward message encapsulated relay-forward message
 *
 * @param sock           L3 socket for sending data to servers
 * @param msg            pointer to dhcpv6 message header position
 * @param len            size of data received
 * @param ip_hdr         pointer to IPv6 header
 * @param config         pointer to the relay interface config
 *
 * @return none
 */
void relay_relay_forw(int sock, const uint8_t *msg, int32_t len, const ip6_hdr *ip_hdr, relay_config *config) {
    static uint8_t buffer[4096];
    dhcpv6_relay_msg new_message;
    auto current_buffer_position = buffer;
    auto dhcp_relay_header = parse_dhcpv6_relay(msg);

    if (dhcp_relay_header->hop_count >= HOP_LIMIT)
        return;

    new_message.msg_type = DHCPv6_MESSAGE_TYPE_RELAY_FORW;
    memcpy(&new_message.peer_address, &ip_hdr->ip6_src, sizeof(in6_addr));
    new_message.hop_count = dhcp_relay_header->hop_count + 1;

    memset(&new_message.link_address, 0, sizeof(in6_addr));

    memcpy(current_buffer_position, &new_message, sizeof(dhcpv6_relay_msg));
    current_buffer_position += sizeof(dhcpv6_relay_msg);

    auto dhcp_message_length = len;
    relay_forward(current_buffer_position, parse_dhcpv6_hdr(msg), dhcp_message_length);
    current_buffer_position += dhcp_message_length + sizeof(dhcpv6_option);

    for(auto server: config->servers_sock) {
        send_udp(sock, buffer, server, current_buffer_position - buffer, config, new_message.msg_type);
    }
}

/**
 * @code                relay_relay_reply(int sock, const uint8_t *msg, int32_t len, relay_config *configs);
 * 
 * @brief               relay and unwrap a relay-reply message
 *
 * @param sock          L3 socket for sending data to servers
 * @param msg           pointer to dhcpv6 message header position
 * @param len           size of data received
 * @param config        relay interface config
 *
 * @return              none
 */
 void relay_relay_reply(int sock, const uint8_t *msg, int32_t len, relay_config *config) {
    static uint8_t buffer[4096];
    uint8_t type = 0;
    struct sockaddr_in6 target_addr;
    auto current_buffer_position = buffer;
    auto current_position = msg;
    const uint8_t *tmp = NULL;
    auto dhcp_relay_header = parse_dhcpv6_relay(msg);
    current_position += sizeof(struct dhcpv6_relay_msg);

    auto position = current_position + sizeof(struct dhcpv6_option);
    auto dhcpv6msg = parse_dhcpv6_hdr(position);

    while ((current_position - msg) < len) {
        auto option = parse_dhcpv6_opt(current_position, &tmp);
        current_position = tmp;
        if (current_position - msg > len || ntohs(option->option_length) > sizeof(buffer) - (current_buffer_position - buffer)) {
            break;
        }
        switch (ntohs(option->option_code)) {
            case OPTION_RELAY_MSG:
                memcpy(current_buffer_position, ((uint8_t *)option) + sizeof(struct dhcpv6_option), ntohs(option->option_length));
                current_buffer_position += ntohs(option->option_length);
                type = dhcpv6msg->msg_type;
                break;
            default:
                break;
        }
    }

    memcpy(&target_addr.sin6_addr, &dhcp_relay_header->peer_address, sizeof(struct in6_addr));
    target_addr.sin6_family = AF_INET6;
    target_addr.sin6_flowinfo = 0;
    target_addr.sin6_port = htons(CLIENT_PORT);
    target_addr.sin6_scope_id = if_nametoindex(config->interface.c_str());

    send_udp(sock, buffer, target_addr, current_buffer_position - buffer, config, type);
} 


/**
 * @code                callback(evutil_socket_t fd, short event, void *arg);
 * 
 * @brief               callback for libevent that is called everytime data is received at the filter socket
 *
 * @param fd            filter socket
 * @param event         libevent triggered event  
 * @param arg           callback argument provided by user
 *
 * @return              none
 */
void callback(evutil_socket_t fd, short event, void *arg) {
    struct relay_config *config = (struct relay_config *)(arg);
    static uint8_t message_buffer[4096];
    int32_t len = recv(config->filter, message_buffer, 4096, 0);
    if (len <= 0) {
        syslog(LOG_WARNING, "recv: Failed to receive data at filter socket: %s\n", strerror(errno));
        return;
    }

    char* ptr = (char *)message_buffer;
    const uint8_t *current_position = (uint8_t *)ptr; 
    const uint8_t *tmp = NULL;
    const uint8_t *prev = NULL;

    auto ether_header = parse_ether_frame(current_position, &tmp);
    current_position = tmp;

    auto ip_header = parse_ip6_hdr(current_position, &tmp);
    current_position = tmp;

    prev = current_position;
    if (ip_header->ip6_ctlun.ip6_un1.ip6_un1_nxt != IPPROTO_UDP) {
        const struct ip6_ext *ext_header;
        do {
            ext_header = (const struct ip6_ext *)current_position;
            current_position += ext_header->ip6e_len;
            if((current_position == prev) || (current_position >= (uint8_t *)ptr + sizeof(message_buffer))) {
                return;
            }
            prev = current_position;
        }
        while (ext_header->ip6e_nxt != IPPROTO_UDP);
    }  

    auto udp_header = parse_udp(current_position, &tmp);
    current_position = tmp;

    auto msg = parse_dhcpv6_hdr(current_position);
    counters[msg->msg_type]++;
    std::string counterVlan = counter_table;
    update_counter(counterVlan.append(config->interface), msg->msg_type);

    switch (msg->msg_type) {
        case DHCPv6_MESSAGE_TYPE_RELAY_FORW:
        {
            relay_relay_forw(config->local_sock, current_position, ntohs(udp_header->len) - sizeof(udphdr), ip_header, config);
            break;
        }
        default:
        {
            relay_client(config->local_sock, current_position, ntohs(udp_header->len) - sizeof(udphdr), ip_header, ether_header, config);
            break;
        }
    }
}

/**
 * @code                void server_callback(evutil_socket_t fd, short event, void *arg);
 * 
 * @brief               callback for libevent that is called everytime data is received at the server socket
 *
 * @param fd            filter socket
 * @param event         libevent triggered event  
 * @param arg           callback argument provided by user
 *
 * @return              none
 */
void server_callback(evutil_socket_t fd, short event, void *arg) {
    struct relay_config *config = (struct relay_config *)arg;
    sockaddr_in6 from;
    socklen_t len = sizeof(from);
    int32_t data = 0;
    static uint8_t message_buffer[4096];

    if ((data = recvfrom(config->local_sock, message_buffer, 4096, 0, (sockaddr *)&from, &len)) == -1) {
        syslog(LOG_WARNING, "recv: Failed to receive data from server\n");
    }

    auto msg = parse_dhcpv6_hdr(message_buffer);

    counters[msg->msg_type]++;
    std::string counterVlan = counter_table;
    update_counter(counterVlan.append(config->interface), msg->msg_type);
    if (msg->msg_type == DHCPv6_MESSAGE_TYPE_RELAY_REPL) {
        relay_relay_reply(config->server_sock, message_buffer, data, config);
    }
}

/**
 * @code signal_init();
 *
 * @brief initialize DHCPv6 Relay libevent signals
 */
int signal_init() {
    int rv = -1;
     do {
        ev_sigint = evsignal_new(base, SIGINT, signal_callback, base);
        if (ev_sigint == NULL) {
            syslog(LOG_ERR, "Could not create SIGINT libevent signal\n");
            break;
        }

        ev_sigterm = evsignal_new(base, SIGTERM, signal_callback, base);
        if (ev_sigterm == NULL) {
            syslog(LOG_ERR, "Could not create SIGTERM libevent signal\n");
            break;
        }
        rv = 0;
    } while(0);
    return rv;
}

/**
 * @code signal_start();
 *
 * @brief start DHCPv6 Relay libevent base and add signals
 */
int signal_start()
{
    int rv = -1;
    do
    {
        if (evsignal_add(ev_sigint, NULL) != 0) {
            syslog(LOG_ERR, "Could not add SIGINT libevent signal\n");
            break;
        }

        if (evsignal_add(ev_sigterm, NULL) != 0) {
            syslog(LOG_ERR, "Could not add SIGTERM libevent signal\n");
            break;
        }

        if (event_base_dispatch(base) != 0) {
            syslog(LOG_ERR, "Could not start libevent dispatching loop\n");
        }

        rv = 0;
    } while (0);

    return rv;
}

/**
 * @code signal_callback(fd, event, arg);
 *
 * @brief signal handler for dhcp6relay. Initiate shutdown when signal is caught
 *
 * @param fd        libevent socket
 * @param event     event triggered
 * @param arg       pointer to libevent base
 *
 * @return none
 */
void signal_callback(evutil_socket_t fd, short event, void *arg)
{
    syslog(LOG_ALERT, "Received signal: '%s'\n", strsignal(fd));
    if ((fd == SIGTERM) || (fd == SIGINT)) {
        dhcp6relay_stop();
    }
}

/**
 * @code dhcp6relay_stop();
 *
 * @brief stop DHCPv6 Relay libevent loop upon signal
 */
void dhcp6relay_stop()
{
    event_base_loopexit(base, NULL);
}

/**
 * @code                loop_relay(std::vector<relay_config> *vlans);
 * 
 * @brief               main loop: configure sockets, create libevent base, start server listener thread
 *  
 * @param vlans         list of vlans retrieved from config_db
 */
void loop_relay(std::vector<relay_config> *vlans) {
    std::vector<int> sockets;
    base = event_base_new();
    if(base == NULL) {
        syslog(LOG_ERR, "libevent: Failed to create base\n");
    }

    for(relay_config &vlan : *vlans) {
        relay_config *config = &vlan;
        int filter = 0;
        int local_sock = 0; 
        int server_sock = 0;
        int index = if_nametoindex(config->interface.c_str());

        std::string counterVlan = counter_table;
        initialize_counter(counterVlan.append(config->interface));

        filter = sock_open(index, &ether_relay_fprog);
        prepare_socket(&local_sock, &server_sock, config, index);

        config->local_sock = local_sock;
        config->server_sock = server_sock;
        
        sockets.push_back(filter);
        sockets.push_back(local_sock);
        sockets.push_back(server_sock);

        prepare_relay_config(config, &local_sock, filter);

        evutil_make_listen_socket_reuseable(filter);
        evutil_make_socket_nonblocking(filter);

        evutil_make_listen_socket_reuseable(local_sock);
        evutil_make_socket_nonblocking(local_sock);

        listen_event = event_new(base, filter, EV_READ|EV_PERSIST, callback, config);
        server_listen_event = event_new(base, local_sock, EV_READ|EV_PERSIST, server_callback, config);
        if (listen_event == NULL || server_listen_event == NULL) {
            syslog(LOG_ERR, "libevent: Failed to create libevent\n");
        }

        event_add(listen_event, NULL);
        event_add(server_listen_event, NULL);
    }
    
    if((signal_init() == 0) && signal_start() == 0) {
        shutdown();
        for(std::size_t i = 0; i<sockets.size(); i++) {
            close(sockets.at(i));
        }
    }
}

/**
 * @code shutdown();
 *
 * @brief free signals and terminate threads
 */
void shutdown() {
    event_del(ev_sigint);
    event_del(ev_sigterm);
    event_free(ev_sigint); 
    event_free(ev_sigterm);
    event_base_free(base);
    deinitialize_swss();
}
