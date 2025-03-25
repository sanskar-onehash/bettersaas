import frappe
import requests
from bettersaas.bettersaas.doctype.available_apps.available_apps import get_apps

@frappe.whitelist(allow_guest=True)
def get_all_apps():
    try:
        site_apps = [x["app_name"] for x in frappe.utils.get_installed_apps_info()]
        all_apps = get_apps()
        apps_to_return = []
        for app in all_apps:
            if app["app_name"] in site_apps:
                app["installed"] = "true"
            else:
                app["installed"] = "false"
            apps_to_return.append(app)
        return sorted(apps_to_return, key=lambda x: x["name"].lower())
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return e

@frappe.whitelist()
def install_app(*args, **kwargs):
    arr = []
    for key, value in kwargs.items():
        arr.append((key, value))
    app_name = arr[0][1]
    site_name = frappe.local.site
    frappe.utils.execute_in_shell(
        "bench --site {site_name} install-app {app_name}".format(
            site_name=site_name, app_name=app_name
        )
    )
    return "Success"

@frappe.whitelist()
def uninstall_app(*args, **kwargs):
    arr = []
    for key, value in kwargs.items():
        arr.append((key, value))
    app_name = arr[0][1]
    site_name = frappe.local.site
    frappe.utils.execute_in_shell(
        "bench --site {site_name} uninstall-app {app_name} --yes --no-backup".format(
            site_name=site_name, app_name=app_name
        )
    )
    return "Success"