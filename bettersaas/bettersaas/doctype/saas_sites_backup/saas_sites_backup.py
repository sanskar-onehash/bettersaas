# Copyright (c) 2024, OneHash and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


@frappe.whitelist()
def get_backups(site):
	frappe.only_for("System Manager")
	return frappe.db.get_list(
		"SaaS Sites Backup",
		filters={"site": site},
		fields=["*"],
		ignore_permissions=True,
	)


@frappe.whitelist()
def restore_site(*args, **kwargs):
	frappe.only_for("System Manager")
	frappe.throw(_("Legacy S3 restores are disabled. Restore a local database backup using Bench."))


class SaaSSitesBackup(Document):
	pass
