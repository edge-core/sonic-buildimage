#include <linux/module.h>
#include <linux/vermagic.h>
#include <linux/compiler.h>

MODULE_INFO(vermagic, VERMAGIC_STRING);

__visible struct module __this_module
__attribute__((section(".gnu.linkonce.this_module"))) = {
	.name = KBUILD_MODNAME,
	.init = init_module,
#ifdef CONFIG_MODULE_UNLOAD
	.exit = cleanup_module,
#endif
	.arch = MODULE_ARCH_INIT,
};

#ifdef RETPOLINE
MODULE_INFO(retpoline, "Y");
#endif

static const struct modversion_info ____versions[]
__used
__attribute__((section("__versions"))) = {
	{ 0xd1a11d1c, __VMLINUX_SYMBOL_STR(module_layout) },
	{ 0x8308dcad, __VMLINUX_SYMBOL_STR(i2c_del_driver) },
	{ 0x851c3bfc, __VMLINUX_SYMBOL_STR(i2c_register_driver) },
	{ 0xbba4aa3a, __VMLINUX_SYMBOL_STR(devm_hwmon_device_register_with_groups) },
	{ 0x888680a0, __VMLINUX_SYMBOL_STR(__mutex_init) },
	{ 0x2daa70fe, __VMLINUX_SYMBOL_STR(__devm_regmap_init_i2c) },
	{ 0x32a81c89, __VMLINUX_SYMBOL_STR(devm_kmalloc) },
	{ 0x5792f848, __VMLINUX_SYMBOL_STR(strlcpy) },
	{ 0x14c72286, __VMLINUX_SYMBOL_STR(i2c_smbus_read_byte_data) },
	{ 0xa46f2f1b, __VMLINUX_SYMBOL_STR(kstrtouint) },
	{ 0x60ea2d6, __VMLINUX_SYMBOL_STR(kstrtoull) },
	{ 0x783815ef, __VMLINUX_SYMBOL_STR(regmap_update_bits_base) },
	{ 0x94218140, __VMLINUX_SYMBOL_STR(mutex_unlock) },
	{ 0x86b8d7be, __VMLINUX_SYMBOL_STR(mutex_lock) },
	{ 0x1b17e06c, __VMLINUX_SYMBOL_STR(kstrtoll) },
	{ 0xaee034fd, __VMLINUX_SYMBOL_STR(regmap_write) },
	{ 0x5a5a94a6, __VMLINUX_SYMBOL_STR(kstrtou8) },
	{ 0x91715312, __VMLINUX_SYMBOL_STR(sprintf) },
	{ 0xdb7305a1, __VMLINUX_SYMBOL_STR(__stack_chk_fail) },
	{ 0x12872e73, __VMLINUX_SYMBOL_STR(regmap_read) },
	{ 0xbdfb6dbb, __VMLINUX_SYMBOL_STR(__fentry__) },
};

static const char __module_depends[]
__used
__attribute__((section(".modinfo"))) =
"depends=";

MODULE_ALIAS("i2c:nct7511");
