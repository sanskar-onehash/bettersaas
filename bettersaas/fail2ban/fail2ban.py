import frappe
import subprocess

JAIL_NAME = "nginx-proxy"


def get_root_password():
    password = frappe.conf.get("root_password")
    if not password:
        frappe.throw("Root password not found in site configuration.")
    return password


def set_ignore_ips(ip_list):
    if not ip_list:
        return
    ips = " ".join(ip_list)
    cmd = f"echo {get_root_password()} | sudo -S fail2ban-client set {JAIL_NAME} addignoreip {ips}"
    subprocess.call(cmd, shell=True)


def remove_ignore_ips(ip_list):
    if not ip_list:
        return
    ips = " ".join(ip_list)
    cmd = f"echo {get_root_password()} | sudo -S fail2ban-client set {JAIL_NAME} delignoreip {ips}"
    subprocess.call(cmd, shell=True)
