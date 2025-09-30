import frappe

def get_context():
	"""
	Set up context for the SMTP configuration page.
	"""
	context = frappe._dict()
	context.title = "SMTP Configuration"
	context.no_cache = 1
	context.show_sidebar = True
	context.show_search = False
	
	return context
