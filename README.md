# Health Core App

A Frappe Framework 15 app that provides core functionality for the 4Geeks Health syste├── www/
    ├── __init__.py
    ├── health-core.html  # SMTP configuration web interface
    └── health-core.py    # Web page controllerncluding automatic SMTP configuration.

## Features

### Automatic SMTP Configuration
- **Automatic Setup**: Configures 4Geeks SMTP service during app installation
- **Secure Configuration**: Uses site configuration for credentials (no hardcoded passwords)
- **Test Email**: Sends verification email after setup
- **Audit Logging**: All SMTP operations are logged for audit purposes
- **Admin Override**: Administrators can still modify settings via standard ERPNext interface

## Installation

### Prerequisites
- Frappe Framework 15
- ERPNext (optional but recommended)
- Access to 4Geeks SMTP credentials

### Install the App

1. **Get the app**:
   ```bash
   bench get-app health_core /path/to/health-core
   ```

2. **Install on site**:
   ```bash
   bench --site [site-name] install-app health_core
   ```

### Configuration

Before installing, ensure your `site_config.json` contains the SMTP credentials:

```json
{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_user": "your-smtp-username@4geeks.com",
  "smtp_password": "your-smtp-password"
}
```

**Note**: These credentials will be managed by the Frappe Cloud infrastructure in production.

## Usage

### Automatic Configuration
The app automatically configures the default SMTP settings when installed. No manual intervention is required.

### SMTP Management Interface
Access the SMTP configuration interface at: `https://[your-site]/health_core`

This interface allows administrators to:
- View current SMTP configuration status
- See all configured email accounts
- Send test emails
- Reset to default 4Geeks SMTP configuration

### Manual Configuration
Administrators can still modify email settings via the standard ERPNext interface:
1. Go to **Setup → Email → Email Account**
2. Modify the "4Geeks Health SMTP" account or create new ones
3. Set the desired account as default for outgoing emails

### API Endpoints

The app provides several API endpoints for programmatic access:

#### Get SMTP Configuration Status
```
GET /api/method/health_core.utils.smtp_manager.get_smtp_configuration_status
```

#### Send Test Email
```
POST /api/method/health_core.utils.smtp_manager.send_test_email_api
Data: { recipient_email: "test@example.com" }
```

#### Reset to Default SMTP
```
POST /api/method/health_core.utils.smtp_manager.reset_to_default_smtp
```

#### Get Email Account Settings
```
GET /api/method/health_core.utils.smtp_manager.get_email_account_settings
```

## Architecture

### App Structure
```
health_core/
├── __init__.py
├── hooks.py              # App configuration and hooks
├── setup/
│   ├── __init__.py
│   └── install.py        # Installation and SMTP setup logic
├── utils/
│   ├── __init__.py
│   └── smtp_manager.py   # SMTP management utilities and APIs
└── www/
    ├── __init__.py
    ├── health_core.html  # SMTP configuration web interface
    └── health_core.py    # Web page controller
```

### Key Components

1. **Installation Hook** (`hooks.py`):
   - Calls `after_install` hook to configure SMTP

2. **SMTP Setup** (`setup/install.py`):
   - Creates or updates default email account
   - Validates configuration
   - Sends test email
   - Creates audit logs

3. **SMTP Manager** (`utils/smtp_manager.py`):
   - API endpoints for SMTP management
   - Status checking and validation
   - Test email functionality

4. **Web Interface** (`www/health_core.*`):
   - Clean, intuitive UI for administrators
   - Real-time status updates
   - Action buttons for common tasks

## Security Considerations

- **No Hardcoded Credentials**: All SMTP credentials are retrieved from `site_config.json`
- **Permission Checks**: All API endpoints check user permissions
- **Audit Logging**: All operations are logged using Frappe's Communication doctype
- **Safe Defaults**: The app uses secure SMTP settings (TLS enabled)

## Troubleshooting

### SMTP Configuration Not Applied
1. Check that `smtp_user` and `smtp_password` are set in `site_config.json`
2. Verify the app installation completed successfully
3. Check the Error Log for any installation errors

### Test Emails Not Sending
1. Verify SMTP credentials are correct
2. Check firewall settings (port 587 should be open)
3. Review audit logs in Communication doctype
4. Test SMTP settings manually via Email Account doctype

### Permission Issues
1. Ensure user has "System Manager" role
2. Check if user has "Email Account" read/write permissions
3. Verify site administrator permissions

## Development

### Running Tests
```bash
bench --site [site-name] run-tests --app health_core
```

### Code Style
The app follows Frappe's coding standards:
- PEP 8 compliance
- Proper error handling
- Comprehensive logging
- Documentation for all functions

## Support

For support and issues, please contact the 4Geeks Health development team.

## License

MIT License - see LICENSE file for details.

## Changelog

### Version 0.0.1
- Initial release
- Automatic SMTP configuration
- Web-based management interface
- Comprehensive API endpoints
- Audit logging functionality