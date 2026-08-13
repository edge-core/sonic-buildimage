// SPDX-License-Identifier: GPL-2.0
/*
 * i2c-ocores.c: I2C bus driver for OpenCores I2C controller
 * (https://opencores.org/project/i2c/overview)
 *
 * Peter Korsgaard <peter@korsgaard.com>
 *
 * Support for the GRLIB port of the controller by
 * Andreas Larsson <andreas@gaisler.com>
 */

#include <linux/clk.h>
#include <linux/delay.h>
#include <linux/err.h>
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/errno.h>
#include <linux/platform_device.h>
#include <linux/i2c.h>
#include <linux/interrupt.h>
#include <linux/wait.h>
#include <linux/platform_data/i2c-ocores.h>
#include <linux/slab.h>
#include <linux/io.h>
#include <linux/log2.h>
#include <linux/spinlock.h>
#include <linux/jiffies.h>
#include <linux/ktime.h>
#include <linux/timekeeping.h>
#include <linux/atomic.h>
#include <linux/sysfs.h>
#include <linux/build_bug.h>  /* static_assert() */

/*
 * 'process_lock' exists because ocores_process() and ocores_process_timeout()
 * can't run in parallel.
 */
struct ocores_i2c {
    void __iomem *base;
    int iobase;
    u32 reg_shift;
    u32 reg_io_width;
    unsigned long flags;
    wait_queue_head_t wait;
    struct i2c_adapter adap;
    struct i2c_msg *msg;
    int pos;
    int nmsgs;
    int state; /* see STATE_ */
    int xfer_err;
    spinlock_t process_lock;
    struct clk *clk;
    int ip_clock_khz;
    int bus_clock_khz;
    void (*setreg)(struct ocores_i2c *i2c, int reg, u8 value);
    u8 (*getreg)(struct ocores_i2c *i2c, int reg);
};

/* registers */
#define OCI2C_PRELOW		0
#define OCI2C_PREHIGH		1
#define OCI2C_CONTROL		2
#define OCI2C_DATA		3
#define OCI2C_CMD		4 /* write only */
#define OCI2C_STATUS		4 /* read only, same address as OCI2C_CMD */

#define OCI2C_CTRL_IEN		0x40
#define OCI2C_CTRL_EN		0x80

#define OCI2C_CMD_START		0x91
#define OCI2C_CMD_STOP		0x41
#define OCI2C_CMD_READ		0x21
#define OCI2C_CMD_WRITE		0x11
#define OCI2C_CMD_READ_ACK	0x21
#define OCI2C_CMD_READ_NACK	0x29
#define OCI2C_CMD_IACK		0x01

#define OCI2C_STAT_IF		0x01
#define OCI2C_STAT_TIP		0x02
#define OCI2C_STAT_ARBLOST	0x20
#define OCI2C_STAT_BUSY		0x40
#define OCI2C_STAT_NACK		0x80

#define STATE_DONE		0
#define STATE_START		1
#define STATE_WRITE		2
#define STATE_READ		3
#define STATE_ERROR		4

#define TYPE_OCORES		0
#define TYPE_GRLIB		1
#define TYPE_SIFIVE_REV0	2

#define OCORES_FLAG_BROKEN_IRQ BIT(1) /* Broken IRQ for FU540-C000 SoC */

static unsigned int timeout = 1;
module_param(timeout , uint, S_IRUGO|S_IWUSR);
MODULE_PARM_DESC(timeout, "Tiemout for ocores_poll_wait, in unit of milliseconds.");

static unsigned int debug = 1;
module_param(debug , uint, S_IRUGO|S_IWUSR);
MODULE_PARM_DESC(debug, "Enable or disable debug message. 1 -> enable, 0 -> disable");

spinlock_t cpld_access_lock;
EXPORT_SYMBOL(cpld_access_lock);

#define LOCK(lock)      \
do {                                                \
    spin_lock(lock);                                \
} while (0)

#define UNLOCK(lock)    \
do {                                                \
    spin_unlock(lock);                              \
} while (0)

/*
 * FPGA SPI busy polling workaround parameters.
 *
 * These values are now exposed as module parameters so the platform team can
 * tune them at runtime during MCE reproduction, FPGA validation, or platform
 * bring-up, without rebuilding the driver.  They are readable and writable
 * through sysfs under (the exact module name depends on how the driver is
 * built and loaded):
 *
 *   /sys/module/<module name>/parameters/spi_poll_delay_us
 *   /sys/module/<module name>/parameters/spi_idle_stable_count
 *   /sys/module/<module name>/parameters/spi_idle_guard_delay_us
 *   /sys/module/<module name>/parameters/spi_post_write_guard_delay_us
 *
 * The *_DEFAULT macros below are only the build-time default values.  They are
 * also used by the static_assert() further down, so the default combination is
 * still checked at compile time.
 *
 * spi_poll_delay_us:
 * Delay between two reads of the FPGA SPI busy register.
 *
 * The original code reads spi_busy_reg in a tight loop.  On AS9817-64O, this
 * may create very high rate BAR0 MMIO reads.  A small delay can reduce the
 * MMIO pressure to the FPGA PCIe endpoint.  It also gives the busy status more
 * time to become stable if the status comes from another FPGA clock domain.
 *
 * Suggested tuning:
 *   1 us  - Default value to try first.  Lower performance impact.
 *   5 us  - More safe if MCE can still be reproduced.
 *   10 us - Very safe.  Use only if needed because I2C polling will be slower.
 *
 * spi_idle_stable_count:
 * Number of continuous idle samples before wait_spi() treats the SPI path as
 * idle.
 *
 * This avoids using only one idle sample as the ready condition.  The FPGA
 * busy bit may become idle before the whole FPGA internal path is ready for
 * the next BAR access.  Requiring several idle samples makes the software flow
 * control more conservative.
 *
 * Suggested tuning:
 *   1 - Close to the old behavior.  Not suggested for this issue.
 *   3 - Default value.  Good balance between safety and latency.
 *   5 - More safe if the busy bit is suspected to be unstable.
 *
 * spi_idle_guard_delay_us:
 * Common guard delay after stable idle before the next FPGA BAR access.
 *
 * This delay is added before the caller continues to access BAR1/BAR2
 * OpenCores registers. The default is 0 so the read path keeps the original
 * latency unless the value is changed at runtime.
 *
 * spi_post_write_guard_delay_us:
 * Extra delay after writing one FPGA BAR register.
 *
 * wait_spi() only checks that the FPGA SPI path is idle before the register
 * access. Some FPGA write paths may still need a short post-write settle time
 * after the write accessor returns, so this delay is applied only after
 * write accesses. The value is exported so the FPGA sysfs driver and the
 * OpenCores register write path use the same tuning knob.
 */
#define OCORES_SPI_POLL_DELAY_US_DEFAULT        1
#define OCORES_SPI_IDLE_STABLE_COUNT_DEFAULT    1
#define OCORES_SPI_IDLE_GUARD_DELAY_US_DEFAULT  0
#define OCORES_SPI_POST_WRITE_GUARD_DELAY_US_DEFAULT  15

/*
 * Allowed ranges for the runtime parameters.  Writes through sysfs or the
 * kernel command line that fall outside these ranges are rejected, so a bad
 * value can never take effect.  The upper bounds on the delays keep udelay()
 * inside its safe range: udelay() is a busy loop whose internal math is only
 * accurate for small delays, and a very large value would also busy wait for a
 * long time inside the polling critical section (where local interrupts are
 * disabled), which can trigger a soft lockup or watchdog reset.
 */
#define OCORES_SPI_POLL_DELAY_US_MIN            0
#define OCORES_SPI_POLL_DELAY_US_MAX            1000
#define OCORES_SPI_IDLE_STABLE_COUNT_MIN        1
#define OCORES_SPI_IDLE_STABLE_COUNT_MAX        1000
#define OCORES_SPI_IDLE_GUARD_DELAY_US_MIN      0
#define OCORES_SPI_IDLE_GUARD_DELAY_US_MAX      1000
#define OCORES_SPI_POST_WRITE_GUARD_DELAY_US_MIN 0
#define OCORES_SPI_POST_WRITE_GUARD_DELAY_US_MAX 1000

/**
 * ocores_set_uint_range - Parse and range-check one uint module parameter
 * @val: New value as a string, from sysfs or the kernel command line.
 * @kp: Kernel parameter; kp->arg points to the unsigned int to update.
 * @min: Smallest value that is allowed.
 * @max: Largest value that is allowed.
 *
 * The new value is stored only if it parses and is inside [@min, @max].  An
 * out of range value is rejected so a bad write cannot silently take effect;
 * this also keeps the udelay() based delays inside their safe range.
 *
 * Return: 0 on success, negative errno on parse error or out of range value.
 */
