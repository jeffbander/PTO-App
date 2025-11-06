# SMS Call-Out Feature Guide

## Overview

The PTO app now supports **SMS-only call-outs** via Twilio. Employees can text a designated phone number to report that they are calling out sick for the day, and the system will automatically:

1. Authenticate the employee by phone number
2. Create a PTO request for "Sick Leave" for today
3. Send instant confirmation back to the employee via SMS
4. Notify the manager via email (and optionally via SMS)
5. Display the call-out in the manager dashboard with the SMS message

---

## How It Works

### For Employees

1. **Text the Call-Out Line**: Send an SMS to the designated Twilio number (configured in your .env file)
2. **Include Your Reason**: Text your reason for calling out sick (e.g., "Not feeling well", "Flu symptoms", etc.)
3. **Get Instant Confirmation**: You'll receive an SMS confirmation with your request ID

**Example:**
```
Employee sends: "Not feeling well today, have fever and headache"
System replies: "Call-out recorded, John Doe. Request #123 has been submitted to your manager. Feel better!"
```

### For Managers

1. **Email Notification**: Receive an instant email with:
   - Employee name and details
   - SMS message text
   - Request ID and timestamp
   - Link to approve/deny in the dashboard

2. **Dashboard View**: See call-out requests with a special "CALL OUT" badge
   - Filter to view "Call-Outs Only"
   - Click to view SMS message details
   - Approve or deny as usual

3. **Optional SMS Alert**: If configured, managers can receive SMS notifications for urgent call-outs

---

## Setup Instructions

### 1. Twilio Account Setup

1. Sign up for Twilio: https://www.twilio.com/try-twilio
2. Get your credentials from the console:
   - Account SID
   - Auth Token
3. Purchase a phone number with SMS capability

### 2. Configure Environment Variables

Update your `.env` file with Twilio credentials:

```env
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+15551234567
TWILIO_SMS_NUMBER=+15551234567
```

Optionally, enable manager SMS notifications:
```env
MANAGER_ADMIN_SMS=+15559876543
MANAGER_CLINICAL_SMS=+15559876544
```

### 3. Configure Twilio Webhook

In your Twilio Console, configure the SMS webhook:

1. Go to Phone Numbers → Manage → Active Numbers
2. Click your phone number
3. Under "Messaging", set:
   - **A MESSAGE COMES IN**: Webhook
   - **URL**: `https://your-domain.com/twilio/sms/incoming`
   - **HTTP METHOD**: POST

### 4. Add Employee Phone Numbers

Ensure all employees have their phone numbers stored in the database:

1. Go to Dashboard → Manage Employees
2. Edit each employee
3. Add phone number in format: `+15551234567` or `555-123-4567`

### 5. Database Migration (Optional)

If you were previously using voice calls, run the migration to remove unused columns:

```bash
python migrate_remove_voice_call_fields.py
```

---

## Features

### SMS Authentication
- Employees are authenticated automatically by phone number
- Phone number must match what's in the database
- No PIN required for SMS (unlike removed voice call feature)

### Automatic PTO Request Creation
- Creates "Sick Leave" request for today only
- Status: "Pending" (manager must approve)
- Extracts reason from SMS message text
- Deducts from sick balance when approved (based on business days)

### Instant Confirmation
- Employee receives SMS confirmation immediately
- Includes request ID for reference
- Friendly message ("Feel better!")

### Manager Notifications
- Email notification sent instantly
- Includes full SMS message
- Optional SMS alert for urgent situations

### Dashboard Integration
- Call-outs have special "CALL OUT" badge
- Filter to view only call-outs
- Click to expand and see SMS message
- Approve/deny workflow same as regular PTO

---

## SMS Message Format

### Employee Messages

The system accepts any text message as a call-out reason. Common prefixes are automatically removed:
- "calling out"
- "call out"
- "calling in sick"
- "sick today"
- "sick"

**Examples:**
```
"Calling out - have the flu"          → Reason: "have the flu"
"Sick today, not feeling well"        → Reason: "not feeling well"
"Not coming in, family emergency"     → Reason: "Not coming in, family emergency"
```

### System Responses

**Success:**
```
"Call-out recorded, [Name]. Request #[ID] has been submitted to your manager. Feel better!"
```

**Authentication Failed:**
```
"Phone number not found in system. Please contact your manager directly or submit via the web app."
```

**Error:**
```
"Error processing call-out. Please contact your manager directly."
```

---

## Testing

### Test the SMS Endpoint

1. **Test in Browser**: Visit `https://your-domain.com/twilio/test/sms`
   - This shows what the TwiML response looks like

2. **Test with Your Phone**:
   - Text the Twilio number from a phone that matches an employee in the database
   - Verify you receive a confirmation
   - Check the manager dashboard for the new call-out request

3. **Test Authentication**:
   - Text from an unknown number
   - Verify you receive the "not found" message

---

## Troubleshooting

### "Phone number not found in system"

**Problem**: Employee's phone number doesn't match database
**Solution**:
- Check the phone number format in the database
- Ensure it includes country code (+1 for US)
- Try formats: `+15551234567`, `555-123-4567`, or `(555) 123-4567`

### No SMS confirmation received

**Problem**: Twilio not sending replies
**Solutions**:
- Check Twilio logs in console
- Verify credentials in .env file
- Check webhook is configured correctly
- Ensure phone number has SMS capability

### Call-out not appearing in dashboard

**Problem**: Request not created in database
**Solutions**:
- Check application logs
- Verify database connection
- Check that employee exists in database
- Review Twilio webhook logs for errors

### Manager not receiving email

**Problem**: Email notification not sent
**Solutions**:
- Check email configuration in .env
- Verify SMTP credentials
- Check spam folder
- Review application logs for email errors

---

## Security Considerations

1. **Phone Number Authentication**: Employees are authenticated by phone number match only
2. **Database Security**: Phone numbers should be stored securely
3. **Webhook Security**: Use HTTPS for Twilio webhooks
4. **Rate Limiting**: Consider implementing rate limits to prevent abuse
5. **Logging**: All call-out attempts are logged for audit purposes

---

## Cost Considerations

### Twilio Pricing (as of 2024):
- **SMS Received**: ~$0.0075 per message
- **SMS Sent**: ~$0.0079 per message
- **Phone Number**: ~$1.15 per month

### Estimated Monthly Costs:
- 50 employees, 10 call-outs/month
- 10 received SMS × $0.0075 = $0.08
- 10 sent confirmations × $0.0079 = $0.08
- 2 manager notifications × $0.0079 = $0.02
- Phone number = $1.15
- **Total: ~$1.33/month**

---

## Future Enhancements (Optional)

- Multi-day call-outs via SMS
- Return-to-work notifications
- Call-out history via SMS query
- Automated reminder for documentation
- Integration with calendar systems

---

## Support

For issues or questions:
1. Check application logs: `logs/app.log`
2. Review Twilio console logs
3. Contact system administrator
4. Review this guide for troubleshooting steps

---

**Note**: Voice call functionality has been removed. Only SMS call-outs are supported.
