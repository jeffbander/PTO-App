# Email Setup Instructions for PTO System

## Why Emails Aren't Being Sent

The PTO system is configured to send emails but requires a Gmail App Password to authenticate with Gmail's SMTP servers. Regular passwords don't work due to Google's security requirements.

## How to Enable Email Sending

### Step 1: Create a Gmail App Password

1. **Sign in to Google Account**
   - Go to: https://myaccount.google.com/apppasswords
   - Sign in with: sbzakow@mswheart.com

2. **Enable 2-Factor Authentication (if not already enabled)**
   - Google requires 2FA to use app passwords
   - Go to Security settings and enable 2-Step Verification

3. **Generate App Password**
   - Click "Select app" and choose "Mail"
   - Click "Select device" and choose "Other (custom name)"
   - Enter: "PTO System"
   - Click "Generate"
   - **COPY THE 16-CHARACTER PASSWORD** (looks like: xxxx xxxx xxxx xxxx)

### Step 2: Update Configuration

1. **Open the .env file** in PTO-App-Samanthas-Version folder
2. **Replace the password**:
   ```
   SMTP_PASSWORD=your_app_password_here
   ```
   with:
   ```
   SMTP_PASSWORD=xxxx xxxx xxxx xxxx
   ```
   (Use the actual 16-character password from Google, without spaces)

3. **Save the .env file**

### Step 3: Restart the Application

1. Stop the current Flask app (Ctrl+C)
2. Run: `python -X utf8 app.py`
3. Test by submitting a new PTO request

## Current Email Configuration

- **All emails will be sent TO:** samantha.zakow@mountsinai.org
- **All emails will be sent FROM:** sbzakow@mswheart.com
- **SMTP Server:** smtp.gmail.com (port 587)

## Testing Email

Once configured, the system will send emails for:
- PTO Request Submission (to employee and manager)
- Manager Approval
- Request Denial
- Checklist Completion (final approval)

## Troubleshooting

If emails still don't send:
1. Check the Flask console for error messages
2. Verify the app password is correct (no spaces)
3. Ensure 2FA is enabled on the Google account
4. Try regenerating a new app password

## Alternative: Keep in Console Mode

If you prefer to see emails in the console without sending:
- Set `EMAIL_ENABLED=False` in .env file
- Emails will be logged to the console for testing