static int ocores_set_uint_range(const char *val,
                                 const struct kernel_param *kp,
                                 unsigned int min, unsigned int max)
{
    unsigned int n;
    int ret;

    ret = kstrtouint(val, 0, &n);
    if (ret) {
        return ret;
    }

    if (n < min || n > max) {
        pr_warn("%s: value %u is out of range [%u, %u]\n",
                kp->name, n, min, max);
        return -EINVAL;
    }

    *(unsigned int *)kp->arg = n;
    return 0;
}

/* spi_post_write_guard_delay_us: parse with its own allowed range. */
static int ocores_set_spi_post_write_guard_delay_us(const char *val,
                                                    const struct kernel_param *kp)
{
    return ocores_set_uint_range(val, kp,
                                 OCORES_SPI_POST_WRITE_GUARD_DELAY_US_MIN,
                                 OCORES_SPI_POST_WRITE_GUARD_DELAY_US_MAX);
}
static const struct kernel_param_ops ocores_spi_post_write_guard_delay_us_ops = {
    .set = ocores_set_spi_post_write_guard_delay_us,
    .get = param_get_uint,
};

/* spi_poll_delay_us: parse with its own allowed range. */
static int ocores_set_spi_poll_delay_us(const char *val,
                                        const struct kernel_param *kp)
{
    return ocores_set_uint_range(val, kp,
                                 OCORES_SPI_POLL_DELAY_US_MIN,
                                 OCORES_SPI_POLL_DELAY_US_MAX);
}
static const struct kernel_param_ops ocores_spi_poll_delay_us_ops = {
    .set = ocores_set_spi_poll_delay_us,
    .get = param_get_uint,
};

/* spi_idle_stable_count: parse with its own allowed range. */
static int ocores_set_spi_idle_stable_count(const char *val,
                                            const struct kernel_param *kp)
{
    return ocores_set_uint_range(val, kp,
                                 OCORES_SPI_IDLE_STABLE_COUNT_MIN,
                                 OCORES_SPI_IDLE_STABLE_COUNT_MAX);
}
static const struct kernel_param_ops ocores_spi_idle_stable_count_ops = {
    .set = ocores_set_spi_idle_stable_count,
    .get = param_get_uint,
};

/* spi_idle_guard_delay_us: parse with its own allowed range. */
static int ocores_set_spi_idle_guard_delay_us(const char *val,
                                              const struct kernel_param *kp)
{
    return ocores_set_uint_range(val, kp,
                                 OCORES_SPI_IDLE_GUARD_DELAY_US_MIN,
                                 OCORES_SPI_IDLE_GUARD_DELAY_US_MAX);
}
static const struct kernel_param_ops ocores_spi_idle_guard_delay_us_ops = {
    .set = ocores_set_spi_idle_guard_delay_us,
    .get = param_get_uint,
};

static unsigned int spi_poll_delay_us = OCORES_SPI_POLL_DELAY_US_DEFAULT;
module_param_cb(spi_poll_delay_us, &ocores_spi_poll_delay_us_ops,
                &spi_poll_delay_us, S_IRUGO|S_IWUSR);
MODULE_PARM_DESC(spi_poll_delay_us, "Delay between FPGA SPI busy-register reads (us). Range [0, 1000].");

static unsigned int spi_idle_stable_count = OCORES_SPI_IDLE_STABLE_COUNT_DEFAULT;
module_param_cb(spi_idle_stable_count, &ocores_spi_idle_stable_count_ops,
                &spi_idle_stable_count, S_IRUGO|S_IWUSR);
MODULE_PARM_DESC(spi_idle_stable_count, "Consecutive idle samples required before SPI is treated as idle. Range [1, 1000].");

static unsigned int spi_idle_guard_delay_us = OCORES_SPI_IDLE_GUARD_DELAY_US_DEFAULT;
module_param_cb(spi_idle_guard_delay_us, &ocores_spi_idle_guard_delay_us_ops,
                &spi_idle_guard_delay_us, S_IRUGO|S_IWUSR);
MODULE_PARM_DESC(spi_idle_guard_delay_us, "Guard delay after stable idle before the next FPGA BAR access (us). Range [0, 1000].");

unsigned int spi_post_write_guard_delay_us =
    OCORES_SPI_POST_WRITE_GUARD_DELAY_US_DEFAULT;
module_param_cb(spi_post_write_guard_delay_us,
                &ocores_spi_post_write_guard_delay_us_ops,
                &spi_post_write_guard_delay_us, S_IRUGO|S_IWUSR);
MODULE_PARM_DESC(spi_post_write_guard_delay_us,
                 "Post-write guard delay after FPGA BAR write (us). Range [0, 1000].");
EXPORT_SYMBOL(spi_post_write_guard_delay_us);

/*
 * spi_wait_timeout_us:
 * Timeout for waiting SPI busy bits to become stable idle, in microseconds.
 *
 * This timeout does not include spi_idle_guard_delay_us.  The common guard
 * delay is applied by wait_spi() after stable idle is detected.
 *
 * It also does not include spi_post_write_guard_delay_us, which is applied
 * by write helpers after the BAR write accessor returns.
 *
 * This value is passed to wait_spi() as the per-call timeout at every checked
 * register access site.  OCORES_SPI_WAIT_TIMEOUT_US_DEFAULT is only the
 * build-time default and is also used by the static_assert() below.
 */
#define OCORES_SPI_WAIT_TIMEOUT_US_DEFAULT      1000
#define OCORES_SPI_WAIT_TIMEOUT_US_MIN          1
#define OCORES_SPI_WAIT_TIMEOUT_US_MAX          1000000

/* spi_wait_timeout_us: parse with its own allowed range. */
static int ocores_set_spi_wait_timeout_us(const char *val,
                                          const struct kernel_param *kp)
{
    return ocores_set_uint_range(val, kp,
                                 OCORES_SPI_WAIT_TIMEOUT_US_MIN,
                                 OCORES_SPI_WAIT_TIMEOUT_US_MAX);
}
static const struct kernel_param_ops ocores_spi_wait_timeout_us_ops = {
    .set = ocores_set_spi_wait_timeout_us,
    .get = param_get_uint,
};

static unsigned int spi_wait_timeout_us = OCORES_SPI_WAIT_TIMEOUT_US_DEFAULT;
module_param_cb(spi_wait_timeout_us, &ocores_spi_wait_timeout_us_ops,
                &spi_wait_timeout_us, S_IRUGO|S_IWUSR);
MODULE_PARM_DESC(spi_wait_timeout_us, "Timeout for FPGA SPI to reach stable idle (us); guard delay excluded. Range [1, 1000000].");

/*
 * These three values are linked.  wait_spi() needs spi_idle_stable_count idle
 * samples in a row, taken spi_poll_delay_us apart, and the timeout
 * (spi_wait_timeout_us) is checked against the same time.  So the timeout must
 * be long enough to fit the whole run of idle samples; if not, wait_spi() can
 * return -ETIMEDOUT before it ever collects enough idle samples.  This is very
 * likely once the first sample is busy, which is the normal reason we wait.
 *
 * Because all three are now runtime module parameters, this relation cannot be
 * fully checked at compile time.  wait_spi() re-checks it at runtime (when
 * debug is enabled) using the live parameter values and warns if the timeout
 * is too small.  The static_assert() below only checks the build-time default
 * combination, as a minimum sanity check (just the run of idle samples).
 *
 * To be safe, also leave extra room for an initial busy time, for example make
 * the timeout a few times spi_idle_stable_count * spi_poll_delay_us.  If you
 * raise spi_poll_delay_us or spi_idle_stable_count, raise spi_wait_timeout_us
 * too.
 */
static_assert(OCORES_SPI_WAIT_TIMEOUT_US_DEFAULT >=
              OCORES_SPI_IDLE_STABLE_COUNT_DEFAULT *
              OCORES_SPI_POLL_DELAY_US_DEFAULT,
              "OCORES_SPI_WAIT_TIMEOUT_US_DEFAULT too small for the SPI idle sample run");

void __iomem    *spi_busy_reg=NULL;
EXPORT_SYMBOL(spi_busy_reg);

/*
 * wait_spi() implementation selection.
 *
 *   LEGACY - Original simple busy-poll: jiffies timeout, break on the first
 *            idle sample, no stable-idle samples and no guard delay.  Kept as
 *            the baseline for MCE reproduction / A-B comparison.  Note jiffies
 *            does not advance while local interrupts are disabled, so this can
 *            time out wrongly in polling mode.
 *   STABLE - ktime deadline + several continuous idle samples
 *            (spi_idle_stable_count) + common guard delay
 *            (spi_idle_guard_delay_us). Default.
 */
