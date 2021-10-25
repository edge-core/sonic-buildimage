#include <stdlib.h>
#include <syslog.h>
#include "configInterface.h"

int main(int argc, char *argv[]) {
    try {
        std::vector<relay_config> vlans;
        initialize_swss(&vlans);
        loop_relay(&vlans);
    }
    catch (std::exception &e)
    {
        syslog(LOG_ERR, "An exception occurred.\n");
        return 1;
    }
    return 0;
}
