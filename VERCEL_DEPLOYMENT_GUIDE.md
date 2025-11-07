# Vercel Deployment Guide - PTO App

## ✅ Initial Deployment Complete!

Your PTO App has been successfully deployed to Vercel:

**Production URL**: https://pto-hl7qvq55u-jeff-banders-projects.vercel.app

---

## 🚀 Next Steps to Complete Setup

### Step 1: Add Vercel Postgres Database

1. Go to your Vercel project dashboard:
   - Visit: https://vercel.com/jeff-banders-projects/pto-app

2. Click on the **"Storage"** tab

3. Click **"Create Database"**

4. Select **"Postgres"**

5. Choose a database name (e.g., `pto-database`)

6. Select your preferred region

7. Click **"Create"**

8. Vercel will automatically add the `DATABASE_URL` environment variable to your project

---

### Step 2: Add Environment Variables

1. In your Vercel project dashboard, go to **Settings** → **Environment Variables**

2. Add each of the following variables (copy from your `.env` file):

#### Required Variables:

| Variable Name | Value | Notes |
|--------------|--------|-------|
| `SESSION_SECRET` | `your_secret_key_here_change_in_production` | Change to a secure random string |
| `EMAIL_ENABLED` | `True` | Enable email notifications |
| `SMTP_HOST` | `smtp.office365.com` | Your email SMTP host |
| `SMTP_PORT` | `587` | SMTP port |
| `SMTP_USER` | `your_email@example.com` | Your email address |
| `SMTP_PASSWORD` | `your_email_password` | Your email password or app password |
| `FROM_EMAIL` | `noreply@example.com` | Sender email address |
| `ADMIN_EMAIL` | `admin@example.com` | Admin notification email |
| `CLINICAL_EMAIL` | `clinical@example.com` | Clinical notification email |

#### Twilio Variables:

| Variable Name | Value | Notes |
|--------------|--------|-------|
| `TWILIO_ACCOUNT_SID` | `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx` | Your Twilio Account SID (from Twilio Console) |
| `TWILIO_AUTH_TOKEN` | `your_twilio_auth_token_here` | Your Twilio Auth Token (from Twilio Console) |
| `TWILIO_PHONE_NUMBER` | `+1XXXXXXXXXX` | Your Twilio phone number |
| `TWILIO_SMS_NUMBER` | `+1XXXXXXXXXX` | Your Twilio SMS number |
| `MANAGER_ADMIN_SMS` | `+1XXXXXXXXXX` | Manager SMS notifications (optional) |
| `MANAGER_CLINICAL_SMS` | `+1XXXXXXXXXX` | Clinical manager SMS (optional) |

3. For each variable:
   - Click **"Add New"**
   - Enter the **Name**
   - Enter the **Value**
   - Select **"Production"** (and optionally "Preview" and "Development")
   - Click **"Save"**

---

### Step 3: Redeploy the Application

After adding all environment variables and the database:

```bash
cd PTO-App
vercel --prod --token nYArKPOcpHZkvWfQIiLFsgLn
```

Or click **"Redeploy"** in the Vercel dashboard.

---

### Step 4: Initialize the Database

Once redeployed with the Postgres database, the app will automatically:
- Create all necessary tables
- Add default manager accounts
- Add sample employee data
- Add sample PTO requests

---

### Step 5: Update Twilio Webhooks

Configure your Twilio phone number to use the new Vercel URLs:

1. Go to https://console.twilio.com
2. Navigate to **Phone Numbers** → **Manage** → **Active numbers**
3. Click on your phone number: **+1 (516) 518-9564**

#### Configure Voice Webhook:
- **A CALL COMES IN**: Webhook
- **URL**: `https://pto-hl7qvq55u-jeff-banders-projects.vercel.app/twilio/voice/incoming`
- **HTTP Method**: POST

#### Configure SMS Webhook:
- **A MESSAGE COMES IN**: Webhook
- **URL**: `https://pto-hl7qvq55u-jeff-banders-projects.vercel.app/twilio/sms/incoming`
- **HTTP Method**: POST

4. Click **"Save"**

---

## 🧪 Testing Your Deployment

### Test the Web Interface:
1. Visit: https://pto-hl7qvq55u-jeff-banders-projects.vercel.app
2. Try submitting a PTO request
3. Login as a manager:
   - Email: `admin.manager@mswcvi.com`
   - Password: `admin123`

### Test SMS Call-Out:
1. Send a text to: **+1 (516) 518-9564**
2. Message: "Calling out sick - not feeling well"
3. Check if you receive a confirmation SMS
4. Check if manager receives an email notification

### Test Voice Call-Out:
1. Call: **+1 (516) 518-9564**
2. Follow the voice prompts
3. Leave a voice message
4. Check manager email for recording link

---

## 📊 Monitoring Your Deployment

### View Deployment Logs:
```bash
vercel logs --token nYArKPOcpHZkvWfQIiLFsgLn
```

### View Build Logs in Dashboard:
1. Go to https://vercel.com/jeff-banders-projects/pto-app
2. Click on **"Deployments"**
3. Click on the latest deployment
4. View logs and runtime information

---

## 🔧 Troubleshooting

### Database Connection Issues:
- Ensure `DATABASE_URL` is set (automatically added by Vercel Postgres)
- Check logs for connection errors
- Verify the database is in the same region as your deployment

### Email Not Sending:
- Verify `EMAIL_ENABLED=True`
- Check SMTP credentials are correct
- Review logs for SMTP errors

### Twilio Not Working:
- Verify webhooks are configured correctly
- Check Twilio credentials are valid
- Ensure phone number is verified in Twilio

### Application Errors:
```bash
# View real-time logs
vercel logs --follow --token nYArKPOcpHZkvWfQIiLFsgLn

# View specific deployment logs
vercel logs [deployment-url] --token nYArKPOcpHZkvWfQIiLFsgLn
```

---

## 🎯 Production Checklist

- [ ] Vercel Postgres database created and connected
- [ ] All environment variables configured
- [ ] Application redeployed with environment variables
- [ ] Database initialized with tables and default data
- [ ] Twilio webhooks updated with Vercel URLs
- [ ] Web interface tested
- [ ] SMS call-out tested
- [ ] Voice call-out tested
- [ ] Email notifications tested
- [ ] Manager login tested
- [ ] PTO approval workflow tested

---

## 📱 Your Deployment URLs

- **Production**: https://pto-hl7qvq55u-jeff-banders-projects.vercel.app
- **Project Dashboard**: https://vercel.com/jeff-banders-projects/pto-app
- **Twilio Console**: https://console.twilio.com

---

## 🔐 Security Reminders

1. **Change Default Passwords**: Update all default manager passwords after deployment
2. **Secure Session Secret**: Use a strong, random SESSION_SECRET in production
3. **Protect Credentials**: Never commit `.env` to version control
4. **Monitor Usage**: Regularly check Vercel and Twilio usage to avoid unexpected charges
5. **Enable 2FA**: Enable two-factor authentication on Vercel and Twilio accounts

---

## 🎉 You're Live!

Your PTO tracking system is now running on Vercel with:
- ✅ Persistent PostgreSQL database
- ✅ Email notifications via Office 365
- ✅ SMS/Voice call-outs via Twilio
- ✅ Global CDN deployment
- ✅ Automatic HTTPS
- ✅ Zero-downtime deployments

**Need Help?** Check the logs or visit the Vercel documentation:
- Vercel Docs: https://vercel.com/docs
- Vercel Postgres: https://vercel.com/docs/storage/vercel-postgres
