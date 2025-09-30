# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
import json
from frappe.utils import get_url


def after_install():
	"""
	Called after the health_core app is installed.
	Sets up the default 4Geeks SMTP email account configuration.
	"""
	try:
		setup_default_email_account()
		frappe.db.commit()
		
		# Log the successful setup
		frappe.logger().info("Health Core app installed successfully with default SMTP configuration")
		
	except Exception as e:
		frappe.logger().error(f"Error setting up default email account during installation: {str(e)}")
		frappe.throw(f"Failed to configure default email account: {str(e)}")


def setup_default_email_account():
	"""
	Creates or updates the default 4Geeks SMTP email account configuration.
	This function is idempotent - it can be run multiple times safely.
	"""
	
	# Check if a default email account already exists
	existing_default = frappe.db.get_value(
		"Email Account", 
		{"default_outgoing": 1}, 
		["name", "email_id"]
	)
	
	# Get SMTP credentials from site configuration
	smtp_user = frappe.conf.get('smtp_user')
	smtp_password = frappe.conf.get('smtp_password')
	
	if not smtp_user or not smtp_password:
		frappe.logger().warning("SMTP credentials not found in site configuration. Skipping email account setup.")
		return
	
	# 4Geeks SMTP configuration
	email_account_data = {
		"doctype": "Email Account",
		"email_id": smtp_user,
		"email_account_name": "4Geeks Health SMTP",
		"service": "GMail",  # Using GMail service as template for SMTP settings
		"smtp_server": frappe.conf.get('smtp_server', 'smtp.gmail.com'),
		"smtp_port": frappe.conf.get('smtp_port', 587),
		"use_tls": 1,
		"use_ssl": 0,
		"password": smtp_password,
		"enable_outgoing": 1,
		"default_outgoing": 1,
		"enable_incoming": 0,
		"awaiting_password": 0,
		"ascii_encode_password": 0
	}
	
	if existing_default:
		# Update existing default email account
		existing_name = existing_default[0] if isinstance(existing_default, (list, tuple)) else existing_default
		
		try:
			email_account = frappe.get_doc("Email Account", existing_name)
			
			# Only update if it's not already configured with our settings
			if email_account.email_account_name != "4Geeks Health SMTP":
				# Update the existing account with 4Geeks settings
				for key, value in email_account_data.items():
					if key != "doctype":
						setattr(email_account, key, value)
				
				email_account.save()
				frappe.logger().info(f"Updated existing default email account: {existing_name}")
				
				# Send test email to verify configuration
				send_test_email(email_account)
			else:
				frappe.logger().info("4Geeks SMTP configuration already exists and is set as default")
				
		except Exception as e:
			frappe.logger().error(f"Error updating existing email account: {str(e)}")
			raise
	
	else:
		# Create new email account
		try:
			email_account = frappe.get_doc(email_account_data)
			email_account.insert()
			frappe.logger().info("Created new 4Geeks Health SMTP email account")
			
			# Send test email to verify configuration
			send_test_email(email_account)
			
		except Exception as e:
			frappe.logger().error(f"Error creating new email account: {str(e)}")
			raise


