# Perform an i2c device configuration : instantiate / delete.
# Input is of the form:
# "echo [driver] <i2c-address> >  <i2c-bus/operation>"
# where operation = "new_device" or "delete_device"

i2c_config() {
    local count=0
    local MAX_BUS_RETRY=20
    local MAX_I2C_OP_RETRY=10

    i2c_bus_op=`echo "$@" | cut -d'>' -f 2`
    i2c_bus=$(dirname $i2c_bus_op)

    # check if bus exists
    while [[ "$count" -lt "$MAX_BUS_RETRY" ]]; do
        [[ -e $i2c_bus ]] && break || sleep .1
        count=$((count+1))
    done

    if [[ "$count" -eq "$MAX_BUS_RETRY" ]]; then
        echo "ERROR: $@ : i2c bus not created"
        return
    fi

    # perform the add/delete
    count=0
    while [[ "$count" -lt "$MAX_I2C_OP_RETRY" ]]; do
        eval "$@" > /dev/null 2>&1
        [[ $? == 0 ]] && break || sleep .2
        count=$((count+1))
    done

    if [[ "$count" -eq "$MAX_I2C_OP_RETRY" ]]; then
        echo "ERROR: $@ : i2c operation failed"
        return
    fi
}

# Check if a i2c bus exists. Poll for upto 2 seconds since mux creation may take time..
# Input: bus to check for existence

i2c_poll_bus_exists() {
    local count=0
    local MAX_BUS_RETRY=20
    local i2c_bus

    i2c_bus=$1

    # check if bus exists
    while [[ "$count" -lt "$MAX_BUS_RETRY" ]]; do
        [[ -e $i2c_bus ]] && break || sleep .1
        count=$((count+1))
    done

    if [[ "$count" -eq "$MAX_BUS_RETRY" ]]; then
        echo "ERROR: $@ : i2c bus not created"
        return 1
    else
        return 0
    fi
}

