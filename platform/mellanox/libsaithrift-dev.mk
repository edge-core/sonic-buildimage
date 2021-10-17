#
# Copyright (c) 2017-2021 NVIDIA CORPORATION & AFFILIATES.
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
# libsaithrift-dev package

SAI_VER = 0.9.4

LIBSAITHRIFT_DEV = libsaithrift-dev_$(SAI_VER)_amd64.deb
$(LIBSAITHRIFT_DEV)_SRC_PATH = $(SRC_PATH)/sonic-sairedis/SAI
$(LIBSAITHRIFT_DEV)_DEPENDS += $(LIBTHRIFT) $(LIBTHRIFT_DEV) $(PYTHON_THRIFT) $(THRIFT_COMPILER) $(MLNX_SAI) $(MLNX_SAI_DEV)
$(LIBSAITHRIFT_DEV)_RDEPENDS += $(LIBTHRIFT) $(MLNX_SAI)
SONIC_DPKG_DEBS += $(LIBSAITHRIFT_DEV)

PYTHON_SAITHRIFT = python-saithrift_$(SAI_VER)_amd64.deb
$(eval $(call add_extra_package,$(LIBSAITHRIFT_DEV),$(PYTHON_SAITHRIFT)))

SAISERVER = saiserver_$(SAI_VER)_amd64.deb
$(SAISERVER)_RDEPENDS += $(LIBTHRIFT) $(MLNX_SAI)
$(eval $(call add_extra_package,$(LIBSAITHRIFT_DEV),$(SAISERVER)))

SAISERVER_DBG = saiserver-dbg_$(SAI_VER)_amd64.deb
$(SAISERVER_DBG)_RDEPENDS += $(SAISERVER)
$(eval $(call add_extra_package,$(LIBSAITHRIFT_DEV),$(SAISERVER_DBG)))
