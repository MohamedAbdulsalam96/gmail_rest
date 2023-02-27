frappe.pages['gmail_poc'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Gmail',
		single_column: true
	});
	feed = $(frappe.render_template("gmail_poc")).appendTo(page.main);;
}