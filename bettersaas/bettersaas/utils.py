import subprocess
import requests
import frappe
from frappe import utils


@frappe.whitelist()
def get_backup_size_of_site():
    url = (
        "http://"
        + frappe.conf.admin_url
        + "/api/method/bettersaas.bettersaas.doctype.saas_sites.saas_sites.get_site_backup_size?site_name="
        + frappe.local.site
    )
    resp = requests.get(url)
    return resp.json()["message"]


@frappe.whitelist()
def get_database_size_of_site():
    return frappe.db.sql(
        "SELECT table_schema "
        + frappe.conf.db_name
        + ", SUM(data_length + index_length)  'Database Size in B' FROM information_schema.TABLES GROUP BY table_schema;"
    )


@frappe.whitelist()
def get_total_files_size():
    files = frappe.db.get_list("File", fields=["file_size"])
    total_size = sum(
        file["file_size"] for file in files if file["file_size"] is not None
    )
    return total_size


def check_disk_size(path):
    return subprocess.check_output(["du", "-hs", path]).decode("utf-8").split("\t")[0]


def convert_to_bytes(sizeInStringWithPrefix):
    if sizeInStringWithPrefix == "0":
        return 0
    prefix = sizeInStringWithPrefix[-1]
    if prefix == "G":
        return float(sizeInStringWithPrefix[:-1]) * 1024 * 1024 * 1024
    if prefix == "M":
        return float(sizeInStringWithPrefix[:-1]) * 1024 * 1024
    if prefix == "K":
        return float(sizeInStringWithPrefix[:-1]) * 1024
    return float(sizeInStringWithPrefix)


def validate_name(name, reqd=True, throw=True, name_label="Name") -> str | None:
    name = utils.strip(name)

    if not name and reqd:
        if throw:
            frappe.throw(f"{name_label} is required")

        return None

    if not utils.validate_name(name or "'"):
        if throw:
            frappe.throw(
                f"{name_label} is not valid. Special characters are not allowed."
            )

        return None

    return name


def validate_email_address(
    email_str, reqd=True, throw=True, email_label="Email"
) -> str | None:

    email_str = utils.strip(email_str)
    if not email_str:
        if reqd:
            if throw:
                frappe.throw(f"{email_label} is required")

            return None
        else:
            return email_str

    email_str = utils.validate_email_address(email_str)
    if not email_str:
        if throw:
            frappe.throw(f"{email_label} is not valid")

        return None

    return email_str


def validate_phone_number(phone_number: str, fieldname: str = "Phone"):
    if not phone_number.startswith("+"):
        phone_number = "+" + phone_number
    utils.validate_phone_number_with_country_code(phone_number, fieldname)


def parse_email_list(emails):
    return [
        email.strip()
        for email in (emails or "").replace("\n", ",").split(",")
        if email.strip()
    ]


def send_account_status_email(email, content, subject="Account Status", bcc=None):
    template = "account_status_email"
    args = {"content": content}
    frappe.sendmail(
        recipients=email,
        bcc=bcc,
        subject=subject,
        template=template,
        args=args,
        delayed=False,
    )
    return True
