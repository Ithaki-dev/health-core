# Health Core Configuration Guide

## SMTP Configuration

Add these settings to your `site_config.json` file for SMTP configuration.
The values will be used during app installation to configure the default email account.

### Required SMTP Settings

```json
{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_user": "your-email@4geeks.com",
  "smtp_password": "your-app-password"
}
```

### Optional SMTP Settings

```json
{
  "smtp_use_tls": 1,
  "smtp_use_ssl": 0
}
```

### Complete site_config.json Example

Here's how your complete `site_config.json` file might look:

```json
{
  "db_name": "your_site_db",
  "db_password": "your_db_password", 
  "encryption_key": "your_encryption_key",
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_user": "health@4geeks.com",
  "smtp_password": "your-secure-password",
  "smtp_use_tls": 1,
  "smtp_use_ssl": 0
}
```

### Security Notes

- Never commit `site_config.json` to version control
- Use environment variables or secure credential management in production
- The SMTP password should be an app-specific password, not your main account password

## Automatic Email Processing Setup

The health_core app includes automatic email processing to ensure emails are sent without manual intervention.

### 1. Deploy the Email Processing Script

First, copy the email processing script to your Frappe container:

```bash
# Copy the script to the container
docker cp process_emails.sh your_frappe_container_name:/home/frappe/

# Make the script executable
docker exec your_frappe_container_name chmod +x /home/frappe/process_emails.sh
```

### 2. Setup Cron Job for Automatic Processing

Create a cron job to process emails every 2 minutes:

```bash
# Access the container as frappe user
docker exec -u frappe your_frappe_container_name bash

# Add cron job entry
echo '*/2 * * * * cd /home/frappe/frappe-bench && bench --site your_site execute "frappe.email.queue.flush"' | crontab -

# Verify the cron job was added
crontab -l
```

### 3. Start the Cron Service

Enable and start the cron service in the container:

```bash
# Start cron service (as root user)
docker exec -u root your_frappe_container_name service cron start

# Verify cron is running
docker exec your_frappe_container_name ps aux | grep cron
```

### 4. Enable System Settings

Ensure the following settings are enabled in your Frappe site:

```bash
# Enable scheduler
docker exec -u frappe your_frappe_container_name bash -c "cd /home/frappe/frappe-bench && bench --site your_site set-config enable_scheduler 1"

# Enable auto email queue
docker exec -u frappe your_frappe_container_name bash -c "cd /home/frappe/frappe-bench && bench --site your_site set-config auto_email_queue 1"
```

### 5. Verify Automatic Processing

Test that emails are processed automatically:

1. Send a test email from your Frappe system
2. Check the Email Queue: `/app/email-queue`
3. Wait 2 minutes - the email should change from "Not Sent" to "Sent" automatically
4. The email should arrive in the recipient's inbox without manual intervention

### Troubleshooting

If emails are not processing automatically:

1. **Check cron service**: `docker exec your_container ps aux | grep cron`
2. **Verify cron job**: `docker exec -u frappe your_container crontab -l`
3. **Check email queue**: Navigate to `/app/email-queue` in your Frappe interface
4. **Manual processing**: Run `frappe.email.queue.flush()` in console to test
5. **Check logs**: `docker logs your_scheduler_container`

### Alternative: Background Script Method

If cron is not available, you can run the background script:

```bash
# Run the email processing script in background
docker exec -d -u frappe your_frappe_container /home/frappe/process_emails.sh
```

This script will continuously process emails every 2 minutes.
- In production, these credentials will be managed by Frappe Cloud infrastructure

### Testing Configuration

After installing the app, you can test the configuration by:

1. Visiting `/health-core` on your site
2. Using the "Send Test Email" feature
3. Checking the Communication doctype for audit logs