#define OCORES_SPI_WAIT_IMPL_LEGACY  0
#define OCORES_SPI_WAIT_IMPL_STABLE  1
#define OCORES_SPI_WAIT_IMPL         OCORES_SPI_WAIT_IMPL_STABLE


#if OCORES_SPI_WAIT_IMPL == OCORES_SPI_WAIT_IMPL_STABLE
/**
 * wait_spi - Wait until FPGA SPI busy bits are stable idle
 * @mask: SPI busy bit mask.
 * @timeout_us: Timeout in microseconds for waiting stable idle.
 *
 * The FPGA SPI busy register may not mean that the whole FPGA PCIe/MMIO path
 * is ready for the next BAR access.  Do not use only one idle sample as the
 * safe condition.  The selected busy bits must be idle for several continuous
 * samples before the caller can access the next register.
 *
 * wait_spi() only applies spi_idle_guard_delay_us after stable idle.  The
 * optional post-write guard is handled by write helpers after the BAR write
 * accessor returns.
 *
 * Poll loop:
 *
 *   +--> read busy bit (status & mask)
 *   |        |
 *   |        v
 *   |     busy ? --- yes ---> count = 0 ----------------+
 *   |        | no                                       |
 *   |        v                                          |
 *   |     count++                                       |
 *   |        |                                          |
 *   |        v                                          |
 *   |     count >= STABLE_COUNT ? --- yes ---> udelay(GUARD_DELAY)
 *   |        | no                              return 0  (idle, ok)
 *   |        v                                          |
 *   |     <---------------------------------------------+
 *   |        |
 *   |        v
 *   |     now > deadline ? --- yes ---> return -ETIMEDOUT
 *   |        | no
 *   |        v
 *   |     udelay(POLL_DELAY)
 *   |        |
 *   +--------+
 * Return: 0 on success, negative errno on failure.
 */
int wait_spi(u32 mask, unsigned long timeout_us)
{
    ktime_t start;
    ktime_t deadline;
    ktime_t read_start;
    ktime_t now;
    s64 last_read_us;
    s64 max_read_us;
    unsigned int stable;
    unsigned int stable_count;
    unsigned int poll_delay_us;
    unsigned int guard_delay_us;
    u32 data;
    u32 busy;
    u32 ri = 0;
    int dbg;

    /* pr_info("CPLD %u, Will time-out at jiffie %lu\n", cpld_id,timeout); */
    if (!spi_busy_reg) {
        return -EFAULT;
    }

    /*
     * Take a single snapshot of the tunable parameters for the whole call.
     * They are writable module parameters, so a concurrent sysfs write could
     * change them in the middle of the poll loop.  READ_ONCE() keeps the value
     * stable inside this call and stops the compiler from re-reading the
     * globals on every loop pass.
     */
    stable_count = READ_ONCE(spi_idle_stable_count);
    poll_delay_us = READ_ONCE(spi_poll_delay_us);
    guard_delay_us = READ_ONCE(spi_idle_guard_delay_us);
    dbg = READ_ONCE(debug);

    if (!mask) {
        if (dbg) {
            pr_warn("wait_spi called with zero mask\n");
        }

        /*
         * Keep compatible behavior.  A zero mask means there is no SPI busy
         * bit to wait for.  Still add a guard delay before the next FPGA BAR
         * access.
         */
        if (guard_delay_us) {
            udelay(guard_delay_us);
        }
        return 0;
    }

    /*
     * Warn if the timeout is too small to ever collect the required run of
     * idle samples.  Cast to unsigned long before the multiply so the product
     * cannot overflow unsigned int.  Only the bare minimum is checked here;
     * extra room for an initial busy time is still recommended.
     */
    if (dbg &&
        timeout_us < (unsigned long)stable_count * poll_delay_us) {
        pr_warn_ratelimited("wait_spi timeout_us=%lu is smaller than stable_count(%u) * poll_delay_us(%u); it may always time out\n",
                            timeout_us, stable_count, poll_delay_us);
    }

    /*
     * Use a ktime based deadline.  jiffies does not advance while local
     * interrupts are disabled (in polling mode this runs inside the
     * process_lock critical section), so a jiffies based timeout could be far
     * too long or, on a UP system, never fire.  ktime keeps advancing here.
     *
     * Keep the start timestamp too. It is used only for debug timeout logs so
     * that stress logs can show how far the call went beyond the requested
     * timeout window.
     */
    start = ktime_get();
    deadline = ktime_add_us(start, timeout_us);
    stable = 0;
    last_read_us = 0;
    max_read_us = 0;

    while (1) {
        /*
         * Measure the BAR0 read latency around the SPI busy register access.
         * This helps identify whether a timeout is related to a slow
         * ioread32()/PCIe completion.
         */
        if (dbg) {
            read_start = ktime_get();
            data = ioread32(spi_busy_reg);
            now = ktime_get();

            last_read_us = ktime_us_delta(now, read_start);
            if (last_read_us > max_read_us) {
                max_read_us = last_read_us;
            }
        } else {
            data = ioread32(spi_busy_reg);
            now = ktime_get();
        }

        /* pr_info("@ %u, Read spi_busy_reg: 0x%08x 0x%08x\n", ri, data, mask); */
        busy = ((data >> 24) & 0xff) & mask;

        /*
         * timeout_us is the deadline for accepting stable-idle samples.  Check
         * the deadline after the BAR0 busy-register read and before counting the
         * current idle sample.  Otherwise stable_count == 1 could return success
         * even if the sample was observed after the timeout window had already
         * expired.
         *
         * The common guard delay is intentionally not included in timeout_us.
         */
        if (ktime_after(now, deadline)) {
            if (dbg) {
                pr_warn("wait_spi timeout: reason=%s, elapsed_us=%lld, "
                        "last_read_us=%lld, max_read_us=%lld, ri=%u, "
                        "data=0x%08x, mask=0x%08x, busy=0x%08x, "
                        "stable=%u/%u, timeout_us=%lu, guard_delay_us=%u\n",
                        busy ? "busy_asserted" : "idle_not_stable_before_timeout",
                        (long long)ktime_us_delta(now, start),
                        (long long)last_read_us,
                        (long long)max_read_us,
                        ri, data, mask, busy, stable, stable_count,
                        timeout_us, guard_delay_us);
            }

            return -ETIMEDOUT;
        }

        if (!busy) {
            stable++;
            if (stable >= stable_count) {
                /*
                 * The busy bit may become idle before the FPGA internal
                 * bridge, CDC path, BAR decoder, or PCIe completion path is
                 * ready.  Add a guard delay before the starting current BAR access.
                 */
                if (guard_delay_us) {
                    udelay(guard_delay_us);
                }
                return 0;
            }
        } else {
            stable = 0;
        }

        /*
         * Do not keep reading the FPGA PCIe endpoint without any delay.  This
         * reduces BAR0 MMIO read rate and gives the busy status time to become
         * stable.
         */
        if (poll_delay_us) {
            udelay(poll_delay_us);
        } else {
            cpu_relax();
        }

        ri++;
    }
}
#else
int wait_spi(u32 mask, unsigned long timeout_us) {
    u32 data;
    u32 ri = 0;
    unsigned long j;

    /* pr_info("CPLD %u, Will time-out at jiffie %lu\n", cpld_id,timeout); */
    if (!spi_busy_reg) {
        return -EFAULT;
    }

    j = jiffies + usecs_to_jiffies(timeout_us);
    while (1) {
        data = ioread32(spi_busy_reg);
        /* pr_info("@ %u, Read spi_busy_reg: 0x%08x 0x%08x\n", ri, data, mask); */
        if (!((( data >> 24) & 0xFF) & mask)) {
            break;
        }

        if (time_after(jiffies, j)) {
            if (debug) {
                pr_warn("@ %u, wait_spi TIMEOUT \n", ri);
            }
            return -ETIMEDOUT;
        }

        ri++;
    }

    return 0;
}
#endif
EXPORT_SYMBOL(wait_spi);

static int wait_cpld(struct ocores_i2c *i2c, unsigned long timeout_us)
{
    struct platform_device *pdev;
    struct device *dev;
    u32 mask;

    if (!i2c->adap.dev.parent) {
        return -EFAULT;
    }

    /* Get SPI Busy mask from pdev->id */
    dev = i2c->adap.dev.parent;
    pdev = container_of(dev, struct platform_device, dev);
    mask = (pdev->id & 0xff00) >> 8;

    return wait_spi(mask, timeout_us);
}

/**
 * oc_setreg_checked - Wait for FPGA ready and write one OpenCores register
 * @i2c: OpenCores I2C adapter data.
 * @reg: OpenCores register offset.
 * @value: Value to write.
 *
 * Return: 0 on success, negative errno on failure.
 */
