## Mellanox non-upstream linux kernel patches ##

To include non-upstream patches into the sonic-linux image during build time, this folder must contain a patch archive.

### Structure of the patch archive

  1. It should contain a file named series. series should provide an order in which the patches have to be applied
  ```
  admin@build-server:/sonic-buildimage/src/sonic-linux-kernel$ cat linux-5.10.103/non_upstream_patches/series
  mlx5-Refactor-module-EEPROM-query.patch
  mlx5-Implement-get_module_eeprom_by_page.patch
  mlx5-Add-support-for-DSFP-module-EEPROM-dumps.patch
  ```
  2. All the patches should be present in the same folder where series resides.
  3. Developers should make sure patches apply cleanly over the existing patches present in the src/sonic-linux-kernel .
  4. Name of the tarball should match with the one specified under EXTERNAL_KERNEL_PATCH_TAR

#### Example
```
admin@build-server:/sonic-buildimage/platform/mellanox/non-upstream-patches$ tar -tf patches.tar.gz
./
./mlx5-Implement-get_module_eeprom_by_page.patch
./mlx5-Add-support-for-DSFP-module-EEPROM-dumps.patch
./series
./mlx5-Refactor-module-EEPROM-query.patch
```

### Include the archive while building sonic linux kernel

Set `INCLUDE_EXTERNAL_PATCH_TAR=y` using `SONIC_OVERRIDE_BUILD_VARS` to include these changes before building the kernel.
- Eg: `NOJESSIE=1 NOSTRETCH=1 NOBUSTER=1 make SONIC_OVERRIDE_BUILD_VARS=' INCLUDE_EXTERNAL_PATCH_TAR=y ' target/debs/bullseye/linux-headers-5.10.0-12-2-common_5.10.103-1_all.deb`
