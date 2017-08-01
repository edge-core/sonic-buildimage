#!/bin/bash

query_retry_count_max="10"
required_fw_version="13.1400.0126"
fw_file=/etc/mlnx/fw-SPC.mfa

run_or_fail() {
	$1
	if [[ $? != 0 ]]; then
		echo $1 failed
		exit 1
	fi
}

# wait until devices will be available
query_retry_count="0"
mlxfwmanager --query > /dev/null

while [[ (${query_retry_count} -lt ${query_retry_count_max}) && ($? -ne "0") ]]; do
	sleep 1
	query_retry_count=$[${query_retry_count}+1]
	mlxfwmanager --query > /dev/null
done

run_or_fail "mlxfwmanager --query" > /tmp/mlnxfwmanager-query.txt

# get current firmware version
found_fw=false
for word in `cat /tmp/mlnxfwmanager-query.txt`
do
	if [[ ${found_fw} == true ]]; then
		fw_version=${word}
		break
	fi
	if [[ ${word} == FW ]]; then
		found_fw=true
	fi
done

if [[ -z ${fw_version} ]]; then
	echo "Could not retreive current FW version."
	exit 1
fi

if [[ ${required_fw_version} == ${fw_version} ]]; then
	echo "Mellanox firmware is up to date."
else
	echo "Mellanox firmware required version is ${required_fw_version}. Installing compatible version..."
	run_or_fail "mlxfwmanager -i ${fw_file} -u -f -y"
fi