static int oc_setreg_checked(struct ocores_i2c *i2c, int reg, u8 value)
{
    unsigned int post_write_guard_delay_us;
    int ret;

    ret = wait_cpld(i2c, spi_wait_timeout_us);
    if (ret)
        return ret;

    i2c->setreg(i2c, reg, value);

    /*
     * Some FPGA write paths may need extra time after the BAR write has
     * been issued.  Keep wait_spi() unchanged and apply this guard only
     * after OpenCores register writes.
     */
    post_write_guard_delay_us = READ_ONCE(spi_post_write_guard_delay_us);
    if (post_write_guard_delay_us) {
        udelay(post_write_guard_delay_us);
    }

    return 0;
}

/**
 * oc_getreg_checked - Wait for FPGA ready and read one OpenCores register
 * @i2c: OpenCores I2C adapter data.
 * @reg: OpenCores register offset.
 * @value: Output register value.
 *
 * Return: 0 on success, negative errno on failure.
 */
static int oc_getreg_checked(struct ocores_i2c *i2c, int reg, u8 *value)
{
    int ret;

    ret = wait_cpld(i2c, spi_wait_timeout_us);
    if (ret)
        return ret;

    *value = i2c->getreg(i2c, reg);

    return 0;
}

/**
 * ocores_map_pre_start_error - Map pre-START timeout for i2c-core retry
 * @ret: Original error code.
 * @xfer_started: Whether START command was accepted by the controller.
 *
 * i2c-core retries a transfer only when the adapter returns -EAGAIN and
 * adap->retries is greater than zero.  Use -EAGAIN only before START is sent,
 * because no slave device should have observed this transfer yet.
 *
 * After START is sent, keep the original error.  A STOP may be attempted later
 * as best-effort cleanup, but STOP cannot roll back bytes already accepted by
 * the slave.
 *
 * Return: -EAGAIN for pre-START timeout, otherwise the original error code.
 */
static int ocores_map_pre_start_error(int ret, bool xfer_started)
{
    if (ret == -ETIMEDOUT && !xfer_started)
        return -EAGAIN;

    return ret;
}

/**
 * ocores_set_xfer_error - Save transfer error and wake the waiter
 * @i2c: OpenCores I2C adapter data.
 * @err: Error code to save.
 *
 * The first error is kept so the transfer path can return the original
 * wait_cpld()/wait_spi() error to the I2C core.
 */
static void ocores_set_xfer_error(struct ocores_i2c *i2c, int err)
{
    unsigned long flags;

    spin_lock_irqsave(&i2c->process_lock, flags);
    if (!i2c->xfer_err)
        i2c->xfer_err = err;
    i2c->state = STATE_ERROR;
    spin_unlock_irqrestore(&i2c->process_lock, flags);

    wake_up(&i2c->wait);
}

/**
 * ocores_try_stop_cleanup_locked - Try to send STOP as best-effort cleanup
 * @i2c: OpenCores I2C adapter data.
 *
 * Caller must hold i2c->process_lock.
 *
 * This helper is only a cleanup attempt after the transfer is already in an
 * error path.  STOP may fail because the same FPGA-side wait path is needed
 * before writing OCI2C_CMD.  Therefore, a STOP failure must not be interpreted
 * as successful bus recovery, and it must not cause a post-START error to be
 * converted to -EAGAIN.
 *
 * Return: 0 if STOP command was written, negative errno on failure.
 */
static int ocores_try_stop_cleanup_locked(struct ocores_i2c *i2c)
{
    int ret;

    ret = oc_setreg_checked(i2c, OCI2C_CMD, OCI2C_CMD_STOP);
    if (ret && debug)
        dev_warn(i2c->adap.dev.parent,
             "I2C %s STOP cleanup failed: %d\n",
             i2c->adap.name, ret);

    return ret;
}

static void oc_setreg_8(struct ocores_i2c *i2c, int reg, u8 value)
{
    iowrite8(value, i2c->base + (reg << i2c->reg_shift));
}

static void oc_setreg_16(struct ocores_i2c *i2c, int reg, u8 value)
{
    iowrite16(value, i2c->base + (reg << i2c->reg_shift));
}

static void oc_setreg_32(struct ocores_i2c *i2c, int reg, u8 value)
{
    iowrite32(value, i2c->base + (reg << i2c->reg_shift));
}

static void oc_setreg_16be(struct ocores_i2c *i2c, int reg, u8 value)
{
    iowrite16be(value, i2c->base + (reg << i2c->reg_shift));
}

static void oc_setreg_32be(struct ocores_i2c *i2c, int reg, u8 value)
{
    iowrite32be(value, i2c->base + (reg << i2c->reg_shift));
}

static inline u8 oc_getreg_8(struct ocores_i2c *i2c, int reg)
{
    return ioread8(i2c->base + (reg << i2c->reg_shift));
}

static inline u8 oc_getreg_16(struct ocores_i2c *i2c, int reg)
{
    return ioread16(i2c->base + (reg << i2c->reg_shift));
}

static inline u8 oc_getreg_32(struct ocores_i2c *i2c, int reg)
{
    return ioread32(i2c->base + (reg << i2c->reg_shift));
}

static inline u8 oc_getreg_16be(struct ocores_i2c *i2c, int reg)
{
    return ioread16be(i2c->base + (reg << i2c->reg_shift));
}

static inline u8 oc_getreg_32be(struct ocores_i2c *i2c, int reg)
{
    return ioread32be(i2c->base + (reg << i2c->reg_shift));
}

static void oc_setreg_io_8(struct ocores_i2c *i2c, int reg, u8 value)
{
    outb(value, i2c->iobase + reg);
}

static inline u8 oc_getreg_io_8(struct ocores_i2c *i2c, int reg)
{
    return inb(i2c->iobase + reg);
}

#if 0
/*
 * Keep the old unchecked wrappers temporarily for comparison only.
 *
 * These wrappers ignore the return value from wait_cpld(), so they must not be
 * used by the normal access path.  All register accesses should go through
 * oc_setreg_checked() or oc_getreg_checked() to propagate wait_spi() timeout.
 */
static inline void oc_setreg(struct ocores_i2c *i2c, int reg, u8 value)
{
    wait_cpld(i2c, spi_wait_timeout_us);
    i2c->setreg(i2c, reg, value);
}

static inline u8 oc_getreg(struct ocores_i2c *i2c, int reg)
{
    wait_cpld(i2c, spi_wait_timeout_us);
    return i2c->getreg(i2c, reg);
}
#endif

static int ocores_process(struct ocores_i2c *i2c, u8 stat)
{
    struct i2c_msg *msg = i2c->msg;
    unsigned long flags;
    struct device *dev = i2c->adap.dev.parent;
    u8 data;
    int ret = 0;

    /*
     * If we spin here is because we are in timeout, so we are going
     * to be in STATE_ERROR. See ocores_process_timeout()
     */
    spin_lock_irqsave(&i2c->process_lock, flags);
    if ((i2c->state == STATE_DONE) || (i2c->state == STATE_ERROR)) {
        /* stop has been sent */
        ret = oc_setreg_checked(i2c, OCI2C_CMD, OCI2C_CMD_IACK);
        if (ret)
            goto err;
        wake_up(&i2c->wait);
        goto out;
    }

    /* error? */
    if (stat & OCI2C_STAT_ARBLOST) {
        i2c->state = STATE_ERROR;
        if (debug) {
            dev_warn(dev, "I2C %s arbitration lost", i2c->adap.name);
        }
        ret = ocores_try_stop_cleanup_locked(i2c);
        if (ret)
            goto err;
        goto out;
    }

    if ((i2c->state == STATE_START) || (i2c->state == STATE_WRITE)) {
        i2c->state =
            (msg->flags & I2C_M_RD) ? STATE_READ : STATE_WRITE;

        if (stat & OCI2C_STAT_NACK) {
            i2c->state = STATE_ERROR;
            if (debug) {
                dev_warn(dev, "I2C %s, no ACK from slave 0x%02x",
             i2c->adap.name, msg->addr);
            }
            ret = ocores_try_stop_cleanup_locked(i2c);
            if (ret)
                goto err;
            goto out;
        }
    } else {
        ret = oc_getreg_checked(i2c, OCI2C_DATA, &data);
        if (ret)
            goto err;
        msg->buf[i2c->pos++] = data;
    }

    /* end of msg? */
    if (i2c->pos == msg->len) {
        i2c->nmsgs--;
        i2c->msg++;
        i2c->pos = 0;
        msg = i2c->msg;

        if (i2c->nmsgs) {	/* end? */
            /* send start? */
            if (!(msg->flags & I2C_M_NOSTART)) {
                u8 addr = i2c_8bit_addr_from_msg(msg);

                i2c->state = STATE_START;

                ret = oc_setreg_checked(i2c, OCI2C_DATA, addr);
                if (ret)
                    goto err;
                ret = oc_setreg_checked(i2c, OCI2C_CMD, OCI2C_CMD_START);
                if (ret)
                    goto err;
                goto out;
            }
            i2c->state = (msg->flags & I2C_M_RD)
                         ? STATE_READ : STATE_WRITE;
        } else {
            i2c->state = STATE_DONE;
            ret = ocores_try_stop_cleanup_locked(i2c);
            if (ret)
                goto err;
            goto out;
        }
    }

    if (i2c->state == STATE_READ) {
        ret = oc_setreg_checked(i2c, OCI2C_CMD,
                    i2c->pos == (msg->len - 1) ?
                    OCI2C_CMD_READ_NACK :
                    OCI2C_CMD_READ_ACK);
        if (ret)
            goto err;
    } else {
        ret = oc_setreg_checked(i2c, OCI2C_DATA, msg->buf[i2c->pos++]);
        if (ret)
            goto err;
        ret = oc_setreg_checked(i2c, OCI2C_CMD, OCI2C_CMD_WRITE);
        if (ret)
            goto err;
    }

out:
    spin_unlock_irqrestore(&i2c->process_lock, flags);
    return ret;

err:
    if (!i2c->xfer_err)
        i2c->xfer_err = ret;
    i2c->state = STATE_ERROR;
    wake_up(&i2c->wait);
    goto out;
}

