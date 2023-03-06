// Copyright (c) 2023, tridz and contributors
// For license information, please see license.txt

frappe.ui.form.on('Google Credentials', {
	refresh: function(frm) {
		frm.add_custom_button(__('Add Account'),function(){
			window.location.href="https://helpdesk.frappe.cloud/api/method/gmail_rest.www.home.authorize"

		},__("Account Settings"))
		frm.add_custom_button(__('Revoke'),function(){
			frappe.call({
				method: "gmail_rest.www.home.revoke",
				callback: function(r) {
					// code snippet
				}
			});

		},__("Account Settings"))

	}
});