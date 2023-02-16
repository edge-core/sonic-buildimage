#
# Copyright (c) 2018-2022 NVIDIA CORPORATION & AFFILIATES.
# Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# docker image for mlnx saiserver

DOCKER_SAISERVER_MLNX = docker-saiserver$(SAITHRIFT_VER)-mlnx.gz
$(DOCKER_SAISERVER_MLNX)_PATH = $(PLATFORM_PATH)/docker-saiserver-mlnx
$(DOCKER_SAISERVER_MLNX)_DEPENDS += $(SAISERVER)

$(DOCKER_SAISERVER_MLNX)_DEPENDS += $(PYTHON_SDK_API) $(MFT)

ifeq ($(ENABLE_ASAN), y)
$(DOCKER_SAISERVER_MLNX)_DEPENDS += $(SAISERVER_DBG)
endif

$(DOCKER_SAISERVER_MLNX)_FILES += $(ISSU_VERSION_FILE)

ifeq ($(SDK_FROM_SRC), y)
$(DOCKER_SAISERVER_MLNX)_DBG_DEPENDS += $(MLNX_SDK_DBG_DEBS) $(MLNX_SAI_DBGSYM)
endif

# Use syncd_init_common.sh to init hardware platform
SYNCD_INIT_COMMON_SCRIPT = syncd_init_common.sh
$(SYNCD_INIT_COMMON_SCRIPT)_PATH = $(SRC_PATH)/sonic-sairedis/syncd/scripts
SONIC_COPY_FILES += $(SYNCD_INIT_COMMON_SCRIPT)

$(DOCKER_SAISERVER_MLNX)_FILES += $(SYNCD_INIT_COMMON_SCRIPT)
$(DOCKER_SAISERVER_MLNX)_PYTHON_DEBS += $(MLNX_SFPD)
$(DOCKER_SAISERVER_MLNX)_LOAD_DOCKERS += $(DOCKER_CONFIG_ENGINE_BULLSEYE)
SONIC_DOCKER_IMAGES += $(DOCKER_SAISERVER_MLNX)
$(DOCKER_SAISERVER_MLNX)_CONTAINER_NAME = saiserver$(SAITHRIFT_VER)
SONIC_BULLSEYE_DOCKERS += $(DOCKER_SAISERVER_MLNX)

$(DOCKER_SAISERVER_MLNX)_RUN_OPT += --privileged -t
$(DOCKER_SAISERVER_MLNX)_RUN_OPT += -v /host/machine.conf:/etc/machine.conf
$(DOCKER_SAISERVER_MLNX)_RUN_OPT += -v /etc/sonic:/etc/sonic:ro
$(DOCKER_SYNCD_BASE)_RUN_OPT += --tmpfs /run/criu