static irqreturn_t ocores_isr(int irq, void *dev_id)
{
    struct ocores_i2c *i2c = dev_id;
    u8 stat;
    int ret;

    ret = oc_getreg_checked(i2c, OCI2C_STATUS, &stat);
    if (ret) {
        ocores_set_xfer_error(i2c, ret);
        return IRQ_HANDLED;
    }

    if (i2c->flags & OCORES_FLAG_BROKEN_IRQ) {
        if ((stat & OCI2C_STAT_IF) && !(stat & OCI2C_STAT_BUSY))
            return IRQ_NONE;
    } else if (!(stat & OCI2C_STAT_IF)) {
        return IRQ_NONE;
    }

    ret = ocores_process(i2c, stat);
    if (ret)
        return IRQ_HANDLED;

    return IRQ_HANDLED;
}

/**
 * Process timeout event
 * @i2c: ocores I2C device instance
 */
static void ocores_process_timeout(struct ocores_i2c *i2c)
{
    unsigned long flags;
    int stop_ret;

    spin_lock_irqsave(&i2c->process_lock, flags);
    i2c->state = STATE_ERROR;
    stop_ret = ocores_try_stop_cleanup_locked(i2c);
    if (stop_ret && !i2c->xfer_err) {
        /*
         * This path is normally used after the transfer has already
         * started.  STOP is only best-effort cleanup.  Save the STOP
         * failure only if no earlier error has been recorded.
         */
        i2c->xfer_err = stop_ret;
    }
    spin_unlock_irqrestore(&i2c->process_lock, flags);
}

/**
 * Wait until something change in a given register
 * @i2c: ocores I2C device instance
 * @reg: register to query
 * @mask: bitmask to apply on register value
 * @val: expected result
 * @timeout: timeout in jiffies
 *
 * Timeout is necessary to avoid to stay here forever when the chip
 * does not answer correctly.
 *
 * Return: 0 on success, -ETIMEDOUT on timeout
 */
static int ocores_wait(struct ocores_i2c *i2c,
                       int reg, u8 mask, u8 val,
                       const unsigned long timeout)
{
    unsigned long j;
    int ret;

    j = jiffies + timeout;
    while (1) {
        u8 status;

        ret = oc_getreg_checked(i2c, reg, &status);
        if (ret)
            return ret;

        if ((status & mask) == val)
            break;

        if (time_after(jiffies, j))
            return -ETIMEDOUT;
    }
    return 0;
}

/**
 * Wait until is possible to process some data
 * @i2c: ocores I2C device instance
 *
 * Used when the device is in polling mode (interrupts disabled).
 *
 * Return: 0 on success, -ETIMEDOUT on timeout
 */
static int ocores_poll_wait(struct ocores_i2c *i2c)
{
    u8 mask;
    int err;

    if (i2c->state == STATE_DONE || i2c->state == STATE_ERROR) {
        /* transfer is over */
        mask = OCI2C_STAT_BUSY;
    } else {
        /* on going transfer */
        mask = OCI2C_STAT_TIP;
        /*
         * We wait for the data to be transferred (8bit),
         * then we start polling on the ACK/NACK bit
         */
        udelay((8 * 1000) / i2c->bus_clock_khz);
    }

    /*
     * once we are here we expect to get the expected result immediately
     * so if after 1ms we timeout then something is broken.
     */
    err = ocores_wait(i2c, OCI2C_STATUS, mask, 0, msecs_to_jiffies(timeout));
    if (err) {
        if (debug) {
            dev_warn(i2c->adap.dev.parent,
                     "%s: STATUS timeout, bit 0x%x did not clear in %ums(msecs_to_jiffies(%u)=%lu)\n",
                     __func__, mask, timeout, timeout, msecs_to_jiffies(timeout));
        }
    }
    return err;
}

/**
 * It handles an IRQ-less transfer
 * @i2c: ocores I2C device instance
 *
 * Even if IRQ are disabled, the I2C OpenCore IP behavior is exactly the same
 * (only that IRQ are not produced). This means that we can re-use entirely
 * ocores_isr(), we just add our polling code around it.
 *
 * It can run in atomic context
 *
 * Return: 0 on success, -ETIMEDOUT on timeout
 */
static int ocores_process_polling(struct ocores_i2c *i2c)
{
    irqreturn_t ret;
    int err;

    while (1) {
        err = ocores_poll_wait(i2c);
        if (err) {
            break; /* timeout */
        }

        ret = ocores_isr(-1, i2c);
        if (i2c->xfer_err)
            return i2c->xfer_err;

        if (ret == IRQ_NONE)
            break; /* all messages have been transferred */
        else {
            if (i2c->flags & OCORES_FLAG_BROKEN_IRQ)
                if (i2c->state == STATE_DONE)
                    break;
        }
    }

    return err;
}

static int ocores_xfer_core(struct ocores_i2c *i2c,
                            struct i2c_msg *msgs, int num,
                            bool polling)
{
    int ret = 0;
    bool xfer_started = false;
    u8 ctrl;

    LOCK(&cpld_access_lock);

    i2c->xfer_err = 0;

    ret = oc_getreg_checked(i2c, OCI2C_CONTROL, &ctrl);
    if (ret) {
        ret = ocores_map_pre_start_error(ret, xfer_started);
        goto out_unlock;
    }

    if (polling) {
        ret = oc_setreg_checked(i2c, OCI2C_CONTROL,
                    ctrl & ~OCI2C_CTRL_IEN);
    } else {
        ret = oc_setreg_checked(i2c, OCI2C_CONTROL,
                    ctrl | OCI2C_CTRL_IEN);
    }
    if (ret) {
        ret = ocores_map_pre_start_error(ret, xfer_started);
        goto out_unlock;
    }

    i2c->msg = msgs;
    i2c->pos = 0;
    i2c->nmsgs = num;
    i2c->state = STATE_START;

    ret = oc_setreg_checked(i2c, OCI2C_DATA,
                i2c_8bit_addr_from_msg(i2c->msg));
    if (ret) {
        ret = ocores_map_pre_start_error(ret, xfer_started);
        goto out_unlock;
    }

    ret = oc_setreg_checked(i2c, OCI2C_CMD, OCI2C_CMD_START);
    if (ret) {
        ret = ocores_map_pre_start_error(ret, xfer_started);
        goto out_unlock;
    }

    /*
     * START command was accepted by the controller from this point.
     * Later errors remain as their original errno.  Do not map them to
     * -EAGAIN because i2c-core would retry the whole transfer, and the
     * slave may already have seen address or data bytes.
     */
    xfer_started = true;

    if (polling) {
        ret = ocores_process_polling(i2c);
    } else {
        if (wait_event_timeout(i2c->wait,
                               (i2c->state == STATE_ERROR) ||
                               (i2c->state == STATE_DONE), HZ) == 0)
            ret = -ETIMEDOUT;
        else if (i2c->xfer_err)
            ret = i2c->xfer_err;
    }
    if (ret) {
        if (xfer_started) {
            /*
             * Best-effort cleanup only.  STOP may also fail when
             * FPGA wait is still timing out.  Keep the original
             * transfer error and do not request an i2c-core retry.
             */
            ocores_process_timeout(i2c);
        }
        goto out_unlock;
    }

    ret = (i2c->state == STATE_DONE) ? num : -EIO;

out_unlock:
    UNLOCK(&cpld_access_lock);
    return ret;
}

