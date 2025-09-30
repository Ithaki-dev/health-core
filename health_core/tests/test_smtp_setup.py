# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
import unittest
from unittest.mock import patch, MagicMock


class TestSMTPSetup(unittest.TestCase):
	"""
	Test cases for SMTP setup functionality in health_core app.
	"""
	
	def setUp(self):
		"""Set up test environment"""
		self.test_site_config = {
			'smtp_server': 'smtp.gmail.com',
			'smtp_port': 587,
			'smtp_user': 'test@example.com',
			'smtp_password': 'mock_test_password'
		}
	
	@patch('frappe.conf.get')
	def test_smtp_credentials_retrieval(self, mock_conf_get):
		"""Test that SMTP credentials are properly retrieved from site config"""
		from health_core.setup.install import setup_default_email_account
		
		# Mock the configuration values
		def mock_get(key, default=None):
			return self.test_site_config.get(key, default)
		
		mock_conf_get.side_effect = mock_get
		
		# Test that credentials are retrieved
		smtp_user = frappe.conf.get('smtp_user')
		smtp_password = frappe.conf.get('smtp_password')
		
		self.assertEqual(smtp_user, 'test@4geeks.com')
		self.assertEqual(smtp_password, 'test_password')
	
	@patch('frappe.db.get_value')
	@patch('frappe.conf.get')
	def test_no_duplicate_default_account(self, mock_conf_get, mock_db_get_value):
		"""Test that duplicate default email accounts are not created"""
		from health_core.setup.install import setup_default_email_account
		
		# Mock existing default account
		mock_db_get_value.return_value = ("Existing Account", "existing@test.com")
		
		# Mock configuration
		def mock_get(key, default=None):
			return self.test_site_config.get(key, default)
		mock_conf_get.side_effect = mock_get
		
		# This should not raise an exception
		try:
			setup_default_email_account()
		except Exception as e:
			self.fail(f"setup_default_email_account raised an exception: {e}")
	
	def test_smtp_configuration_validation(self):
		"""Test SMTP configuration validation"""
		from health_core.setup.install import validate_smtp_configuration
		
		with patch('frappe.db.get_value') as mock_get_value:
			# Test no default account
			mock_get_value.return_value = None
			result = validate_smtp_configuration()
			self.assertEqual(result['status'], 'error')
			self.assertFalse(result['configured'])
			
			# Test disabled outgoing
			mock_get_value.return_value = {
				'name': 'Test Account',
				'email_account_name': 'Test',
				'enable_outgoing': 0
			}
			result = validate_smtp_configuration()
			self.assertEqual(result['status'], 'warning')
			self.assertFalse(result['configured'])
			
			# Test valid configuration
			mock_get_value.return_value = {
				'name': 'Test Account',
				'email_account_name': '4Geeks Health SMTP',
				'enable_outgoing': 1
			}
			result = validate_smtp_configuration()
			self.assertEqual(result['status'], 'success')
			self.assertTrue(result['configured'])


class TestSMTPManager(unittest.TestCase):
	"""
	Test cases for SMTP manager utilities.
	"""
	
	@patch('frappe.has_permission')
	def test_permission_checks(self, mock_has_permission):
		"""Test that API endpoints properly check permissions"""
		from health_core.utils.smtp_manager import get_smtp_configuration_status
		
		# Test with permission
		mock_has_permission.return_value = True
		try:
			result = get_smtp_configuration_status()
			# Should not raise permission error
		except frappe.PermissionError:
			self.fail("get_smtp_configuration_status raised PermissionError with valid permissions")
	
	@patch('frappe.utils.validate_email_address')
	def test_email_validation(self, mock_validate_email):
		"""Test email address validation in test email function"""
		from health_core.utils.smtp_manager import send_test_email_api
		
		# Test invalid email
		mock_validate_email.return_value = False
		
		with patch('frappe.has_permission', return_value=True):
			result = send_test_email_api("invalid-email")
		
		self.assertEqual(result['status'], 'error')
		self.assertIn('Invalid email address', result['message'])


class TestSecurityCompliance(unittest.TestCase):
	"""
	Test cases to ensure security compliance.
	"""
	
	def test_no_hardcoded_credentials(self):
		"""Test that no SMTP credentials are hardcoded in the source"""
		import os
		import re
		
		# Get the health_core directory
		app_dir = os.path.dirname(os.path.dirname(__file__))
		
		# Pattern to match potential hardcoded passwords/credentials
		sensitive_patterns = [
			r'password\s*=\s*["\'][^"\']+["\']',
			r'smtp_password\s*=\s*["\'][^"\']+["\']',
			r'passwd\s*=\s*["\'][^"\']+["\']'
		]
		
		violations = []
		
		for root, dirs, files in os.walk(app_dir):
			for file in files:
				if file.endswith('.py'):
					file_path = os.path.join(root, file)
					try:
						with open(file_path, 'r', encoding='utf-8') as f:
							content = f.read()
							
							for pattern in sensitive_patterns:
								matches = re.findall(pattern, content, re.IGNORECASE)
								for match in matches:
									# Skip test files and template examples
									if 'test' not in file.lower() and 'example' not in match.lower():
										violations.append(f"{file_path}: {match}")
					except Exception:
						# Skip files that can't be read
						continue
		
		self.assertEqual(len(violations), 0, 
						f"Found potential hardcoded credentials: {violations}")
	
	def test_uses_site_config(self):
		"""Test that the app properly uses site configuration for credentials"""
		from health_core.setup.install import setup_default_email_account
		
		# Read the source code to ensure frappe.conf.get is used
		import inspect
		source = inspect.getsource(setup_default_email_account)
		
		self.assertIn('frappe.conf.get', source, 
					 "setup_default_email_account should use frappe.conf.get for credentials")
		self.assertIn('smtp_user', source, 
					 "setup_default_email_account should retrieve smtp_user from config")
		self.assertIn('smtp_password', source, 
					 "setup_default_email_account should retrieve smtp_password from config")


if __name__ == '__main__':
	unittest.main()