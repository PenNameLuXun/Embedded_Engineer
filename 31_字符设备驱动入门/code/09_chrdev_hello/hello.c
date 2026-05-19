/* Minimal /dev/hello char device.
 *
 * Build (on the target Linux, or with kernel headers cross-installed):
 *   make
 * Install:
 *   sudo insmod hello.ko
 *   cat /dev/hello
 *   echo hi > /dev/hello
 *   dmesg | tail
 *   sudo rmmod hello
 */
#include <linux/module.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/uaccess.h>
#include <linux/device.h>

#define DRV_NAME "hello"

static dev_t          hello_devno;
static struct cdev    hello_cdev;
static struct class  *hello_class;

static const char *kmsg = "Hello from kernel\n";

static ssize_t hello_read(struct file *f, char __user *buf, size_t cnt, loff_t *pos)
{
    size_t len = strlen(kmsg);
    if (*pos >= len) return 0;
    if (cnt > len - *pos) cnt = len - *pos;
    if (copy_to_user(buf, kmsg + *pos, cnt))
        return -EFAULT;
    *pos += cnt;
    return cnt;
}

static ssize_t hello_write(struct file *f, const char __user *buf, size_t cnt, loff_t *pos)
{
    char tmp[64] = {0};
    if (cnt >= sizeof(tmp)) cnt = sizeof(tmp) - 1;
    if (copy_from_user(tmp, buf, cnt)) return -EFAULT;
    pr_info("hello: got '%s'\n", tmp);
    return cnt;
}

static const struct file_operations hello_fops = {
    .owner = THIS_MODULE,
    .read  = hello_read,
    .write = hello_write,
};

static int __init hello_init(void)
{
    int ret = alloc_chrdev_region(&hello_devno, 0, 1, DRV_NAME);
    if (ret) return ret;

    cdev_init(&hello_cdev, &hello_fops);
    ret = cdev_add(&hello_cdev, hello_devno, 1);
    if (ret) { unregister_chrdev_region(hello_devno, 1); return ret; }

    hello_class = class_create(DRV_NAME);
    if (IS_ERR(hello_class)) {
        cdev_del(&hello_cdev);
        unregister_chrdev_region(hello_devno, 1);
        return PTR_ERR(hello_class);
    }
    device_create(hello_class, NULL, hello_devno, NULL, "hello");
    pr_info("hello: registered major=%d\n", MAJOR(hello_devno));
    return 0;
}

static void __exit hello_exit(void)
{
    device_destroy(hello_class, hello_devno);
    class_destroy(hello_class);
    cdev_del(&hello_cdev);
    unregister_chrdev_region(hello_devno, 1);
    pr_info("hello: unloaded\n");
}

module_init(hello_init);
module_exit(hello_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("you");
MODULE_DESCRIPTION("Hello chrdev");
