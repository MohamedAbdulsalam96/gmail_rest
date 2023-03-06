// Copyright (c) 2023, tridz and contributors
// For license information, please see license.txt

frappe.ui.form.on('Google Credentials', {
	refresh: function(frm) {
		frm.add_custom_button(__('Add Account'),function(){
			var url="/api/method"
			window.location.href="https://helpdesk.frappe.cloud/api/method/gmail_rest.www.home.authorize"

		})
	}
});