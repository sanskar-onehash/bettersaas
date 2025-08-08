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
    for ip in ip_list:
        try:
            cmd = f"echo {get_root_password()} | sudo -S fail2ban-client set {JAIL_NAME} addignoreip {ip}"
            subprocess.call(cmd, shell=True)
        except Exception as e:
            frappe.log_error("Error occured while addingoreip", e)


def remove_ignore_ips(ip_list):
    if not ip_list:
        return
    for ip in ip_list:
        try:
            cmd = f"echo {get_root_password()} | sudo -S fail2ban-client set {JAIL_NAME} delignoreip {ip}"
            subprocess.call(cmd, shell=True)
        except Exception as e:
            frappe.log_error("Error occured while delingoreip", e)