static int ocores_xfer_polling(struct i2c_adapter *adap,
                               struct i2c_msg *msgs, int num)
{
    return ocores_xfer_core(i2c_get_adapdata(adap), msgs, num, true);
}

static int ocores_xfer(struct i2c_adapter *adap,
                       struct i2c_msg *msgs, int num)
{
    return ocores_xfer_core(i2c_get_adapdata(adap), msgs, num, false);
}

static int ocores_init(struct device *dev, struct ocores_i2c *i2c)
{
    struct device *org;
    int prescale;
    int diff;
    int ret;
    u8 ctrl;

    /*
     * Temporary assignment for checking SPI busy status.
     *
     * The AS9817 FPGA SPI busy wait gets the SPI busy mask from the parent
     * platform device ID.  During probe, the adapter is not added to i2c-core
     * yet, so set the parent here before checked register access.
     */
    org = i2c->adap.dev.parent;
    i2c->adap.dev.parent = dev;

    LOCK(&cpld_access_lock);

    ret = oc_getreg_checked(i2c, OCI2C_CONTROL, &ctrl);
    if (ret) {
        goto out_unlock;
    }

    /* Make sure the device is disabled before updating prescale registers. */
    ctrl &= ~(OCI2C_CTRL_EN | OCI2C_CTRL_IEN);
    ret = oc_setreg_checked(i2c, OCI2C_CONTROL, ctrl);
    if (ret) {
        goto out_unlock;
    }

    UNLOCK(&cpld_access_lock);

    prescale = (i2c->ip_clock_khz / (5 * i2c->bus_clock_khz)) - 1;
    prescale = clamp(prescale, 0, 0xffff);

    diff = i2c->ip_clock_khz / (5 * (prescale + 1)) - i2c->bus_clock_khz;
    if (abs(diff) > i2c->bus_clock_khz / 10) {
        i2c->adap.dev.parent = org;
        dev_err(dev,
                "Unsupported clock settings: core: %d KHz, bus: %d KHz\n",
                i2c->ip_clock_khz, i2c->bus_clock_khz);
        return -EINVAL;
    }

    dev_info(dev, "OCI2C_PRELOW=0x%02x OCI2C_PREHIGH=0x%02x\n",
                  prescale & 0xff, prescale >> 8);
    LOCK(&cpld_access_lock);

    ret = oc_setreg_checked(i2c, OCI2C_PRELOW, prescale & 0xff);
    if (ret) {
        goto out_unlock;
    }

    ret = oc_setreg_checked(i2c, OCI2C_PREHIGH, prescale >> 8);
    if (ret) {
        goto out_unlock;
    }

    /* Init the device. */
    ret = oc_setreg_checked(i2c, OCI2C_CMD, OCI2C_CMD_IACK);
    if (ret) {
        goto out_unlock;
    }

    ret = oc_setreg_checked(i2c, OCI2C_CONTROL, ctrl | OCI2C_CTRL_EN);

out_unlock:
    UNLOCK(&cpld_access_lock);
    i2c->adap.dev.parent = org;

    return ret;
}

/**
 * ocores_bus_clock_to_prescale - Convert runtime bus clock to prescale bytes
 * @bus_clock_khz: requested I2C bus clock in KHz
 * @prelow: PRELOW register value
 * @prehigh: PREHIGH register value
 *
 * Return: 0 on success, negative errno on failure.
 */
static int ocores_bus_clock_to_prescale(unsigned int bus_clock_khz,
                                        u8 *prelow, u8 *prehigh)
{
    switch (bus_clock_khz) {
    case 100:
        *prelow = 0x2f;
        *prehigh = 0x00;
        break;
    case 400:
        *prelow = 0x0b;
        *prehigh = 0x00;
        break;
    default:
        return -EINVAL;
    }

    return 0;
}

/**
 * ocores_prescale_to_ip_clock - Reverse calculate OpenCores input clock
 * @bus_clock_khz: requested I2C bus clock in KHz
 * @prelow: PRELOW register value
 * @prehigh: PREHIGH register value
 *
 * Return: OpenCores input clock in KHz.
 */
static unsigned int ocores_prescale_to_ip_clock(unsigned int bus_clock_khz,
                                                u8 prelow, u8 prehigh)
{
    unsigned int prescale;

    prescale = prelow | (((unsigned int)prehigh) << 8);

    return bus_clock_khz * 5 * (prescale + 1);
}

static ssize_t bus_clock_khz_show(struct device *dev,
                                  struct device_attribute *attr,
                                  char *buf)
{
    struct ocores_i2c *i2c = dev_get_drvdata(dev);

    if (!i2c) {
        return -ENODEV;
    }

    return sprintf(buf, "%d\n", i2c->bus_clock_khz);
}

static int ocores_set_bus_clock_khz(struct device *dev,
                                    struct ocores_i2c *i2c,
                                    unsigned int bus_clock_khz)
{
    unsigned long flags;
    unsigned int ip_clock_khz;
    u8 prelow;
    u8 prehigh;
    u8 status;
    u8 ctrl;
    int ret;

    ret = ocores_bus_clock_to_prescale(bus_clock_khz, &prelow, &prehigh);
    if (ret) {
        dev_err(dev, "Unsupported I2C bus clock: %u KHz\n",
                bus_clock_khz);
        return ret;
    }

    ip_clock_khz = ocores_prescale_to_ip_clock(bus_clock_khz,
                                               prelow, prehigh);

    /*
     * Prevent new adapter-level transfers from entering this controller while
     * the prescale registers are being changed.
     *
     * The I2C core serializes a complete i2c_transfer()/SMBus operation here,
     * not each byte handled by ocores_process(). After this lock is held, no
     * new complete transfer can start on this adapter.
     */
    i2c_lock_bus(&i2c->adap, I2C_LOCK_ROOT_ADAPTER);

    /*
     * Serialize against all other FPGA BAR access (other adapters and the
     * FPGA sysfs driver) on the shared SPI path.  cpld_access_lock is the
     * global FPGA lock; process_lock below is per-adapter only, so it is not
     * enough on its own.  Take cpld_access_lock outside process_lock to match
     * the transfer path lock order in ocores_xfer_core().
     */
    LOCK(&cpld_access_lock);

    /*
     * Try to wait until the controller becomes idle before changing the
     * prescale registers. If this times out, keep going because this sysfs
     * operation is treated as a forced controller re-init:
     *
     *   disable controller -> update PRELOW/PREHIGH -> enable controller
     *
     * A timeout here usually means the previous adapter-level transfer has
     * already left the I2C core path, but the controller, slave, or bus is
     * still stuck in BUSY/TIP.
     */
    ret = ocores_wait(i2c, OCI2C_STATUS,
                      OCI2C_STAT_BUSY | OCI2C_STAT_TIP, 0,
                      msecs_to_jiffies(timeout));
    if (ret) {
        dev_warn(dev,
                 "Controller is busy, force re-init while changing I2C bus clock\n");
    }

    /*
     * Synchronize with the byte-level OpenCores state machine.
     *
     * ocores_process() advances one step of the current transfer from the IRQ
     * or polling path. It may update i2c->state and touch OCI2C_DATA/CMD.
     * Hold process_lock while forcing the controller re-init so that the
     * prescale update does not race with an in-flight state-machine step.
     */
    spin_lock_irqsave(&i2c->process_lock, flags);

    if (i2c->state != STATE_DONE && i2c->state != STATE_ERROR) {
        dev_warn(dev,
                 "Force I2C state from %d to error while changing bus clock\n",
                 i2c->state);
        i2c->state = STATE_ERROR;
        wake_up(&i2c->wait);
    }

    /*
     * Re-check the hardware status after process_lock is held. This is only a
     * diagnostic check because the controller will be disabled below anyway.
     */
    ret = oc_getreg_checked(i2c, OCI2C_STATUS, &status);
    if (ret) {
        dev_warn(dev,
                 "Failed to read controller status before forced bus clock update: %d\n",
                 ret);
        goto out_unlock;
    }

    if (status & (OCI2C_STAT_BUSY | OCI2C_STAT_TIP)) {
        dev_warn(dev,
                 "Controller status is 0x%02x before forced bus clock update\n",
                 status);
    }

    ret = oc_getreg_checked(i2c, OCI2C_CONTROL, &ctrl);
    if (ret) {
        dev_warn(dev,
                 "Failed to read control register while changing bus clock: %d\n",
                 ret);
        goto out_unlock;
    }

    /*
     * Update prescale while the I2C core is disabled. Restore the previous
     * control value after PRELOW/PREHIGH are updated.
     */
    ret = oc_setreg_checked(i2c, OCI2C_CONTROL,
                            ctrl & ~(OCI2C_CTRL_EN | OCI2C_CTRL_IEN));
    if (ret) {
        goto out_unlock;
    }

    ret = oc_setreg_checked(i2c, OCI2C_PRELOW, prelow);
    if (ret) {
        goto out_unlock;
    }

    ret = oc_setreg_checked(i2c, OCI2C_PREHIGH, prehigh);
    if (ret) {
        goto out_unlock;
    }

    i2c->bus_clock_khz = bus_clock_khz;
    i2c->ip_clock_khz = ip_clock_khz;

    ret = oc_setreg_checked(i2c, OCI2C_CONTROL, ctrl);
    if (ret) {
        goto out_unlock;
    }

    if (ctrl & OCI2C_CTRL_EN) {
        ret = oc_setreg_checked(i2c, OCI2C_CMD, OCI2C_CMD_IACK);
        if (ret) {
            goto out_unlock;
        }
    }

out_unlock:
    spin_unlock_irqrestore(&i2c->process_lock, flags);
    UNLOCK(&cpld_access_lock);
    i2c_unlock_bus(&i2c->adap, I2C_LOCK_ROOT_ADAPTER);

    if (ret) {
        dev_warn(dev,
                 "Failed to set I2C bus clock to %u KHz: %d\n",
                 bus_clock_khz, ret);
        return ret;
    }

    dev_info(dev,
             "Set I2C bus clock to %u KHz, ip clock to %u KHz, OCI2C_PRELOW=0x%02x OCI2C_PREHIGH=0x%02x\n",
             bus_clock_khz, ip_clock_khz, prelow, prehigh);

    return 0;
}

