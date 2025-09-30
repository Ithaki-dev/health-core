# Health Core Deployment Guide

## Pre-deployment Checklist

### 1. Environment Setup
- [ ] Frappe Framework 15 installed
- [ ] ERPNext installed (recommended)
- [ ] Site created and configured
- [ ] Database backup taken

## Quick Setup for Automatic Email Processing

### Prerequisites
- Frappe/ERPNext running in Docker containers
- Health Core app installed and configured
- SMTP credentials in site_config.json

### Step-by-Step Email Processing Setup

#### 1. Copy Email Processing Script
```bash
# Copy the script to your backend container
docker cp process_emails.sh frappe_docker_backend_1:/home/frappe/

# Make it executable
docker exec frappe_docker_backend_1 chmod +x /home/frappe/process_emails.sh
```

#### 2. Setup Automatic Processing (Choose one method)

**Method 1: Cron Job (Recommended)**
```bash
# Add cron job for email processing every 2 minutes
docker exec -u frappe frappe_docker_backend_1 bash -c "echo '*/2 * * * * cd /home/frappe/frappe-bench && bench --site 4geeks execute \"frappe.email.queue.flush\"' | crontab -"

# Start cron service
docker exec -u root frappe_docker_backend_1 service cron start
```

**Method 2: Background Script**
```bash
# Run the background processing script
docker exec -d -u frappe frappe_docker_backend_1 /home/frappe/process_emails.sh
```

#### 3. Enable System Settings
```bash
# Enable scheduler
docker exec -u frappe frappe_docker_backend_1 bash -c "cd /home/frappe/frappe-bench && bench --site 4geeks set-config enable_scheduler 1"

# Enable auto email queue
docker exec -u frappe frappe_docker_backend_1 bash -c "cd /home/frappe/frappe-bench && bench --site 4geeks set-config auto_email_queue 1"
```

#### 4. Configure Email Queue Job
```bash
# Update the scheduled job to run every 2 minutes
docker exec -u frappe frappe_docker_backend_1 bash -c "cd /home/frappe/frappe-bench && echo 'job = frappe.get_doc(\"Scheduled Job Type\", \"queue.flush\"); job.frequency = \"Cron\"; job.cron_format = \"*/2 * * * *\"; job.save(); print(\"Email job updated\")' | bench --site 4geeks console"
```

#### 5. Restart Services
```bash
# Restart backend and scheduler containers
docker restart frappe_docker_backend_1 frappe_docker_scheduler_1
```

### Email Processing Verification

1. **Send Test Email**: Use the Health Core interface at `/health_core` to send a test email
2. **Check Queue**: Visit `/app/email-queue` - emails should show as "Not Sent" initially
3. **Wait 2 Minutes**: Emails should automatically change to "Sent"
4. **Check Inbox**: Verify emails arrive in recipient's mailbox

### Troubleshooting Email Processing

```bash
# Check if cron is running
docker exec frappe_docker_backend_1 ps aux | grep cron

# Check cron jobs
docker exec -u frappe frappe_docker_backend_1 crontab -l

# Manual email processing
docker exec -u frappe frappe_docker_backend_1 bash -c "cd /home/frappe/frappe-bench && bench --site 4geeks execute 'frappe.email.queue.flush'"

# Check email queue status
docker exec -u frappe frappe_docker_backend_1 bash -c "cd /home/frappe/frappe-bench && echo 'print(len(frappe.get_all(\"Email Queue\", filters={\"status\": \"Not Sent\"})), \"emails pending\")' | bench --site 4geeks console"
```

### Success Indicators

✅ Emails appear in queue as "Not Sent"  
✅ After 2 minutes, emails change to "Sent" automatically  
✅ Emails arrive in recipient's inbox  
✅ No manual intervention required

### 2. SMTP Credentials
- [ ] 4Geeks SMTP server details available
- [ ] SMTP username and app password obtained
- [ ] Credentials added to `site_config.json`

### 3. Permissions
- [ ] Deploying user has site administrator access
- [ ] System Manager role available for testing

## Deployment Steps

### Step 1: Get the App

```bash
# Navigate to your bench directory
cd /path/to/your/bench

# Get the health_core app
bench get-app health_core /path/to/health-core
```

### Step 2: Configure SMTP Settings

Edit your site's `site_config.json` file:

```bash
# Edit site configuration
nano sites/[your-site]/site_config.json
```

Add the SMTP configuration:

```json
{
  "db_name": "your_site_db",
  "db_password": "your_db_password",
  "encryption_key": "your_encryption_key",
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_user": "health@4geeks.com",
  "smtp_password": "your-secure-app-password",
  "smtp_use_tls": 1,
  "smtp_use_ssl": 0
}
```

### Step 3: Install the App

```bash
# Install the app on your site
bench --site [your-site] install-app health_core
```

### Step 4: Verify Installation

1. **Check Installation Status**:
   ```bash
   bench --site [your-site] list-apps
   ```
   You should see `health_core` in the list.

2. **Check Email Account Configuration**:
   - Log into your site
   - Go to **Setup → Email → Email Account**
   - Verify "4Geeks Health SMTP" account exists and is set as default

3. **Access SMTP Configuration Interface**:
   - Visit `https://[your-site]/health-core`
   - Verify the interface loads and shows correct configuration

4. **Send Test Email**:
   - Use the SMTP configuration interface
   - Send a test email to verify functionality

## Post-deployment Verification

### 1. Functional Testing

#### Test Email Sending
```bash
# From Frappe console
bench --site [your-site] console
```

```python
# In console, test email sending
import frappe
frappe.sendmail(
    recipients=["admin@yoursite.com"],
    subject="Health Core Test Email",
    message="This is a test email from Health Core app."
)
```

#### Test API Endpoints
```bash
# Test SMTP status API
curl -X GET "https://[your-site]/api/method/health_core.utils.smtp_manager.get_smtp_configuration_status" \
     -H "Authorization: token [your-api-key]:[your-api-secret]"
```

### 2. Security Verification

- [ ] Verify no SMTP credentials are visible in browser
- [ ] Check that only authorized users can access `/health-core`
- [ ] Confirm audit logs are being created in Communication doctype

### 3. Performance Check

- [ ] Site loads normally after installation
- [ ] No significant increase in response times
- [ ] Background jobs processing normally

## Troubleshooting

### Common Issues

#### 1. "Module not found" Error
```bash
# Clear cache and restart
bench --site [your-site] clear-cache
bench restart
```

#### 2. SMTP Configuration Not Applied
- Check `site_config.json` for correct credentials
- Verify credentials format (no extra spaces/quotes)
- Check Error Log for installation errors

#### 3. Permission Errors
```bash
# Reset permissions
bench --site [your-site] set-admin-password [new-password]
```

#### 4. Test Email Not Sending
- Verify SMTP server allows connections from your server IP
- Check if port 587 is open
- Validate SMTP credentials manually

### Log Files to Check

1. **Site Error Log**: `sites/[your-site]/logs/error.log`
2. **Email Queue**: Check Email Queue doctype for failed emails
3. **Communication Log**: Check Communication doctype for audit entries

## Rollback Procedure

If deployment fails and rollback is needed:

```bash
# Remove the app
bench --site [your-site] uninstall-app health_core

# Remove app from bench
bench remove-app health_core

# Restore from backup if needed
bench --site [your-site] restore [backup-file]
```

## Monitoring

### Key Metrics to Monitor

1. **Email Delivery Rate**: Check Email Queue for failed emails
2. **System Performance**: Monitor response times
3. **Error Rates**: Check error logs for health_core related issues
4. **User Adoption**: Monitor usage of `/health-core` interface

### Alerts to Set Up

- Failed email delivery notifications
- SMTP authentication failures
- High error rates in health_core modules

## Maintenance

### Regular Tasks

1. **Weekly**: Review audit logs in Communication doctype
2. **Monthly**: Verify SMTP credentials are still valid
3. **Quarterly**: Review and update app to latest version

### Updates

```bash
# Update the app
bench update --pull --patch

# Migrate site
bench --site [your-site] migrate
```

## Support Contacts

- **Technical Issues**: development-team@4geeks.com
- **SMTP/Infrastructure**: infrastructure@4geeks.com
- **General Support**: health-support@4geeks.com

## Environment-Specific Notes

### Development
- Use test SMTP credentials
- Enable debug logging
- Test with non-production email addresses

### Staging
- Mirror production SMTP settings
- Test full email workflows
- Verify audit logging functionality

### Production
- Use production SMTP credentials
- Enable monitoring and alerting
- Regular backup of site configuration