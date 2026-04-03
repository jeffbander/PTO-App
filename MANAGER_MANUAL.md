# Manager Manual
## MSW CVI PTO Tracker

**App URL: https://pto-app.mswheart.com**

---

## Logging In

1. Go to the app URL
2. Click **Login** in the navigation bar
3. Enter your Mount Sinai email and password
4. You will be redirected to your role-specific dashboard

---

## Manager Roles

| Role | Dashboard | What You Can Manage |
|------|-----------|---------------------|
| **Super Admin** | Super Admin Dashboard | All employees across all teams. Full system access including employee management, all requests, and system-wide calendar. |
| **Clinical** | Clinical Dashboard | All clinical team staff: RNs, CVI MOAs, Echo Techs, Vascular Techs, EKG Techs, Nuclear Techs, Cardiac CT Techs. |
| **Echo Supervisor** | Echo Supervisor Dashboard | Echo Techs and Vascular Techs only. |
| **Admin** | Admin Dashboard | Admin team staff: Secretary II, Leadership positions. |

---

## Your Dashboard

After logging in, you are directed to your role-specific dashboard. All dashboards share these common features:

### Stats Overview
- **Pending Requests** - requests waiting for your decision
- **Approved Requests** - total approved requests
- **Total Requests** - all requests in the system
- **Team Members** - total employees you manage

### Pending Requests Section
Pending requests appear prominently at the top of your dashboard. Each pending request shows:
- Employee name and team
- Dates requested
- PTO type (Vacation, Personal, Sick, Union Business)
- Duration in days
- Approve and Deny buttons

### Team Calendar
Your dashboard includes a calendar showing all approved and pending PTO for your team. Calendar color codes:
- **Green** = Approved
- **Yellow** = Pending
- **Red** = Call-Out (auto-approved sick day via SMS)
- **Purple background** = Mount Sinai Holiday (not a work day)

Use the **prev/next** arrows and **today** button to navigate. Toggle between **month** and **week** views.

### Requests Table
Below the calendar, a table lists all requests. Use the filter tabs to view:
- All Requests
- Pending only
- Approved only
- Call-Outs only

---

## Approving a PTO Request

1. Find the request in the **Pending Requests** section on your dashboard
2. Review the details:
   - Employee name, team, and position
   - Dates requested (start and end)
   - PTO type (Vacation, Personal, Sick, Union Business)
   - Duration in business days
   - Reason (if provided)
3. Click the green **Approve** button
4. The system will:
   - Change the request status to **Approved**
   - Deduct the hours from the employee's balance:
     - **Sick** type requests deduct from **Sick balance**
     - **All other types** (Vacation, Personal, Union Business) deduct from **PTO balance**
   - Send an email notification to the employee
5. The approved request now appears on the calendar

---

## Denying a PTO Request

1. Find the request in the **Pending Requests** section
2. Click the red **Deny** button
3. A denial reason may be requested
4. The employee receives an email notification with the denial
5. No hours are deducted from their balance

---

## Understanding Call-Outs

Call-outs are sick day requests submitted via SMS text message to the Twilio call-out line.

### How Call-Outs Work
1. Employee texts the call-out phone number
2. The system verifies their phone number against the employee database
3. A sick day PTO request is **automatically created and approved**
4. Sick hours are **immediately deducted** from the employee's sick balance
5. All managers receive an SMS notification
6. The employee receives a confirmation text

### What You See on Your Dashboard
- Call-outs appear with a red **CALL OUT** badge
- They are already approved — no action is needed from you
- Click to view details including the original text message

### Manager SMS Notifications
When any employee calls out, the following managers receive an SMS:
- All managers configured in the system receive notifications regardless of team

---

## Managing Employees

### Viewing All Employees
1. Click **Manage All Employees** (or the employees link in navigation)
2. You see a list of all employees you have access to
3. Use the position filter dropdown to narrow by job title

### Adding a New Employee
1. Click **Add Employee**
2. Fill in:
   - **Name** - Full name
   - **Email** - Must be a @mountsinai.org email
   - **Phone** - Cell phone number (used for SMS call-out authentication)
   - **Team** - Admin or Clinical
   - **Position** - Select from available positions
   - **Starting PTO Hours** - Default is 60 hours (8 days)
3. Click **Save**

### Viewing an Employee's Profile
Click an employee's name to see their full profile, which includes:

#### Balance Cards
- **PTO Balance** - Current remaining PTO hours with a progress bar showing usage
- **Sick Time Balance** - Current remaining sick hours with a progress bar
- **Starting hours** and **Used hours** breakdown
- **PTO Refresh Date** - When their balance resets annually

#### PTO Statistics (Three Sections)

**Requests**
- Total submitted, approved, pending, and denied counts

**Completed (Past)**
- PTO days and hours actually taken (past dates only)
- Sick days and hours taken (non-call-out)
- Call-out days and hours

**All Approved (Including Future)**
- All approved PTO days and hours including upcoming scheduled time off
- All approved sick days and hours
- All call-out days and hours