static ssize_t bus_clock_khz_store(struct device *dev,
                                   struct device_attribute *attr,
                                   const char *buf, size_t count)
{
    struct ocores_i2c *i2c = dev_get_drvdata(dev);
    unsigned int bus_clock_khz;
    int ret;

    if (!i2c) {
        return -ENODEV;
    }

    ret = kstrtouint(buf, 0, &bus_clock_khz);
    if (ret) {
        return ret;
    }

    ret = ocores_set_bus_clock_khz(dev, i2c, bus_clock_khz);
    if (ret) {
        return ret;
    }

    return count;
}

static DEVICE_ATTR_RW(bus_clock_khz);

static struct attribute *ocores_i2c_attrs[] = {
    &dev_attr_bus_clock_khz.attr,
    NULL
};

static const struct attribute_group ocores_i2c_attr_group = {
    .attrs = ocores_i2c_attrs,
};

static u32 ocores_func(struct i2c_adapter *adap)
{
    return I2C_FUNC_I2C | I2C_FUNC_SMBUS_EMUL;
}

static struct i2c_algorithm ocores_algorithm = {
    .master_xfer = ocores_xfer,
    .master_xfer_atomic = ocores_xfer_polling,
    .functionality = ocores_func,
};

static const struct i2c_adapter ocores_adapter = {
    .owner = THIS_MODULE,
    .name = "i2c-ocores",
    .class = I2C_CLASS_DEPRECATED,
    .algo = &ocores_algorithm,
};

static const struct of_device_id ocores_i2c_match[] = {
    {
        .compatible = "opencores,i2c-ocores",
        .data = (void *)TYPE_OCORES,
    },
    {
        .compatible = "aeroflexgaisler,i2cmst",
        .data = (void *)TYPE_GRLIB,
    },
    {
        .compatible = "sifive,fu540-c000-i2c",
        .data = (void *)TYPE_SIFIVE_REV0,
    },
    {
        .compatible = "sifive,i2c0",
        .data = (void *)TYPE_SIFIVE_REV0,
    },
    {},
};
MODULE_DEVICE_TABLE(of, ocores_i2c_match);

#ifdef CONFIG_OF
/*
 * Read and write functions for the GRLIB port of the controller. Registers are
 * 32-bit big endian and the PRELOW and PREHIGH registers are merged into one
 * register. The subsequent registers have their offsets decreased accordingly.
 */
static u8 oc_getreg_grlib(struct ocores_i2c *i2c, int reg)
{
    u32 rd;
    int rreg = reg;

    if (reg != OCI2C_PRELOW)
        rreg--;
    rd = ioread32be(i2c->base + (rreg << i2c->reg_shift));
    if (reg == OCI2C_PREHIGH)
        return (u8)(rd >> 8);
    else
        return (u8)rd;
}

static void oc_setreg_grlib(struct ocores_i2c *i2c, int reg, u8 value)
{
    u32 curr, wr;
    int rreg = reg;

    if (reg != OCI2C_PRELOW)
        rreg--;
    if (reg == OCI2C_PRELOW || reg == OCI2C_PREHIGH) {
        curr = ioread32be(i2c->base + (rreg << i2c->reg_shift));
        if (reg == OCI2C_PRELOW)
            wr = (curr & 0xff00) | value;
        else
            wr = (((u32)value) << 8) | (curr & 0xff);
    } else {
        wr = value;
    }
    iowrite32be(wr, i2c->base + (rreg << i2c->reg_shift));
}

static int ocores_i2c_of_probe(struct platform_device *pdev,
                               struct ocores_i2c *i2c)
{
    struct device_node *np = pdev->dev.of_node;
    const struct of_device_id *match;
    u32 val;
    u32 clock_frequency;
    bool clock_frequency_present;

    if (of_property_read_u32(np, "reg-shift", &i2c->reg_shift)) {
        /* no 'reg-shift', check for deprecated 'regstep' */
        if (!of_property_read_u32(np, "regstep", &val)) {
            if (!is_power_of_2(val)) {
                dev_err(&pdev->dev, "invalid regstep %d\n",
                        val);
                return -EINVAL;
            }
            i2c->reg_shift = ilog2(val);
            dev_warn(&pdev->dev,
                     "regstep property deprecated, use reg-shift\n");
        }
    }

    clock_frequency_present = !of_property_read_u32(np, "clock-frequency",
                              &clock_frequency);
    i2c->bus_clock_khz = 100;

    i2c->clk = devm_clk_get(&pdev->dev, NULL);

    if (!IS_ERR(i2c->clk)) {
        int ret = clk_prepare_enable(i2c->clk);

        if (ret) {
            dev_err(&pdev->dev,
                    "clk_prepare_enable failed: %d\n", ret);
            return ret;
        }
        i2c->ip_clock_khz = clk_get_rate(i2c->clk) / 1000;
        if (clock_frequency_present)
            i2c->bus_clock_khz = clock_frequency / 1000;
    }

    if (i2c->ip_clock_khz == 0) {
        if (of_property_read_u32(np, "opencores,ip-clock-frequency",
                                 &val)) {
            if (!clock_frequency_present) {
                dev_err(&pdev->dev,
                        "Missing required parameter 'opencores,ip-clock-frequency'\n");
                clk_disable_unprepare(i2c->clk);
                return -ENODEV;
            }
            i2c->ip_clock_khz = clock_frequency / 1000;
            dev_warn(&pdev->dev,
                     "Deprecated usage of the 'clock-frequency' property, please update to 'opencores,ip-clock-frequency'\n");
        } else {
            i2c->ip_clock_khz = val / 1000;
            if (clock_frequency_present)
                i2c->bus_clock_khz = clock_frequency / 1000;
        }
    }

    of_property_read_u32(pdev->dev.of_node, "reg-io-width",
                         &i2c->reg_io_width);

    match = of_match_node(ocores_i2c_match, pdev->dev.of_node);
    if (match && (long)match->data == TYPE_GRLIB) {
        dev_dbg(&pdev->dev, "GRLIB variant of i2c-ocores\n");
        i2c->setreg = oc_setreg_grlib;
        i2c->getreg = oc_getreg_grlib;
    }

    return 0;
}
#else
#define ocores_i2c_of_probe(pdev, i2c) -ENODEV
#endif

