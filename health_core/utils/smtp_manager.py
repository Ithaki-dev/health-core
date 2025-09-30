# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _


@frappe.whitelist()
def get_smtp_configuration_status():
	"""
	API endpoint to get the current SMTP configuration status.
	This can be used by the frontend to display configuration information.
	
	Returns:
		dict: Current SMTP configuration status and details
	"""
	from health_core.setup.install import validate_smtp_configuration
	
	try:
		return validate_smtp_configuration()
	except Exception as e:
		frappe.logger().error(f"Error getting SMTP configuration status: {str(e)}")
		return {
			"status": "error",
			"message": f"Unable to retrieve configuration status: {str(e)}",
			"configured": False
		}


@frappe.whitelist(methods=["POST"])
def reset_to_default_smtp():
	"""
	API endpoint to reset email configuration back to 4Geeks default SMTP.
	This allows administrators to revert to default settings if needed.
	
	Returns:
		dict: Status of the reset operation
	"""
	from health_core.setup.install import setup_default_email_account, create_audit_log
	
	try:
		# Check if user has permission to modify email accounts
		if not frappe.has_permission("Email Account", "write"):
			frappe.throw(_("You don't have permission to modify email account settings"))
		
		# Setup default email account (this function is idempotent)
		setup_default_email_account()
		frappe.db.commit()
		
		# Log the reset action for audit purposes
		create_audit_log(
			action="SMTP Configuration Reset",
			details="Administrator reset email configuration to 4Geeks default SMTP",
			status="Success"
		)
		
		return {
			"status": "success",
			"message": "Email configuration has been reset to 4Geeks default SMTP settings"
		}
		
	except Exception as e:
		frappe.logger().error(f"Error resetting SMTP configuration: {str(e)}")
		
		# Log the failed reset for audit purposes
		create_audit_log(
			action="SMTP Configuration Reset Failed",
			details=f"Failed to reset SMTP configuration: {str(e)}",
			status="Failed"
		)
		
		return {
			"status": "error",
			"message": f"Failed to reset SMTP configuration: {str(e)}"
		}


@frappe.whitelist(methods=["POST"])
def send_test_email_api(recipient_email=None):
	"""
	API endpoint to send a test email using the current SMTP configuration.
	
	Args:
		recipient_email (str): Email address to send test email to. 
		                      If not provided, sends to current user.
	
	Returns:
		dict: Status of the test email operation
	"""
	from health_core.setup.install import create_audit_log
	
	try:
		# Check if user has permission to send emails
		if not frappe.has_permission("Communication", "create"):
			frappe.throw(_("You don't have permission to send emails"))
		
		# Use provided recipient or default to current user
		if not recipient_email:
			recipient_email = frappe.session.user
		
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
			<li>Sent by: {frappe.session.user}</li>
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
		
		# Log the successful test for audit purposes
		create_audit_log(
			action="Manual SMTP Test Email Sent",
			details=f"Test email sent to {recipient_email} by user {frappe.session.user}",
			status="Success"
		)
		
		return {
			"status": "success",
			"message": f"Test email sent successfully to {recipient_email}"
		}
		
	except Exception as e:
		frappe.logger().error(f"Failed to send test email: {str(e)}")
		
		# Log the failed test for audit purposes
		create_audit_log(
			action="Manual SMTP Test Email Failed",
			details=f"Failed to send test email to {recipient_email or 'current user'}: {str(e)}",
			status="Failed"
		)
		
		return {
			"status": "error",
			"message": f"Failed to send test email: {str(e)}"
		}


@frappe.whitelist()
def get_email_account_settings():
	"""
	API endpoint to get current email account settings for display in UI.
	Only returns non-sensitive information.
	
	Returns:
		dict: Email account configuration details (without password)
	"""
	try:
		# Get all email accounts for the user to see
		if frappe.has_permission("Email Account", "read"):
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
				"has_permission_to_modify": frappe.has_permission("Email Account", "write")
			}
		else:
			return {
				"status": "error",
				"message": "You don't have permission to view email account settings"
			}
			
	except Exception as e:
		frappe.logger().error(f"Error getting email account settings: {str(e)}")
		return {
			"status": "error",
			"message": f"Failed to retrieve email account settings: {str(e)}"
		}