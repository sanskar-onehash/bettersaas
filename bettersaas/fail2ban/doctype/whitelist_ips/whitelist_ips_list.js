frappe.listview_settings["Whitelist IPs"] = {
  onload: function (listview) {
    listview.page.add_inner_button(__("Reapply Ignore IPs"), function () {
      frappe.call({
        method:
          "bettersaas.fail2ban.doctype.whitelist_ips.whitelist_ips.reignore_ips",
        callback: function (r) {
          if (!r.exc) {
            frappe.msgprint(__("Ignore IPs reapplied successfully."));
          }
        },
        freeze: true,
        freeze_message: __("Reapplying ignore IPs..."),
      });
    });
  },
};
