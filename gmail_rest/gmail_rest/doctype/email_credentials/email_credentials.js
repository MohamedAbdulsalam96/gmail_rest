// Copyright (c) 2023, tridz and contributors
// For license information, please see license.txt

frappe.ui.form.on('Email Credentials', {
	refresh: function(frm) {
		frm.add_custom_button(__('Add Account'),function(){
			window.location.href="/api/method/gmail_rest.gmail_rest.email.gmail.oauth.authorize"

		},__("Account Settings"))
		frm.add_custom_button(__('Revoke'),function(){
			frappe.call({
				method: "gmail_rest.gmail_rest.email.gmail.oauth.revoke",
				callback: function(r) {
					// code snippet
				}
			});

		},__("Account Settings"))

	}
});