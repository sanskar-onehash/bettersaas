frappe.listview_settings["SaaS Sites"] = {
  onload: function (listview) {
    listview.page.add_inner_button(__("Reapply Ignore IPs"), function () {
      frappe.call({
        method:
          "bettersaas.bettersaas.doctype.saas_sites.saas_sites.reignore_ips",
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
