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
	{ 0xdb7305a1, __VMLINUX_SYMBOL_STR(__stack_chk_fail) },
	{ 0x91715312, __VMLINUX_SYMBOL_STR(sprintf) },
	{ 0x14c72286, __VMLINUX_SYMBOL_STR(i2c_smbus_read_byte_data) },
	{ 0x4f6e1ac4, __VMLINUX_SYMBOL_STR(i2c_smbus_read_word_data) },
	{ 0xfa119060, __VMLINUX_SYMBOL_STR(hwmon_device_register) },
	{ 0xae59a99, __VMLINUX_SYMBOL_STR(sysfs_create_group) },
	{ 0x4b82759, __VMLINUX_SYMBOL_STR(_dev_info) },
	{ 0x888680a0, __VMLINUX_SYMBOL_STR(__mutex_init) },
	{ 0xe52cb2e9, __VMLINUX_SYMBOL_STR(kmem_cache_alloc_trace) },
	{ 0x660b9bcf, __VMLINUX_SYMBOL_STR(kmalloc_caches) },
	{ 0x2ea2c95c, __VMLINUX_SYMBOL_STR(__x86_indirect_thunk_rax) },
	{ 0x27e1a049, __VMLINUX_SYMBOL_STR(printk) },
	{ 0x50eb70fa, __VMLINUX_SYMBOL_STR(i2c_smbus_write_byte_data) },
	{ 0xb742fd7, __VMLINUX_SYMBOL_STR(simple_strtol) },
	{ 0x94218140, __VMLINUX_SYMBOL_STR(mutex_unlock) },
	{ 0xd0b0d91b, __VMLINUX_SYMBOL_STR(i2c_smbus_read_i2c_block_data) },
	{ 0x86b8d7be, __VMLINUX_SYMBOL_STR(mutex_lock) },
	{ 0x37a0cba, __VMLINUX_SYMBOL_STR(kfree) },
	{ 0x9b242c96, __VMLINUX_SYMBOL_STR(sysfs_remove_group) },
	{ 0x81e2daa3, __VMLINUX_SYMBOL_STR(hwmon_device_unregister) },
	{ 0xbdfb6dbb, __VMLINUX_SYMBOL_STR(__fentry__) },
};

static const char __module_depends[]
__used
__attribute__((section(".modinfo"))) =
"depends=";

