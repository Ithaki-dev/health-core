import frappe

@frappe.whitelist(allow_guest=True)
def get_smtp_status():
	"""Get SMTP configuration status"""
	try:
		from health_core.setup.install import validate_smtp_configuration
		result = validate_smtp_configuration()
		return result
	except Exception as e:
		return {
			"status": "error",
			"message": f"Error: {str(e)}",
			"configured": False
		}

@frappe.whitelist(allow_guest=True)
def get_email_accounts():
	"""Get email account settings"""
	try:
		# Get all email accounts without permission check for guest access
		accounts = frappe.get_all(
			"Email Account",
			fields=[
				"name", "email_account_name", "email_id", "smtp_server", 
				"smtp_port", "use_tls", "use_ssl", "enable_outgoing", 
				"default_outgoing", "service"
			],
			order_by="default_outgoing desc, creation desc"
		)
		
		return {
			"status": "success",
			"accounts": accounts,
			"has_permission_to_modify": False  # Guest can't modify
		}
		
	except Exception as e:
		return {
			"status": "error",
			"message": f"Error: {str(e)}"
		}

@frappe.whitelist(allow_guest=True, methods=["POST"])
def send_test_email(recipient_email=None):
	"""Send test email"""
	try:
		# Use provided recipient or default to a test email
		if not recipient_email:
			recipient_email = "test@example.com"
		
		# Validate email format
		if not frappe.utils.validate_email_address(recipient_email):
			return {
				"status": "error",
				"message": "Invalid email address provided"
			}
		
		# Get current default email account
		default_account = frappe.db.get_value(
			"Email Account",
			{"default_outgoing": 1},
			["name", "email_account_name"],
			as_dict=True
		)
		
		if not default_account:
			return {
				"status": "error",
				"message": "No default email account configured"
			}
		
		# Prepare test email content
		subject = "Health Core SMTP Test Email"
		message = f"""
		<p>Hello,</p>
		
		<p>This is a test email sent from your 4Geeks Health system to verify that email sending is working correctly.</p>
		
		<p><strong>Configuration Details:</strong></p>
		<ul>
			<li>Email Account: {default_account.email_account_name}</li>
			<li>Sent at: {frappe.utils.now()}</li>
			<li>Test Mode: Guest Access</li>
		</ul>
		
		<p>If you received this email, your SMTP configuration is working properly.</p>
		
		<p>Best regards,<br>
		4Geeks Health System</p>
		"""
		
		# Send the test email
		frappe.sendmail(
			recipients=[recipient_email],
			subject=subject,
			message=message,
			reference_doctype="Email Account",
			reference_name=default_account.name,
			now=True
		)
		
		return {
			"status": "success",
			"message": f"Test email sent successfully to {recipient_email}"
		}
		
	except Exception as e:
		return {
			"status": "error",
			"message": f"Error: {str(e)}"
		}

@frappe.whitelist(allow_guest=True, methods=["POST"])
def reset_smtp():
	"""Reset SMTP to default"""
	try:
		# For guest access, we'll provide info instead of actually resetting
		return {
			"status": "info",
			"message": "SMTP reset functionality requires admin login. Please contact your system administrator to reset SMTP configuration."
		}
	except Exception as e:
		return {
			"status": "error",
			"message": f"Error: {str(e)}"
		}