#### Request History
- Full list of all PTO requests with dates, type, duration, and status
- Toggle between list view and calendar view
- Managers can add PTO requests on behalf of employees

#### Tardiness Records
- Log and track employee tardiness
- Add records with date, minutes late, and reason

### Editing an Employee
1. Click the employee's name to open their profile
2. Click the pencil icon next to any editable field:
   - PTO balance hours
   - Sick balance hours
   - PTO refresh date
3. Enter the new value and save

### Deleting an Employee
1. Go to the employee's profile
2. If the employee has PTO history, they will be marked as **[INACTIVE]** rather than deleted
3. If they have no PTO history, they are permanently removed
4. To permanently delete an inactive employee, delete them again

---

## The Calendar

### Main Calendar Page
Access via **View Calendar** in the navigation or quick actions.

#### Features
- Full month view with all team PTO displayed
- **Filter by Team** - Show only Admin or Clinical
- **Filter by Position** - Show specific positions (RNs, Echo Techs, etc.)
- Holidays persist on the calendar regardless of filters applied

#### Color Codes
| Color | Meaning |
|-------|---------|
| Green | Approved PTO |
| Yellow | Pending (awaiting approval) |
| Red | Call-Out (auto-approved sick) |
| Purple cell with purple text | Mount Sinai Holiday |

#### Calendar Navigation
- **< >** arrows to go to previous/next month
- **today** button (green) to jump to current date
- **month/week** toggle on the right

### How Multi-Day Requests Display
- Requests spanning weekdays show as a continuous bar
- If a request spans a weekend, it splits into separate bars (e.g., Friday bar + Monday bar)
- Weekends are never shown as PTO days on the calendar

---

## How Time Off is Calculated

### Business Days
- A full work day = **7.5 hours**
- Only Monday through Friday count as work days
- Mount Sinai holidays do not count as work days

### Example Calculations
| Request | Business Days | Hours Deducted |
|---------|--------------|----------------|
| Monday to Friday (no holidays) | 5 days | 37.5 hours |
| Monday to Monday (spans a weekend) | 6 days | 45 hours |
| Single day | 1 day | 7.5 hours |
| Partial day (9 AM to 1 PM) | N/A | 4 hours |

### Partial Day Requests
Employees can request partial days by checking the "Partial Day" option and entering start and end times. Hours are calculated from the actual time difference, not the standard 7.5 hours.

### Balance Deduction Rules
| PTO Type | Deducted From | When |
|----------|---------------|------|
| Vacation | PTO Balance | When manager approves |
| Personal | PTO Balance | When manager approves |
| Union Business | PTO Balance | When manager approves |
| Sick | Sick Balance | When manager approves |
| Call-Out (via SMS) | Sick Balance | Immediately on submission (auto-approved) |

---

## Mount Sinai Holidays

These 9 holidays are excluded from PTO calculations and appear on the calendar in purple:

1. **New Year's Day** - January 1
2. **Martin Luther King Jr. Day** - 3rd Monday in January
3. **Presidents' Day** - 3rd Monday in February
4. **Memorial Day** - Last Monday in May
5. **Juneteenth** - June 19
6. **Independence Day** - July 4
7. **Labor Day** - 1st Monday in September
8. **Thanksgiving** - 4th Thursday in November
9. **Christmas** - December 25

If a holiday falls on a Saturday, it is observed on Friday. If it falls on a Sunday, it is observed on Monday.

---

## Approving New Employee Registrations

When an employee registers through the app:
1. You receive an email notification
2. Go to **Pending Employee Registrations** from your dashboard
3. Review their submitted information (name, email, position)
4. Click **Approve** to add them to the system with default PTO balances
5. Click **Deny** if the information is incorrect

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Can't see certain employees | Make sure you are logged in with the correct role. Clinical managers only see clinical staff. |
| Employee balance seems wrong | Go to the employee profile, click the edit icon next to the balance, and adjust manually. |
| PTO hours not deducted | Hours are only deducted when a request is approved. Check that the request status is "Approved." |
| Call-out not showing | Verify the employee's phone number in their profile matches the number they texted from. |
| Calendar not showing all events | Check that no filters are applied. Click "Clear" to reset filters. |
| Employee can't submit request | Make sure they are selecting their name from the dropdown and filling in all required fields. |

---

## Quick Reference

| Task | How To |
|------|--------|
| Approve a request | Dashboard → Pending Requests → Click green Approve |
| Deny a request | Dashboard → Pending Requests → Click red Deny |
| Add an employee | Quick Actions → Add Employee |
| Edit employee balance | Employee profile → Click pencil icon next to balance |
| View team calendar | Navigation → Calendar, or Dashboard calendar |
| Filter calendar | Use Team and Position dropdowns above calendar |
| View employee history | Click employee name → see Request History |
| Add PTO for employee | Employee profile → Request History → + Add PTO |
| Log tardiness | Employee profile → Tardiness section → Add Record |
| View manager manual | Quick Actions → Manager Manual |

---

*Last updated: April 2026*
