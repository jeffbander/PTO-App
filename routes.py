from flask import render_template, request, redirect, url_for, flash, jsonify, session, current_app
from database import db
from models import PTORequest, TeamMember, Manager, User, PendingEmployee, Position
from pto_system import PTOTrackerSystem
from auth import roles_required, authenticate_user, login_user, logout_user, get_current_user
from email_service import send_submission_email
from datetime import datetime

# Initialize the PTO system
pto_system = PTOTrackerSystem()

def get_staff_directory():
    """Get current staff directory"""
    from pto_system import PTOTrackerSystem
    pto_sys = PTOTrackerSystem()
    return pto_sys.get_staff_directory()

def register_routes(app):

    @app.route('/')
    def index():
        """Main page for submitting PTO requests"""
        staff_directory = pto_system.get_staff_directory()
        return render_template('index.html', staff_directory=staff_directory)

    @app.route('/index.html')
    def index_html():
        return render_template('index.html')

    @app.route('/api/staff-directory')
    def api_staff_directory():
        """API endpoint to get current staff directory"""
        return jsonify(get_staff_directory())

    @app.route('/api/positions')
    def api_positions():
        """API endpoint to get all available positions"""
        positions = {}
        for p in Position.query.all():
            if p.team not in positions:
                positions[p.team] = []
            positions[p.team].append(p.name)
        return jsonify(positions)

@app.route('/submit_request', methods=['POST'])
def submit_request():
    """Handle PTO request submission or new employee registration"""
    try:
        name_field = request.form.get('name')
        
        # Check if this is a new employee registration
        if name_field == 'NOT_LISTED':
            return handle_new_employee_registration()
        
        # Regular PTO request submission
        return handle_pto_request_submission()
        
    except Exception as e:
        flash(f'Error processing request: {str(e)}', 'error')
        return redirect(url_for('index'))

def handle_new_employee_registration():
    """Handle new employee registration submission"""
    try:
        # Get new employee data
        new_employee_name = request.form.get('new_employee_name')
        new_employee_email = request.form.get('new_employee_email')
        team = request.form.get('new_employee_team')
        position = request.form.get('new_employee_position')
        notes = request.form.get('employee_notes', '')
        
        # Validate required fields
        if not all([new_employee_name, new_employee_email, team, position]):
            flash('Please fill in all required fields for employee registration.', 'error')
            return redirect(url_for('index'))
        
        # Check if pending employee already exists
        existing_pending = PendingEmployee.query.filter_by(email=new_employee_email).first()
        if existing_pending and existing_pending.status == 'pending':
            flash('An employee registration with this email is already pending approval.', 'warning')
            return redirect(url_for('index'))
        
        # Check if employee already exists
        existing_employee = TeamMember.query.filter_by(email=new_employee_email).first()
        if existing_employee:
            flash('An employee with this email already exists in the system.', 'error')
            return redirect(url_for('index'))
        
        # Create pending employee record
        pending_employee = PendingEmployee(
            name=new_employee_name,
            email=new_employee_email,
            team=team,
            position=position
        )
        
        # Add notes if provided
        if notes:
            pending_employee.denial_reason = f"Registration Notes: {notes}"  # Using this field for notes
        
        db.session.add(pending_employee)
        db.session.commit()
        
        # Send notification email to appropriate manager
        send_employee_approval_email(pending_employee)
        
        flash(f'Employee registration submitted successfully! Your profile has been sent to your manager for approval. You will receive an email once approved.', 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error submitting employee registration: {str(e)}', 'error')
        return redirect(url_for('index'))

def handle_pto_request_submission():
    """Handle regular PTO request submission"""
    # Get form data
    member_data = {
        'name': request.form.get('name'),
        'email': request.form.get('email'),
        'team': request.form.get('team'),
        'position': request.form.get('position')
    }
    
    pto_data = {
        'start_date': request.form.get('start_date'),
        'end_date': request.form.get('end_date'),
        'pto_type': request.form.get('pto_type', 'Vacation'),
        'is_partial_day': request.form.get('is_partial_day') == 'on',
        'start_time': request.form.get('start_time'),
        'end_time': request.form.get('end_time'),
        'reason': request.form.get('reason')
    }
    
    # Validate required fields
    if not all([member_data['name'], member_data['email'], 
               pto_data['start_date'], pto_data['end_date']]):
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('index'))
    
    # Add request to system
    new_request = pto_system.add_request(member_data, pto_data)
    
    # Send notification emails
    request_data = {**member_data, **pto_data}
    send_submission_email(request_data, new_request.id)
    
    flash(f'PTO request submitted successfully! Request ID: #{new_request.id}', 'success')
    return redirect(url_for('index'))