static int ocores_i2c_probe(struct platform_device *pdev)
{
    struct ocores_i2c *i2c;
    struct ocores_i2c_platform_data *pdata;
    const struct of_device_id *match;
    struct resource *res;
    int irq;
    int ret;
    int i;

    i2c = devm_kzalloc(&pdev->dev, sizeof(*i2c), GFP_KERNEL);
    if (!i2c)
        return -ENOMEM;

    spin_lock_init(&i2c->process_lock);

    res = platform_get_resource(pdev, IORESOURCE_MEM, 0);
    if (res) {
        i2c->base = devm_ioremap_resource(&pdev->dev, res);
        dev_info(&pdev->dev, "Resouce start:0x%llx, end:0x%llx", res->start, res->end);
        if (IS_ERR(i2c->base))
            return PTR_ERR(i2c->base);
    } else {
        res = platform_get_resource(pdev, IORESOURCE_IO, 0);
        if (!res)
            return -EINVAL;
        i2c->iobase = res->start;
        if (!devm_request_region(&pdev->dev, res->start,
                                 resource_size(res),
                                 pdev->name)) {
            dev_err(&pdev->dev, "Can't get I/O resource.\n");
            return -EBUSY;
        }
        i2c->setreg = oc_setreg_io_8;
        i2c->getreg = oc_getreg_io_8;
    }

    pdata = dev_get_platdata(&pdev->dev);
    if (pdata) {
        i2c->reg_shift = pdata->reg_shift;
        i2c->reg_io_width = pdata->reg_io_width;
        i2c->ip_clock_khz = pdata->clock_khz;
        dev_info(&pdev->dev, "Write %d KHz, ioWidth:%d, shift:%d", i2c->ip_clock_khz, pdata->reg_io_width ,pdata->reg_shift);
        if (pdata->bus_khz)
            i2c->bus_clock_khz = pdata->bus_khz;
        else
            i2c->bus_clock_khz = 100;
    } else {
        ret = ocores_i2c_of_probe(pdev, i2c);
        if (ret)
            return ret;
    }

    if (i2c->reg_io_width == 0)
        i2c->reg_io_width = 1; /* Set to default value */

    if (!i2c->setreg || !i2c->getreg) {
        bool be = pdata ? pdata->big_endian :
                  of_device_is_big_endian(pdev->dev.of_node);

        switch (i2c->reg_io_width) {
        case 1:
            i2c->setreg = oc_setreg_8;
            i2c->getreg = oc_getreg_8;
            break;

        case 2:
            i2c->setreg = be ? oc_setreg_16be : oc_setreg_16;
            i2c->getreg = be ? oc_getreg_16be : oc_getreg_16;
            break;

        case 4:
            i2c->setreg = be ? oc_setreg_32be : oc_setreg_32;
            i2c->getreg = be ? oc_getreg_32be : oc_getreg_32;
            break;

        default:
            dev_err(&pdev->dev, "Unsupported I/O width (%d)\n",
                    i2c->reg_io_width);
            ret = -EINVAL;
            goto err_clk;
        }
    }

    init_waitqueue_head(&i2c->wait);

    irq = platform_get_irq_optional(pdev, 0);
    if (irq == -ENXIO) {
        ocores_algorithm.master_xfer = ocores_xfer_polling;

        /*
         * Set in OCORES_FLAG_BROKEN_IRQ to enable workaround for
         * FU540-C000 SoC in polling mode.
         */
        match = of_match_node(ocores_i2c_match, pdev->dev.of_node);
        if (match && (long)match->data == TYPE_SIFIVE_REV0)
            i2c->flags |= OCORES_FLAG_BROKEN_IRQ;
    } else {
        if (irq < 0)
            return irq;
    }

    if (ocores_algorithm.master_xfer != ocores_xfer_polling) {
        ret = devm_request_any_context_irq(&pdev->dev, irq,
                                           ocores_isr, 0,
                                           pdev->name, i2c);
        if (ret) {
            dev_err(&pdev->dev, "Cannot claim IRQ\n");
            goto err_clk;
        }
    }
    ret = ocores_init(&pdev->dev, i2c);
    if (ret) {
        goto err_clk;
    }
    /* hook up driver to tree */
    platform_set_drvdata(pdev, i2c);
    i2c->adap = ocores_adapter;
    i2c_set_adapdata(&i2c->adap, i2c);
    i2c->adap.dev.parent = &pdev->dev;
    i2c->adap.dev.of_node = pdev->dev.of_node;

    /*
     * i2c-core retries a transfer only when the adapter returns -EAGAIN.
     * This driver returns -EAGAIN only for wait_cpld() timeout before the
     * START command is accepted.
     */
    i2c->adap.retries = 1;

    /* add i2c adapter to i2c tree */
    ret = i2c_add_adapter(&i2c->adap);
    if (ret) {
        goto err_clk;
    }

    ret = sysfs_create_group(&i2c->adap.dev.kobj,
                             &ocores_i2c_attr_group);
    if (ret) {
        dev_err(&pdev->dev, "Failed to create sysfs group: %d\n", ret);
        goto err_del_adapter;
    }

    /* add in known devices to the bus */
    if (pdata) {
        for (i = 0; i < pdata->num_devices; i++){
            i2c_new_client_device(&i2c->adap, pdata->devices + i);
        }
    }

    return 0;

err_del_adapter:
    i2c_del_adapter(&i2c->adap);
err_clk:
    clk_disable_unprepare(i2c->clk);
    return ret;
}

static int ocores_i2c_remove(struct platform_device *pdev)
{
    struct ocores_i2c *i2c = platform_get_drvdata(pdev);
    u8 ctrl;
    int ret;

    sysfs_remove_group(&i2c->adap.dev.kobj, &ocores_i2c_attr_group);

    LOCK(&cpld_access_lock);

    ret = oc_getreg_checked(i2c, OCI2C_CONTROL, &ctrl);
    if (ret) {
        dev_warn(&pdev->dev,
                 "Failed to read control register during remove: %d\n",
                 ret);
        goto out_unlock;
    }

    /* Disable I2C logic. */
    ctrl &= ~(OCI2C_CTRL_EN | OCI2C_CTRL_IEN);
    ret = oc_setreg_checked(i2c, OCI2C_CONTROL, ctrl);
    if (ret) {
        dev_warn(&pdev->dev,
                 "Failed to disable controller during remove: %d\n",
                 ret);
    }

out_unlock:
    UNLOCK(&cpld_access_lock);

    /* Remove adapter and data even if controller cleanup failed. */
    i2c_del_adapter(&i2c->adap);

    if (!IS_ERR(i2c->clk)) {
        clk_disable_unprepare(i2c->clk);
    }

    return 0;
}

#ifdef CONFIG_PM_SLEEP
static int ocores_i2c_suspend(struct device *dev)
{
    struct ocores_i2c *i2c = dev_get_drvdata(dev);
    u8 ctrl;
    int ret;

    LOCK(&cpld_access_lock);

    ret = oc_getreg_checked(i2c, OCI2C_CONTROL, &ctrl);
    if (ret) {
        UNLOCK(&cpld_access_lock);
        return ret;
    }

    /* Make sure the device is disabled. */
    ctrl &= ~(OCI2C_CTRL_EN | OCI2C_CTRL_IEN);
    ret = oc_setreg_checked(i2c, OCI2C_CONTROL, ctrl);
    UNLOCK(&cpld_access_lock);
    if (ret) {
        return ret;
    }

    if (!IS_ERR(i2c->clk)) {
        clk_disable_unprepare(i2c->clk);
    }

    return 0;
}

static int ocores_i2c_resume(struct device *dev)
{
    struct ocores_i2c *i2c = dev_get_drvdata(dev);

    if (!IS_ERR(i2c->clk)) {
        unsigned long rate;
        int ret = clk_prepare_enable(i2c->clk);

        if (ret) {
            dev_err(dev,
                    "clk_prepare_enable failed: %d\n", ret);
            return ret;
        }
        rate = clk_get_rate(i2c->clk) / 1000;
        if (rate) {
            i2c->ip_clock_khz = rate;
        }
    }
    return ocores_init(dev, i2c);
}

static SIMPLE_DEV_PM_OPS(ocores_i2c_pm, ocores_i2c_suspend, ocores_i2c_resume);
#define OCORES_I2C_PM	(&ocores_i2c_pm)
#else
#define OCORES_I2C_PM	NULL
#endif

static struct platform_driver ocores_i2c_driver = {
    .probe   = ocores_i2c_probe,
    .remove  = ocores_i2c_remove,
    .driver  = {
        .name = "ocores-i2c",
        .of_match_table = ocores_i2c_match,
        .pm = OCORES_I2C_PM,
    },
};

#if 0
module_platform_driver(ocores_i2c_driver);
#else
static int __init ocores_i2c_as9817_64_init(void)
{
    int err;

    spin_lock_init(&cpld_access_lock);

    err = platform_driver_register(&ocores_i2c_driver);
    if (err < 0) {
        pr_err("Failed to register ocores_i2c_driver");
        return err;
    }

    return 0;
}
static void __exit ocores_i2c_as9817_64_exit(void)
{
    platform_driver_unregister(&ocores_i2c_driver);

}

module_init(ocores_i2c_as9817_64_init);
module_exit(ocores_i2c_as9817_64_exit);
#endif

MODULE_AUTHOR("Peter Korsgaard <peter@korsgaard.com>");
MODULE_DESCRIPTION("OpenCores I2C bus driver");
MODULE_LICENSE("GPL");
MODULE_ALIAS("platform:ocores-i2c");