def send_test_email(email_account):
	"""
	Sends a test email to verify the SMTP configuration is working.
	
	Args:
		email_account: The Email Account document to test
	"""
	try:
		# Get the administrator email as the test recipient
		admin_email = frappe.db.get_value("User", {"name": "Administrator"}, "email")
		
		if not admin_email:
			# Fallback to the first System Manager user
			admin_email = frappe.db.get_value(
				"Has Role", 
				{"role": "System Manager", "parenttype": "User"}, 
				"parent"
			)
			if admin_email:
				admin_email = frappe.db.get_value("User", admin_email, "email")
		
		if not admin_email:
			frappe.logger().warning("No administrator email found for test email")
			return
		
		# Prepare test email content
		subject = "4Geeks Health SMTP Configuration Test"
		message = f"""
		<p>Hello,</p>
		
		<p>This is a test email to confirm that your 4Geeks Health system has been successfully configured with the default SMTP service.</p>
		
		<p><strong>Configuration Details:</strong></p>
		<ul>
			<li>Email Account: {email_account.email_account_name}</li>
			<li>SMTP Server: {email_account.smtp_server}</li>
			<li>SMTP Port: {email_account.smtp_port}</li>
			<li>From Email: {email_account.email_id}</li>
		</ul>
		
		<p>Your system is now ready to send emails for patient communications, invoices, and reminders.</p>
		
		<p>If you need to modify these settings, you can do so by navigating to:</p>
		<p><strong>Setup → Email → Email Account</strong></p>
		
		<p>Best regards,<br>
		4Geeks Health System</p>
		"""
		
		# Send the test email
		frappe.sendmail(
			recipients=[admin_email],
			subject=subject,
			message=message,
			reference_doctype="Email Account",
			reference_name=email_account.name,
			now=True
		)
		
		frappe.logger().info(f"Test email sent successfully to {admin_email}")
		
		# Log the successful test for audit purposes
		create_audit_log(
			action="SMTP Test Email Sent",
			details=f"Test email sent to {admin_email} using email account {email_account.name}",
			status="Success"
		)
		
	except Exception as e:
		frappe.logger().error(f"Failed to send test email: {str(e)}")
		
		# Log the failed test for audit purposes
		create_audit_log(
			action="SMTP Test Email Failed",
			details=f"Failed to send test email: {str(e)}",
			status="Failed"
		)


def create_audit_log(action, details, status="Success"):
	"""
	Creates an audit log entry for SMTP configuration operations.
	
	Args:
		action (str): The action performed
		details (str): Details about the action
		status (str): Status of the action (Success/Failed)
	"""
	try:
		# Create a Communication document for audit logging
		audit_log = frappe.get_doc({
			"doctype": "Communication",
			"communication_type": "Automated Message",
			"content": f"<p><strong>Action:</strong> {action}</p><p><strong>Details:</strong> {details}</p><p><strong>Status:</strong> {status}</p>",
			"subject": f"Health Core SMTP Setup - {action}",
			"sender": "Administrator",
			"communication_medium": "Email",
			"sent_or_received": "Sent",
			"reference_doctype": "Email Account",
			"status": "Linked"
		})
		
		audit_log.insert(ignore_permissions=True)
		frappe.logger().info(f"Audit log created for action: {action}")
		
	except Exception as e:
		frappe.logger().error(f"Failed to create audit log: {str(e)}")


def validate_smtp_configuration():
	"""
	Validates the current SMTP configuration and returns status information.
	This function can be called to check if the SMTP setup is working correctly.
	
	Returns:
		dict: Configuration status and details
	"""
	try:
		# Get the default outgoing email account
		default_email_account = frappe.db.get_value(
			"Email Account",
			{"default_outgoing": 1},
			["name", "email_account_name", "smtp_server", "smtp_port", "email_id", "enable_outgoing"],
			as_dict=True
		)
		
		if not default_email_account:
			return {
				"status": "error",
				"message": "No default outgoing email account configured",
				"configured": False
			}
		
		if not default_email_account.enable_outgoing:
			return {
				"status": "warning",
				"message": "Default email account exists but outgoing email is disabled",
				"configured": False,
				"account_details": default_email_account
			}
		
		# Check if it's the 4Geeks configuration
		is_4geeks_config = default_email_account.email_account_name == "4Geeks Health SMTP"
		
		return {
			"status": "success",
			"message": "SMTP configuration is active and ready",
			"configured": True,
			"is_4geeks_config": is_4geeks_config,
			"account_details": default_email_account
		}
		
	except Exception as e:
		return {
			"status": "error",
			"message": f"Error validating SMTP configuration: {str(e)}",
			"configured": False
		}