def send_employee_approval_email(pending_employee):
    """Send email notification to manager about new employee registration"""
    try:
        # Determine manager email based on team
        if pending_employee.team == 'admin':
            manager_emails = ['admin.manager@mswcvi.com']
        elif pending_employee.team == 'clinical':
            manager_emails = ['clinical.manager@mswcvi.com'] 
        else:
            manager_emails = ['superadmin@mswcvi.com']
        
        # Send notification to employee
        employee_subject = f"Employee Registration Submitted - Pending Approval"
        employee_body = f"""Dear {pending_employee.name},

Your employee registration has been submitted and is pending manager approval.

Registration Details:
- Name: {pending_employee.name}
- Email: {pending_employee.email}
- Team: {pending_employee.team.title()}
- Position: {pending_employee.position}
- Submitted: {pending_employee.submitted_at.strftime('%B %d, %Y at %I:%M %p')}

You will receive another email once your registration has been reviewed and approved. Once approved, you will be able to submit PTO requests.

Thank you for your patience.

Best regards,
MSW CVI PTO System
"""
        
        # Send to employee
        send_submission_email({
            'name': pending_employee.name,
            'email': pending_employee.email,
            'subject_override': employee_subject,
            'body_override': employee_body
        }, f"EMPLOYEE_REG_{pending_employee.id}")
        
        # Send notification to managers
        manager_subject = f"New Employee Registration - {pending_employee.name}"
        manager_body = f"""A new employee registration requires your approval.

Employee Information:
- Name: {pending_employee.name}
- Email: {pending_employee.email}
- Team: {pending_employee.team.title()}
- Position: {pending_employee.position}
- Registration ID: #{pending_employee.id}
- Submitted: {pending_employee.submitted_at.strftime('%B %d, %Y at %I:%M %p')}

Please log in to the PTO system to review and approve/deny this registration:
http://localhost:5000/login

Best regards,
MSW CVI PTO System
"""
        
        # Send to managers
        for manager_email in manager_emails:
            send_submission_email({
                'name': 'Manager',
                'email': manager_email,
                'subject_override': manager_subject,
                'body_override': manager_body
            }, f"MANAGER_APPROVAL_{pending_employee.id}")
            
    except Exception as e:
        print(f"Error sending employee approval emails: {e}")
        # Don't fail the registration if email fails
        pass

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Manager login page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = authenticate_user(email, password)
        if user:
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout current user"""
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@roles_required('admin', 'clinical', 'superadmin', 'moa_supervisor', 'echo_supervisor')
def dashboard():
    """Redirect to appropriate dashboard based on user role"""
    user_role = session.get('user_role')
    if user_role == 'admin':
        requests = pto_system.get_requests_by_team('admin')
        return render_template('dashboard_admin.html', requests=requests)
    elif user_role == 'clinical':
        requests = pto_system.get_requests_by_team('clinical')
        return render_template('dashboard_clinical.html', requests=requests)
    elif user_role == 'superadmin':
        requests = pto_system.get_all_requests()
        team_members = TeamMember.query.all()
        return render_template('dashboard_superadmin.html', requests=requests, team_members=team_members)
    elif user_role == 'moa_supervisor':
        requests = PTORequest.query.join(TeamMember).join(Position).filter(Position.name.contains('MOA')).all()
        return render_template('dashboard_moa_supervisor.html', requests=requests)
    elif user_role == 'echo_supervisor':
        requests = PTORequest.query.join(TeamMember).join(Position).filter(Position.name.contains('Echo')).all()
        return render_template('dashboard_echo_supervisor.html', requests=requests)
    else:
        return redirect(url_for('index'))

@app.route('/approve_request/<int:request_id>')
@roles_required('admin', 'clinical', 'superadmin', 'moa_supervisor', 'echo_supervisor')
def approve_request(request_id):
    """Approve a PTO request"""
    current_user = get_current_user()
    if pto_system.approve_request(request_id, current_user):
        flash('Request approved successfully!', 'success')
    else:
        flash('Failed to approve request.', 'error')
    return redirect(url_for('dashboard'))

@app.route('/deny_request/<int:request_id>', methods=['POST'])
@roles_required('admin', 'clinical', 'superadmin', 'moa_supervisor', 'echo_supervisor')
def deny_request(request_id):
    """Deny a PTO request"""
    denial_reason = request.form.get('denial_reason', '')
    current_user = get_current_user()
    
    if pto_system.deny_request(request_id, denial_reason, current_user):
        flash('Request denied successfully!', 'success')
    else:
        flash('Failed to deny request.', 'error')
    return redirect(url_for('dashboard'))

# Employee Management Routes
@app.route('/employees')
@roles_required('admin', 'clinical', 'superadmin', 'moa_supervisor', 'echo_supervisor')
def employees():
    """Employee management page"""
    current_user = get_current_user()
    
    if current_user.role == 'superadmin':
        # Super admin can see all employees
        team_members = TeamMember.query.order_by(TeamMember.name).all()
    elif current_user.role == 'admin':
        # Admin manager sees admin team members
        team_members = TeamMember.query.filter_by(team='admin').order_by(TeamMember.name).all()
    elif current_user.role == 'clinical':
        # Clinical manager sees clinical team members
        team_members = TeamMember.query.filter_by(team='clinical').order_by(TeamMember.name).all()
    elif current_user.role == 'moa_supervisor':
        # MOA supervisor sees MOA staff
        team_members = TeamMember.query.filter(TeamMember.position.contains('MOA')).order_by(TeamMember.name).all()
    elif current_user.role == 'echo_supervisor':
        # Echo supervisor sees Echo techs
        team_members = TeamMember.query.filter(TeamMember.position.contains('Echo')).order_by(TeamMember.name).all()
    else:
        team_members = []
    
    # Calculate statistics
    total_employees = len(team_members)
    active_employees = len([m for m in team_members if '[INACTIVE]' not in m.name])
    total_pto_hours = sum(float(m.pto_balance_hours) for m in team_members)
    total_pto_days = round(total_pto_hours / 7.5, 1)
    avg_pto_days = round((total_pto_hours / len(team_members)) / 7.5, 1) if team_members else 0
    
    stats = {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'total_pto_days': total_pto_days,
        'avg_pto_days': avg_pto_days
    }
    
    return render_template('employees.html', team_members=team_members, stats=stats)

@app.route('/employee/add', methods=['GET', 'POST'])
@roles_required('admin', 'clinical', 'superadmin')
def add_employee():
    """Add new employee"""
    if request.method == 'POST':
        try:
            employee_data = {
                'name': request.form.get('name'),
                'email': request.form.get('email'),
                'position': request.form.get('position'),
                'pto_balance': float(request.form.get('pto_balance', 60.0)),
                'pto_refresh_date': request.form.get('pto_refresh_date')
            }
            pto_system.add_employee(employee_data)
            flash(f'Employee {employee_data["name"]} added successfully!', 'success')
            return redirect(url_for('employees'))
            
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('add_employee.html')
        except Exception as e:
            flash(f'Error adding employee: {str(e)}', 'error')
            return render_template('add_employee.html')
    
    return render_template('add_employee.html')

@app.route('/employee/edit/<int:employee_id>', methods=['GET', 'POST'])
@roles_required('admin', 'clinical', 'superadmin', 'moa_supervisor', 'echo_supervisor')
def edit_employee(employee_id):
    """Edit employee information"""
    employee = TeamMember.query.get_or_404(employee_id)
    current_user = get_current_user()
    
    # Check permissions
    can_edit = False
    if current_user.role == 'superadmin':
        can_edit = True
    elif current_user.role == 'admin' and employee.team == 'admin':
        can_edit = True
    elif current_user.role == 'clinical' and employee.team == 'clinical':
        can_edit = True
    elif current_user.role == 'moa_supervisor' and 'MOA' in employee.position.name:
        can_edit = True
    elif current_user.role == 'echo_supervisor' and 'Echo' in employee.position.name:
        can_edit = True
    
    if not can_edit:
        flash('You do not have permission to edit this employee.', 'error')
        return redirect(url_for('employees'))
    
    if request.method == 'POST':
        try:
            employee_data = {
                'name': request.form.get('name'),
                'email': request.form.get('email'),
                'position': request.form.get('position'),
                'pto_balance': float(request.form.get('pto_balance', employee.pto_balance_hours)),
                'pto_refresh_date': request.form.get('pto_refresh_date')
            }
            pto_system.edit_employee(employee_id, employee_data)
            flash(f'Employee {employee_data["name"]} updated successfully!', 'success')
            return redirect(url_for('employees'))
            
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('edit_employee.html', employee=employee)
        except Exception as e:
            flash(f'Error updating employee: {str(e)}', 'error')
            return render_template('edit_employee.html', employee=employee)
    
    return render_template('edit_employee.html', employee=employee)

@app.route('/employee/<int:employee_id>')
@roles_required('admin', 'clinical', 'superadmin', 'moa_supervisor', 'echo_supervisor')
def employee_detail(employee_id):
    """Employee detail page with PTO history"""
    employee = TeamMember.query.get_or_404(employee_id)
    current_user = get_current_user()
    
    # Check permissions - same as edit permissions
    can_view = False
    if current_user.role == 'superadmin':
        can_view = True
    elif current_user.role == 'admin' and employee.team == 'admin':
        can_view = True
    elif current_user.role == 'clinical' and employee.team == 'clinical':
        can_view = True
    elif current_user.role == 'moa_supervisor' and 'MOA' in employee.position:
        can_view = True
    elif current_user.role == 'echo_supervisor' and 'Echo' in employee.position:
        can_view = True
    
    if not can_view:
        flash('You do not have permission to view this employee.', 'error')
        return redirect(url_for('employees'))
    
    # Get PTO history for this employee
    pto_requests = PTORequest.query.filter_by(member_id=employee.id).order_by(PTORequest.submitted_at.desc()).all()
    
    # Calculate PTO statistics
    total_requests = len(pto_requests)
    approved_requests = len([r for r in pto_requests if r.status == 'approved'])
    pending_requests = len([r for r in pto_requests if r.status == 'pending'])
    denied_requests = len([r for r in pto_requests if r.status == 'denied'])
    
    # Calculate total PTO days used (approved requests only)
    total_pto_used = sum(r.duration_days if not r.is_partial_day else r.duration_hours / 7.5 
                        for r in pto_requests if r.status == 'approved')
    
    # Calculate days until next PTO refresh
    days_until_refresh = None
    refresh_status = 'Not set'
    if employee.pto_refresh_date:
        from datetime import date
        today = date.today()
        days_diff = (employee.pto_refresh_date - today).days
        if days_diff > 0:
            refresh_status = f"{days_diff} days"
        elif days_diff == 0:
            refresh_status = "Today!"
        else:
            refresh_status = f"{-days_diff} days overdue"
    
    stats = {
        'total_requests': total_requests,
        'approved_requests': approved_requests,
        'pending_requests': pending_requests,
        'denied_requests': denied_requests,
        'total_pto_used': round(total_pto_used, 1),
        'refresh_status': refresh_status
    }
    
    return render_template('employee_detail.html', employee=employee, pto_requests=pto_requests, stats=stats)

@app.route('/employee/delete/<int:employee_id>', methods=['POST'])
@roles_required('admin', 'clinical', 'superadmin')
def delete_employee(employee_id):
    """Delete employee (soft delete - keep for historical records)"""
    current_user = get_current_user()
    employee = TeamMember.query.get_or_404(employee_id)
    
    # Check permissions
    can_delete = False
    if current_user.role == 'superadmin':
        can_delete = True
    elif current_user.role == 'admin' and employee.team == 'admin':
        can_delete = True
    elif current_user.role == 'clinical' and employee.team == 'clinical':
        can_delete = True
    
    if not can_delete:
        flash('You do not have permission to delete this employee.', 'error')
        return redirect(url_for('employees'))
    
    try:
        message = pto_system.delete_employee(employee_id)
        flash(message, 'success')
            
    except Exception as e:
        flash(f'Error deleting employee: {str(e)}', 'error')
    
    return redirect(url_for('employees'))

@app.route('/pending_employees')
@roles_required('admin', 'clinical', 'superadmin', 'moa_supervisor', 'echo_supervisor')
def pending_employees():
    """View pending employee registrations"""
    current_user = get_current_user()
    
    # Filter pending employees based on manager role
    if current_user.role == 'superadmin':
        pending_list = PendingEmployee.query.filter_by(status='pending').order_by(PendingEmployee.submitted_at.desc()).all()
    elif current_user.role == 'admin':
        pending_list = PendingEmployee.query.filter_by(team='admin', status='pending').order_by(PendingEmployee.submitted_at.desc()).all()
    elif current_user.role == 'clinical':
        pending_list = PendingEmployee.query.filter_by(team='clinical', status='pending').order_by(PendingEmployee.submitted_at.desc()).all()
    else:
        pending_list = []
    
    # Get all pending employees for stats (superadmin only)
    all_pending = PendingEmployee.query.filter_by(status='pending').count() if current_user.role == 'superadmin' else len(pending_list)
    
    return render_template('pending_employees.html', pending_employees=pending_list, total_pending=all_pending)

@app.route('/approve_employee/<int:employee_id>')
@roles_required('admin', 'clinical', 'superadmin', 'moa_supervisor', 'echo_supervisor')
def approve_employee(employee_id):
    """Approve a pending employee registration"""
    pending_employee = PendingEmployee.query.get_or_404(employee_id)
    current_user = get_current_user()
    
    # Check permissions
    can_approve = False
    if current_user.role == 'superadmin':
        can_approve = True
    elif current_user.role == 'admin' and pending_employee.team == 'admin':
        can_approve = True
    elif current_user.role == 'clinical' and pending_employee.team == 'clinical':
        can_approve = True
    
    if not can_approve:
        flash('You do not have permission to approve this employee registration.', 'error')
        return redirect(url_for('pending_employees'))
    
    if pending_employee.status != 'pending':
        flash('This employee registration has already been processed.', 'warning')
        return redirect(url_for('pending_employees'))
    
    try:
        # Create new TeamMember from pending employee
        new_employee = TeamMember(
            name=pending_employee.name,
            email=pending_employee.email,
            team=pending_employee.team,
            position=pending_employee.position,
            pto_balance_hours=pending_employee.requested_pto_balance
        )
        
        # Update pending employee status
        pending_employee.status = 'approved'
        pending_employee.approved_at = datetime.utcnow()
        pending_employee.approved_by_id = current_user.id
        
        # Save to database
        db.session.add(new_employee)
        db.session.commit()
        
        # Send approval notification to employee
        send_employee_approved_email(pending_employee, new_employee)
        
        flash(f'Employee registration for {pending_employee.name} approved successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error approving employee registration: {str(e)}', 'error')
    
    return redirect(url_for('pending_employees'))

@app.route('/deny_employee/<int:employee_id>', methods=['POST'])
@roles_required('admin', 'clinical', 'superadmin', 'moa_supervisor', 'echo_supervisor')
def deny_employee(employee_id):
    """Deny a pending employee registration"""
    pending_employee = PendingEmployee.query.get_or_404(employee_id)
    current_user = get_current_user()
    
    # Check permissions
    can_deny = False
    if current_user.role == 'superadmin':
        can_deny = True
    elif current_user.role == 'admin' and pending_employee.team == 'admin':
        can_deny = True
    elif current_user.role == 'clinical' and pending_employee.team == 'clinical':
        can_deny = True
    
    if not can_deny:
        flash('You do not have permission to deny this employee registration.', 'error')
        return redirect(url_for('pending_employees'))
    
    if pending_employee.status != 'pending':
        flash('This employee registration has already been processed.', 'warning')
        return redirect(url_for('pending_employees'))
    
    try:
        denial_reason = request.form.get('denial_reason', 'No reason provided')
        
        # Update pending employee status
        pending_employee.status = 'denied'
        pending_employee.denial_reason = denial_reason
        pending_employee.approved_at = datetime.utcnow()
        pending_employee.approved_by_id = current_user.id
        
        db.session.commit()
        
        # Send denial notification to employee
        send_employee_denied_email(pending_employee)
        
        flash(f'Employee registration for {pending_employee.name} denied.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error denying employee registration: {str(e)}', 'error')
    
    return redirect(url_for('pending_employees'))

def send_employee_approved_email(pending_employee, new_employee):
    """Send approval notification to employee"""
    try:
        subject = f"Employee Registration Approved - Welcome to MSW CVI!"
        body = f"""Dear {pending_employee.name},

