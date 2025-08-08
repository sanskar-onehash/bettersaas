# Copyright (c) 2025, OneHash and contributors
# For license information, please see license.txt


import frappe
import bettersaas.fail2ban.fail2ban as f2b
import ipaddress
import re

from frappe.model.document import Document


class WhitelistIPs(Document):

    def on_update(self):
        old_doc = self.get_doc_before_save()

        if self.disabled:
            f2b.remove_ignore_ips(self.parse_ips())
        else:
            old_ips = old_doc.parse_ips() if old_doc else []
            new_ips = self.parse_ips()

            removed_ips = list(set(old_ips) - set(new_ips))
            added_ips = list(set(new_ips) - set(old_ips))

            if removed_ips:
                f2b.remove_ignore_ips(removed_ips)
            if added_ips:
                f2b.set_ignore_ips(added_ips)

    def on_trash(self):
        if not self.disabled:
            f2b.remove_ignore_ips(self.parse_ips())

    def parse_ips(self, ip_text=None):
        ip_text = ip_text or self.ip_addresses or ""
        raw_ips = re.split(r"[\s,]+", ip_text.strip())

        valid_ips = []
        for ip in raw_ips:
            ip = ip.strip()
            if not ip:
                continue
            try:
                ipaddress.ip_network(ip, strict=False)
                valid_ips.append(ip)
            except ValueError:
                frappe.throw(f"Invalid IP address: {ip}")

        return valid_ips


@frappe.whitelist()
def reignore_ips():
    f2b.reapply_ignore_ips_from_file()
