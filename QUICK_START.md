# Twilio Call-Out Feature - Quick Start

## ✅ Phase 1 Complete!

Congratulations! The core Twilio call-out system is now implemented and ready to configure.

---

## 🎯 What You Have Now

✅ **Database schema** - Updated with PIN field and CallOutRecord table
✅ **Twilio service layer** - Voice and SMS handling
✅ **Webhook routes** - API endpoints for Twilio callbacks
✅ **Email notifications** - Enhanced with recording player and SMS display
✅ **Authentication** - Phone matching and PIN support
✅ **PTO integration** - Auto-creates call-out requests

---

## 📋 Files Created/Modified

### New Files (Created):
- `twilio_service.py` - Core Twilio integration (360 lines)
- `routes_twilio.py` - Webhook endpoints (230 lines)
- `migrate_add_twilio_support.py` - Database migration
- `requirements.txt` - Python dependencies
- `.env.example` - Configuration template
- `TWILIO_SETUP_GUIDE.md` - Complete setup instructions
- `TWILIO_FEATURE_SUMMARY.md` - Feature overview
- `QUICK_START.md` - This file

### Modified Files:
- `models.py` - Added PIN field + CallOutRecord model
- `email_service.py` - Enhanced call-out notifications
- `app.py` - Registered Twilio routes

---

## 🚀 Next Steps (In Order)

### Step 1: Set Up Twilio Account (15 minutes)
1. Go to https://www.twilio.com/try-twilio
2. Sign up for free trial ($15 credit included)
3. Get your **Account SID** and **Auth Token**
4. Purchase a phone number (Voice + SMS capable)
5. Save credentials for next step

### Step 2: Configure Environment (5 minutes)
1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` and add your Twilio credentials:
   ```env
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=your_auth_token_here
   TWILIO_PHONE_NUMBER=+15551234567
   ```

### Step 3: Add Phone Numbers to Employees (10 minutes)
Employees need phone numbers in database for authentication.

**Quick Script:**
```python
# add_phones.py
from app import app
from database import db
from models import TeamMember

with app.app_context():
    # Add your phone numbers here
    employees = [
        ('John Smith', '+15551234567'),
        ('Sarah Johnson', '+15552345678'),
        # Add more...
    ]

    for name, phone in employees:
        member = TeamMember.query.filter_by(name=name).first()
        if member:
            member.phone = phone
            print(f"Added phone for {name}")

    db.session.commit()
    print("Done!")
```

Run: `python add_phones.py`

### Step 4: Expose Your Server (For Testing)
**Option A: ngrok (Recommended for local testing)**
```bash
# Download from https://ngrok.com/download
ngrok http 5000
# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
```

**Option B: Deploy to production server**
- Use your actual domain

### Step 5: Configure Twilio Webhooks (5 minutes)
1. Go to Twilio Console → Phone Numbers → Your Number
2. Set **Voice** webhook:
   - URL: `https://your-url.ngrok.io/twilio/voice/incoming`
   - Method: POST
3. Set **SMS** webhook:
   - URL: `https://your-url.ngrok.io/twilio/sms/incoming`
   - Method: POST
4. Save

### Step 6: Test It! (10 minutes)
1. Start your app: `python app.py`
2. Call your Twilio number
3. Text your Twilio number
4. Check dashboard for call-out requests
5. Check email for notifications

---

## 🧪 Quick Test Commands

```bash
# 1. Install dependencies (if not already done)
pip install twilio

# 2. Run migration
python migrate_add_twilio_support.py

# 3. Start Flask app
python app.py

# 4. In another terminal, test webhook endpoints
curl http://127.0.0.1:5000/twilio/test/voice
curl http://127.0.0.1:5000/twilio/test/sms
```

---

## 📞 How Employees Use It

### Phone Call:
1. Call: **[Your Twilio Number]**
2. Hear greeting
3. System recognizes phone OR asks for PIN
4. After beep, say reason for call-out
5. Press `#` when done
6. Receive SMS confirmation

### Text Message:
1. Text: **[Your Twilio Number]**
2. Message: "Calling out sick - stomach flu"
3. Receive instant SMS confirmation
4. Manager gets email notification

---

## 🎯 Cost Breakdown

**Twilio Trial Account:**
- ✅ $15 free credit
- ✅ Phone number: $1.15/month
- ✅ Calls: $0.0085/minute
- ✅ SMS: $0.0075 inbound, $0.0079 outbound

**Example monthly cost (20 call-outs):**
- Phone: $1.15
- 20 voice calls (2 min each): $0.34
- 10 SMS: $0.32
- **Total: ~$1.81/month** 💸

Very affordable!

---

## 📚 Documentation Reference

- **`TWILIO_SETUP_GUIDE.md`** - Detailed setup (Recommended to read!)
- **`TWILIO_FEATURE_SUMMARY.md`** - Complete feature overview
- **`.env.example`** - Configuration template

---

## 🆘 Troubleshooting

**Problem: "Twilio credentials not configured"**
- Solution: Create `.env` file with credentials

**Problem: Webhook not receiving calls**
- Check Twilio Console webhook URLs
- Verify Flask app is running
- Check ngrok is still active

**Problem: Authentication fails**
- Verify phone format: `+15551234567` (with +1)
- Check employee has phone in database

**Problem: No email received**
- Check `EMAIL_ENABLED=True` in .env
- Verify SMTP configuration

---

## ✅ Checklist

- [ ] Twilio account created
- [ ] Phone number purchased
- [ ] `.env` file configured
- [ ] Employee phone numbers added
- [ ] Webhooks configured
- [ ] Flask app running
- [ ] Test call completed
- [ ] Test SMS completed
- [ ] Dashboard shows call-out
- [ ] Email received with recording/message

---

## 🎉 You're Ready!

Once you complete the checklist above, your call-out system is live!

**What's Next?**
1. Read `TWILIO_SETUP_GUIDE.md` for detailed instructions
2. Test thoroughly before announcing to staff
3. Communicate new call-out number to employees
4. Train managers on new features

---

**Total Implementation Time: ~1 hour** ⏱️

**Questions?** Check the documentation or test endpoints using the test routes:
- http://127.0.0.1:5000/twilio/test/voice
- http://127.0.0.1:5000/twilio/test/sms

**Happy call-out tracking!** 📞🎉