Great news! Your employee registration has been approved.

Registration Details:
- Name: {pending_employee.name}
- Email: {pending_employee.email}
- Team: {pending_employee.team.title()}
- Position: {pending_employee.position}
- PTO Balance: {new_employee.pto_balance_days} days ({new_employee.pto_balance_hours} hours)

You can now submit PTO requests using the online system:
http://localhost:5000

Thank you for joining our team!

Best regards,
MSW CVI PTO System
"""
        
        send_submission_email({
            'name': pending_employee.name,
            'email': pending_employee.email,
            'subject_override': subject,
            'body_override': body
        }, f"APPROVED_{pending_employee.id}")
        
    except Exception as e:
        print(f"Error sending approval email: {e}")

def send_employee_denied_email(pending_employee):
    """Send denial notification to employee"""
    try:
        subject = f"Employee Registration - Additional Information Required"
        body = f"""Dear {pending_employee.name},

Thank you for submitting your employee registration. We need some additional information before we can process your request.

Registration Details:
- Name: {pending_employee.name}
- Email: {pending_employee.email}
- Team: {pending_employee.team.title()}
- Position: {pending_employee.position}

Manager's Comments: {pending_employee.denial_reason}

Please contact your supervisor to provide the additional information needed.

Best regards,
MSW CVI PTO System
"""
        
        send_submission_email({
            'name': pending_employee.name,
            'email': pending_employee.email,
            'subject_override': subject,
            'body_override': body
        }, f"DENIED_{pending_employee.id}")
        
    except Exception as e:
        print(f"Error sending denial email: {e}")

@app.route('/calendar')
def calendar():
    """Calendar view of PTO requests"""
    # Get all requests that should be displayed on calendar
    requests = PTORequest.query.filter(PTORequest.status.in_(['pending', 'approved'])).all()
    
    # Prepare calendar events data
    events = []
    for req in requests:
        # Determine event color based on status
        if req.status == 'approved':
            color = '#28a745'  # Green
        elif req.status == 'pending':
            color = '#ffc107'  # Yellow
        else:
            color = '#6c757d'  # Gray
            
        # Create event object
        event = {
            'id': req.id,
            'title': f"{req.member.name if req.member else 'Unknown'} - {req.pto_type}",
            'start': str(req.start_date),
            'end': str(req.end_date),
            'color': color,
            'extendedProps': {
                'employee': req.member.name if req.member else 'Unknown',
                'type': req.pto_type,
                'status': req.status,
                'team': req.member.team if req.member else 'N/A',
                'employee_position': req.member.position if req.member else 'N/A',
                'duration': req.duration_days if not req.is_partial_day else f"{req.duration_hours} hours",
                'is_partial_day': req.is_partial_day,
                'reason': req.reason
            }
        }
        
        # For partial day requests, add time information
        if req.is_partial_day and req.start_time and req.end_time:
            event['start'] = f"{req.start_date}T{req.start_time}"
            event['end'] = f"{req.end_date}T{req.end_time}"
            event['title'] = f"{req.member.name if req.member else 'Unknown'} - {req.pto_type} (Partial)"
        
        events.append(event)
    
    return render_template('calendar.html', requests=requests, calendar_events=events)

@app.route('/not_authorized')
def not_authorized():
    """Page shown when user doesn't have permission"""
    return render_template('not_authorized.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500