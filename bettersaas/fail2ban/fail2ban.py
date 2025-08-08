import frappe
import subprocess
import os
from frappe.utils import get_bench_path

JAIL_NAME = "nginx-proxy"
IGNORE_IP_FILE = os.path.join(get_bench_path(), "ignoreips.list")


def get_root_password():
    password = frappe.conf.get("root_password")
    if not password:
        frappe.throw("Root password not found in site configuration.")
    return password


def get_current_ignore_ips():
    if not os.path.exists(IGNORE_IP_FILE):
        return []
    try:
        with open(IGNORE_IP_FILE, "r") as f:
            return list(filter(None, f.read().strip().splitlines()))
    except Exception as e:
        frappe.log_error("Failed to read ignoreips file", e)
        return []


def update_ignoreip_file(ip_list):
    try:
        unique_ips = sorted(set(ip_list))
        with open(IGNORE_IP_FILE, "w") as f:
            f.write("\n".join(unique_ips) + "\n")
    except Exception as e:
        frappe.log_error("Error updating ignoreips file", e)


def set_ignore_ips(ip_list):
    if not ip_list:
        return

    for ip in ip_list:
        try:
            cmd = f"echo {get_root_password()} | sudo -S fail2ban-client set {JAIL_NAME} addignoreip {ip}"
            subprocess.call(cmd, shell=True)
        except Exception as e:
            frappe.log_error("Error occurred while addignoreip", e)

    current_ips = get_current_ignore_ips()
    new_ips = sorted(set(current_ips + ip_list))
    update_ignoreip_file(new_ips)


def remove_ignore_ips(ip_list):
    if not ip_list:
        return

    for ip in ip_list:
        try:
            cmd = f"echo {get_root_password()} | sudo -S fail2ban-client set {JAIL_NAME} delignoreip {ip}"
            subprocess.call(cmd, shell=True)
        except Exception as e:
            frappe.log_error("Error occurred while delignoreip", e)

    current_ips = get_current_ignore_ips()
    remaining_ips = sorted(set(current_ips) - set(ip_list))
    update_ignoreip_file(remaining_ips)
