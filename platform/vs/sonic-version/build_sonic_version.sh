tee $1 > /dev/null <<EOF
build_version: '$sonic_version'
asic_type: $sonic_asic_platform
commit_id: '$(git rev-parse --short HEAD)'
build_date: $(date -u)
build_number: ${BUILD_NUMBER:-0}
built_by: $USER@$BUILD_HOSTNAME
EOF
