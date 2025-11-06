from flask import render_template, request, redirect, url_for, flash, jsonify, session
from database import db
from models import PTORequest, TeamMember, Manager, User, PendingEmployee, Position
from pto_system import PTOTrackerSystem
from auth import roles_required, authenticate_user, login_user, logout_user, get_current_user
from datetime import datetime
import pytz
from email_service import EmailService

# Define Eastern timezone
EASTERN = pytz.timezone('US/Eastern')

def get_eastern_time():
    """Get current time in Eastern timezone as naive datetime"""
    eastern_now = datetime.now(EASTERN)
    # Return naive datetime (no timezone info) but in Eastern time
    return eastern_now.replace(tzinfo=None)

def register_routes(app):
    # Initialize the PTO system
    pto_system = PTOTrackerSystem()
    # Initialize the email service
    email_service = EmailService()

    @app.route('/')
    def index():
        """Main page for submitting PTO requests"""
        staff_directory = pto_system.get_staff_directory()
        return render_template('index.html', staff_directory=staff_directory)

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

    @app.route('/dashboard')
    @roles_required('admin', 'clinical', 'superadmin', 'moa_supervisor', 'echo_supervisor')
    def dashboard():
        """Redirect to appropriate dashboard based on user role"""
        user_role = session.get('user_role')
        if user_role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif user_role == 'clinical':
            return redirect(url_for('clinical_dashboard'))
        elif user_role == 'superadmin':
            return redirect(url_for('superadmin_dashboard'))
        else:
            return redirect(url_for('index'))

    @app.route('/dashboard/admin')
    @roles_required('admin', 'superadmin')
    def admin_dashboard():
        """Admin dashboard"""
        # Get pending requests for admin team (using manager_team field)
        pending_requests = PTORequest.query.filter_by(status='pending', manager_team='admin').all()

        # Get approved requests for admin team
        approved_requests = PTORequest.query.filter_by(status='approved', manager_team='admin').all()

        # Get in_progress requests for admin team
        in_progress_requests = PTORequest.query.filter_by(status='in_progress', manager_team='admin').all()

        # Get pending employee registrations for admin team
        pending_employees = PendingEmployee.query.filter_by(status='pending', team='admin').all()

        # Get approved requests this month for admin team
        from datetime import datetime, timedelta
        current_month_start = get_eastern_time().replace(day=1)
        approved_this_month = PTORequest.query.filter_by(status='approved', manager_team='admin').filter(
            PTORequest.updated_at >= current_month_start
        ).count()

        # Get total and denied counts
        total_requests = PTORequest.query.filter_by(manager_team='admin').count()
        denied_requests = PTORequest.query.filter_by(status='denied', manager_team='admin').count()

        stats = {
            'pending': len(pending_requests),
            'pending_employees': len(pending_employees),
            'approved_this_month': approved_this_month,
            'total': total_requests,
            'denied': denied_requests,
            'in_progress': len(in_progress_requests),
            'approved': len(approved_requests)
        }

        return render_template('dashboard_admin.html',
                               requests=pending_requests,
                               approved_requests=approved_requests,
                               in_progress_requests=in_progress_requests,
                               pending_employees=pending_employees,
                               stats=stats,
                               now=get_eastern_time)

    @app.route('/dashboard/clinical')
    @roles_required('clinical', 'superadmin')
    def clinical_dashboard():
        """Clinical dashboard"""
        # Get pending requests for clinical team (using manager_team field)
        pending_requests = PTORequest.query.filter_by(status='pending', manager_team='clinical').all()

        # Get approved requests for clinical team
        approved_requests = PTORequest.query.filter_by(status='approved', manager_team='clinical').all()

        # Get in_progress requests for clinical team
        in_progress_requests = PTORequest.query.filter_by(status='in_progress', manager_team='clinical').all()

        # Get pending employee registrations for clinical team
        pending_employees = PendingEmployee.query.filter_by(status='pending', team='clinical').all()

        # Get approved requests this month for clinical team
        from datetime import datetime, timedelta
        current_month_start = get_eastern_time().replace(day=1)
        approved_this_month = PTORequest.query.filter_by(status='approved', manager_team='clinical').filter(
            PTORequest.updated_at >= current_month_start
        ).count()

        # Get total and denied counts
        total_requests = PTORequest.query.filter_by(manager_team='clinical').count()
        denied_requests = PTORequest.query.filter_by(status='denied', manager_team='clinical').count()

        stats = {
            'pending': len(pending_requests),
            'pending_employees': len(pending_employees),
            'approved_this_month': approved_this_month,
            'total': total_requests,
            'denied': denied_requests,
            'in_progress': len(in_progress_requests),
            'approved': len(approved_requests)
        }

        return render_template('dashboard_clinical.html',
                               requests=pending_requests,
                               approved_requests=approved_requests,
                               in_progress_requests=in_progress_requests,
                               pending_employees=pending_employees,
                               stats=stats,
                               now=get_eastern_time)

    @app.route('/dashboard/superadmin')
    @roles_required('superadmin')
    def superadmin_dashboard():
        """Super admin dashboard"""
        requests = pto_system.get_all_requests()
        team_members = TeamMember.query.all()
        return render_template('dashboard_superadmin.html', requests=requests, team_members=team_members)

    @app.route('/api/staff-directory')
    def api_staff_directory():
        """API endpoint to get current staff directory"""
        staff_directory = pto_system.get_staff_directory()

        # Ensure all team/position combinations exist even if empty
        positions_by_team = {}
        for p in Position.query.all():
            if p.team not in positions_by_team:
                positions_by_team[p.team] = []
            positions_by_team[p.team].append(p.name)

        # Add empty position structures if they don't exist in staff directory
        for team, positions in positions_by_team.items():
            if team not in staff_directory:
                staff_directory[team] = {}
            for position in positions:
                if position not in staff_directory[team]:
                    staff_directory[team][position] = []

        return jsonify(staff_directory)

    @app.route('/api/positions')
    def api_positions():
        """API endpoint to get all available positions"""
        positions = {}
        for p in Position.query.all():
            if p.team not in positions:
                positions[p.team] = []
            positions[p.team].append(p.name)
        return jsonify(positions)

    @app.route('/api/callout-details/<int:request_id>')
    def api_callout_details(request_id):
        """API endpoint to get call-out details for a specific PTO request"""
        try:
            # Get the PTO request
            pto_request = PTORequest.query.get(request_id)
            if not pto_request or not pto_request.is_call_out:
                return jsonify({'success': False, 'message': 'Call-out not found'}), 404

            # Get the associated call-out record
            from models import CallOutRecord
            callout_record = CallOutRecord.query.filter_by(pto_request_id=request_id).first()

            if not callout_record:
                return jsonify({'success': False, 'message': 'Call-out details not found'}), 404

            # Prepare call-out data
            callout_data = {
                'source': callout_record.source,
                'phone_number': callout_record.phone_number_used,
                'authentication_method': callout_record.authentication_method,
                'verified': callout_record.verified,
                'message_text': callout_record.message_text,
                'created_at': callout_record.created_at.strftime('%m/%d/%Y %I:%M %p') if callout_record.created_at else None,
                'call_sid': callout_record.call_sid
            }

            return jsonify({'success': True, 'callout': callout_data})

        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/submit_request', methods=['POST'])
    def submit_request():
        """Handle PTO request submission or new employee registration"""
        try:
            # Check if this is a new employee registration
            if request.form.get('name') == 'NOT_LISTED':
                # Handle new employee registration
                new_employee_name = request.form.get('new_employee_name')
                new_employee_email = request.form.get('new_employee_email')
                new_employee_team = request.form.get('new_employee_team')
                new_employee_position = request.form.get('new_employee_position')
                employee_notes = request.form.get('employee_notes', '')

                # Validate required fields
                if not all([new_employee_name, new_employee_email, new_employee_team, new_employee_position]):
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
                    team=new_employee_team,
                    position=new_employee_position,
                    status='pending'
                )

                # Add notes if provided
                if employee_notes:
                    pending_employee.denial_reason = f"Registration Notes: {employee_notes}"  # Using this field for notes

                db.session.add(pending_employee)
                db.session.commit()

                flash(f'Employee registration for {new_employee_name} has been submitted and will be reviewed by the {new_employee_team} team manager.', 'success')
                return redirect(url_for('index'))

            # Regular PTO request handling
            team = request.form.get('team')
            position = request.form.get('position')
            name = request.form.get('name')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            pto_type = request.form.get('pto_type')
            reason = request.form.get('reason')

            # Check if this is a call-out request
            call_out_flag = request.form.get('call_out', '0') == '1'

            # Find the team member by name and position
            member = TeamMember.query.join(Position).filter(
                TeamMember.name == name,
                Position.name == position,
                Position.team == team
            ).first()

            if not member:
                flash(f'Employee {name} not found in {team} team', 'error')
                return redirect(url_for('index'))

            # Server-side validation for call-out requests
            if call_out_flag:
                if pto_type != 'Sick Leave':
                    flash('Call-out requests must use PTO Type: Sick Leave.', 'error')
                    return redirect(url_for('index'))

                if not reason or reason.strip() == '':
                    flash('Please provide a reason for calling out sick.', 'error')
                    return redirect(url_for('index'))

            # Create PTO request with proper member relationship
            # Call-outs are auto-approved, regular PTO is pending
            pto_request = PTORequest(
                member_id=member.id,
                start_date=start_date,
                end_date=end_date,
                pto_type=pto_type,
                reason=reason,
                manager_team=team,
                is_call_out=call_out_flag,
                status='approved' if call_out_flag else 'pending'
            )

            db.session.add(pto_request)
            db.session.commit()

            # If call-out, automatically deduct from sick balance
            if call_out_flag:
                hours_to_deduct = pto_request.duration_hours
                current_sick_balance = float(member.sick_balance_hours)
                new_sick_balance = max(0, current_sick_balance - hours_to_deduct)
                member.sick_balance_hours = new_sick_balance
                db.session.commit()

            # Send email notification for PTO submission
            try:
                email_service.send_submission_email(pto_request)
            except Exception as e:
                # Log error but don't fail the request
                print(f"Failed to send submission email: {str(e)}")

            # Different success message for call-out vs regular PTO
            if call_out_flag:
                flash(f'Call-out submitted successfully for {name}! Request ID: #{pto_request.id}', 'success')
            else:
                flash(f'PTO request submitted successfully for {name}! Request ID: #{pto_request.id}', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            flash(f'Error submitting request: {str(e)}', 'error')
            return redirect(url_for('index'))

    @app.route('/calendar')
    def calendar():
        """Calendar view of PTO requests"""
        # Get all PTO requests (approved and pending) for calendar display
        all_requests = PTORequest.query.filter(
            PTORequest.status.in_(['approved', 'pending'])
        ).all()

        # Convert PTO requests to FullCalendar events format
        calendar_events = []
        for request in all_requests:
            # Determine colors based on call-out status first, then regular status
            if request.is_call_out:
                color = '#dc3545'  # Red for call-outs
                text_color = '#fff'
            elif request.status == 'approved':
                color = '#28a745'  # Green for approved PTO
                text_color = '#fff'
            elif request.status == 'pending':
                color = '#ffc107'  # Yellow for pending PTO
                text_color = '#000'
            else:
                color = '#6c757d'  # Gray for other statuses
                text_color = '#fff'

            # Calculate duration in business days
            try:
                duration = request.duration_days  # This now uses business days calculation
            except:
                duration = 1

            # Determine title based on call-out status
            if request.is_call_out:
                title = f"Call Out - {request.member.name}"
            else:
                title = f'{request.member.name} - {request.pto_type}'

            # Create event for FullCalendar
            event = {
                'id': f'pto-{request.id}',
                'title': title,
                'start': request.start_date,
                'end': request.end_date,
                'backgroundColor': color,
                'borderColor': color,
                'textColor': text_color,
                'extendedProps': {
                    'employee': request.member.name,
                    'employee_position': request.member.position.name if request.member.position else 'Unknown',
                    'team': request.member.position.team if request.member.position else 'unknown',
                    'type': request.pto_type,
                    'status': request.status,
                    'reason': request.reason or '',
                    'duration': duration,
                    'is_partial_day': request.is_partial_day,
                    'is_call_out': request.is_call_out,
                    'request_id': request.id
                }
            }
            calendar_events.append(event)

        return render_template('calendar.html', requests=all_requests, calendar_events=calendar_events)

    @app.route('/api/test-business-days')
    def test_business_days():
        """API endpoint to test business days calculations"""
        try:
            from business_days import BusinessDaysCalculator, get_pto_breakdown

            # Test cases demonstrating business days calculation
            test_cases = [
                {
                    'name': 'Thursday to Tuesday (includes weekend)',
                    'start_date': '2025-09-18',
                    'end_date': '2025-09-23',
                    'expected_business_days': 4
                },
                {
                    'name': 'Christmas period (includes holiday)',
                    'start_date': '2025-12-24',
                    'end_date': '2025-12-26',
                    'expected_business_days': 2
                },
                {
                    'name': 'Thanksgiving (includes holiday)',
                    'start_date': '2025-11-27',
                    'end_date': '2025-11-28',
                    'expected_business_days': 1
                },
                {
                    'name': 'July 4th weekend',
                    'start_date': '2025-07-03',
                    'end_date': '2025-07-07',
                    'expected_business_days': 3
                }
            ]

            results = []
            for case in test_cases:
                breakdown = get_pto_breakdown(case['start_date'], case['end_date'])
                results.append({
                    'test_case': case['name'],
                    'date_range': f"{case['start_date']} to {case['end_date']}",
                    'total_days': breakdown['total_days'],
                    'business_days': breakdown['business_days'],
                    'weekend_days': breakdown['weekend_days'],
                    'holiday_days': breakdown['holiday_days'],
                    'holidays': [h.strftime('%Y-%m-%d') for h in breakdown['holidays_list']],
                    'expected_business_days': case['expected_business_days'],
                    'calculation_correct': breakdown['business_days'] == case['expected_business_days']
                })

            return jsonify({
                'success': True,
                'message': 'Business days calculator test results',
                'test_results': results
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            })

    @app.route('/dashboard/moa_supervisor')
    @roles_required('moa_supervisor', 'superadmin')
    def moa_supervisor_dashboard():
        """MOA Supervisor dashboard"""
        return render_template('dashboard_moa_supervisor.html', requests=[])

    @app.route('/dashboard/echo_supervisor')
    @roles_required('echo_supervisor', 'superadmin')
    def echo_supervisor_dashboard():
        """Echo Supervisor dashboard"""
        return render_template('dashboard_echo_supervisor.html', requests=[])

    @app.route('/employees')
    @roles_required('admin', 'clinical', 'superadmin', 'moa_supervisor', 'echo_supervisor')
    def employees():
        """Employee management page"""
        team_members = TeamMember.query.all()

        # Calculate comprehensive statistics
        active_employees = [m for m in team_members if '[INACTIVE]' not in m.name]
        total_pto_hours = sum(float(member.pto_balance_hours or 0) for member in team_members)
        total_pto_days = total_pto_hours / 7.5  # Convert hours to days
        avg_pto_days = total_pto_days / len(team_members) if team_members else 0

        stats = {
            'total_employees': len(team_members),
            'active_employees': len(active_employees),
            'total_pto_hours': total_pto_hours,
            'total_pto_days': round(total_pto_days, 1),
            'avg_pto_days': round(avg_pto_days, 1)
        }
        return render_template('employees.html', team_members=team_members, stats=stats)

    @app.route('/pending_employees')
    @roles_required('admin', 'clinical', 'superadmin')
    def pending_employees():
        """View pending employee registrations"""
        pending_employees = PendingEmployee.query.all()
        total_pending = len(pending_employees)
        return render_template('pending_employees.html', pending_employees=pending_employees, total_pending=total_pending)

    @app.route('/add_employee', methods=['GET', 'POST'])
    @roles_required('admin', 'clinical', 'superadmin')
    def add_employee():
        """Add new employee"""
        print(f"DEBUG: add_employee called with method: {request.method}")
        print(f"DEBUG: Form data: {dict(request.form)}")

        if request.method == 'POST':
            try:
                # Get team first since position depends on it
                team = request.form.get('team')
                position = request.form.get('position')

                print(f"DEBUG: Selected team: {team}, position: {position}")

                employee_data = {
                    'name': request.form.get('name'),
                    'email': request.form.get('email'),
                    'team': team,
                    'position': position,
                    'pto_balance': float(request.form.get('pto_balance', 60.0)),
                    'pto_refresh_date': request.form.get('pto_refresh_date')
                }

                print(f"DEBUG: Employee data: {employee_data}")
                pto_system.add_employee(employee_data)
                flash(f'Employee {employee_data["name"]} added successfully!', 'success')
                return redirect(url_for('employees'))

            except ValueError as e:
                print(f"DEBUG: ValueError: {str(e)}")
                flash(str(e), 'error')
                return render_template('add_employee.html')
            except Exception as e:
                print(f"DEBUG: Exception: {str(e)}")
                flash(f'Error adding employee: {str(e)}', 'error')
                return render_template('add_employee.html')

        return render_template('add_employee.html')

    @app.route('/employee/<int:employee_id>')
    @roles_required('admin', 'clinical', 'superadmin', 'moa_supervisor', 'echo_supervisor')
    def employee_detail(employee_id):
        """View employee details"""
        from datetime import datetime, timedelta

        employee = TeamMember.query.get_or_404(employee_id)

        # Get all PTO requests for this employee
        pto_requests = PTORequest.query.filter_by(member_id=employee_id).order_by(PTORequest.created_at.desc()).all()

        # Calculate statistics
        total_requests = len(pto_requests)
        approved_requests = len([r for r in pto_requests if r.status == 'approved'])
        pending_requests = len([r for r in pto_requests if r.status == 'pending'])
        denied_requests = len([r for r in pto_requests if r.status == 'denied'])

        # Calculate call-out statistics
        total_callouts = len([r for r in pto_requests if r.is_call_out])
        approved_callouts = len([r for r in pto_requests if r.is_call_out and r.status == 'approved'])
        pending_callouts = len([r for r in pto_requests if r.is_call_out and r.status == 'pending'])

        # Calculate PTO days used (approved non-call-out requests)
        total_pto_used = sum(r.duration_days for r in pto_requests
                            if r.status == 'approved' and not r.is_call_out)

        # Calculate sick days used (approved call-outs)
        total_callouts_used = sum(r.duration_days for r in pto_requests
                                 if r.status == 'approved' and r.is_call_out)

        # Calculate days until PTO refresh
        if employee.pto_refresh_date:
            today = datetime.now().date()
            refresh_date = employee.pto_refresh_date
            if refresh_date < today:
                # If refresh date has passed, calculate next year's refresh
                refresh_date = datetime(today.year + 1, refresh_date.month, refresh_date.day).date()
            days_until_refresh = (refresh_date - today).days
        else:
            days_until_refresh = None

        stats = {
            'total_requests': total_requests,
            'approved_requests': approved_requests,
            'pending_requests': pending_requests,
            'denied_requests': denied_requests,
            'total_callouts': total_callouts,
            'approved_callouts': approved_callouts,
            'pending_callouts': pending_callouts,
            'total_pto_used': round(total_pto_used, 1),
            'total_callouts_used': round(total_callouts_used, 1),
            'days_until_refresh': days_until_refresh
        }

        return render_template('employee_detail.html', employee=employee, pto_requests=pto_requests, stats=stats)

    @app.route('/employee/edit/<int:employee_id>', methods=['GET', 'POST'])
    @roles_required('admin', 'clinical', 'superadmin')
    def edit_employee(employee_id):
        """Edit employee details"""
        employee = TeamMember.query.get_or_404(employee_id)

        if request.method == 'POST':
            try:
                employee.name = request.form.get('name')
                employee.email = request.form.get('email')
                employee.phone = request.form.get('phone')

                # Update PTO balance
                pto_balance = float(request.form.get('pto_balance', employee.pto_balance_hours))
                employee.pto_balance_hours = pto_balance

                # Update sick balance
                sick_balance = float(request.form.get('sick_balance', employee.sick_balance_hours))
                employee.sick_balance_hours = sick_balance

                db.session.commit()
                flash(f'Employee {employee.name} updated successfully!', 'success')
                return redirect(url_for('employees'))
            except Exception as e:
                flash(f'Error updating employee: {str(e)}', 'error')

        return render_template('edit_employee.html', employee=employee)

    @app.route('/employee/delete/<int:employee_id>', methods=['POST'])
    @roles_required('admin', 'clinical', 'superadmin')
    def delete_employee(employee_id):
        """Delete or deactivate employee"""
        employee = TeamMember.query.get_or_404(employee_id)

        try:
            # Check if employee has PTO requests
            has_pto_history = PTORequest.query.filter_by(member_id=employee.id).first() is not None

            if has_pto_history:
                # Mark as inactive instead of deleting
                if '[INACTIVE]' not in employee.name:
                    employee.name = f'[INACTIVE] {employee.name}'
                    db.session.commit()
                    flash(f'Employee {employee.name} marked as inactive due to PTO history.', 'info')
            else:
                # Safe to delete
                db.session.delete(employee)
                db.session.commit()
                flash(f'Employee {employee.name} deleted successfully.', 'success')

        except Exception as e:
            flash(f'Error deleting employee: {str(e)}', 'error')

        return redirect(url_for('employees'))

    @app.route('/approve_request/<int:request_id>')
    @roles_required('admin', 'clinical', 'superadmin', 'moa_supervisor', 'echo_supervisor')
    def approve_request(request_id):
        """Approve a PTO request and move to in_progress"""
        try:
            pto_request = PTORequest.query.get_or_404(request_id)
            pto_request.status = 'in_progress'  # Move to in_progress, not directly to approved
            pto_request.approved_date = get_eastern_time()
            pto_request.updated_at = get_eastern_time()

            db.session.commit()

            # Send email notification for approval
            try:
                email_service.send_approval_email(pto_request)
            except Exception as e:
                # Log error but don't fail the request
                print(f"Failed to send approval email: {str(e)}")

            flash(f'PTO request for {pto_request.member.name} has been approved and moved to In Progress!', 'success')

        except Exception as e:
            flash(f'Error approving request: {str(e)}', 'error')

        return redirect(url_for('dashboard'))

    @app.route('/deny_request/<int:request_id>', methods=['POST'])
    @roles_required('admin', 'clinical', 'superadmin', 'moa_supervisor', 'echo_supervisor')
    def deny_request(request_id):
        """Deny a PTO request"""
        try:
            pto_request = PTORequest.query.get_or_404(request_id)
            denial_reason = request.form.get('denial_reason', 'No reason provided')

            pto_request.status = 'denied'
            pto_request.updated_at = get_eastern_time()
            pto_request.denial_reason = denial_reason

            db.session.commit()

            # Send email notification for denial
            try:
                email_service.send_denial_email(pto_request, denial_reason)
            except Exception as e:
                # Log error but don't fail the request
                print(f"Failed to send denial email: {str(e)}")

            flash(f'PTO request for {pto_request.member.name} has been denied.', 'warning')

        except Exception as e:
            flash(f'Error denying request: {str(e)}', 'error')

        return redirect(url_for('dashboard'))

    @app.route('/approve_employee/<int:employee_id>')
    @roles_required('admin', 'clinical', 'superadmin')
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
            flash('You do not have permission to approve this employee.', 'error')
            return redirect(url_for('dashboard'))

        # Find or create the position
        position = Position.query.filter_by(name=pending_employee.position, team=pending_employee.team).first()
        if not position:
            position = Position(name=pending_employee.position, team=pending_employee.team)
            db.session.add(position)
            db.session.flush()

        # Create the new team member
        new_member = TeamMember(
            name=pending_employee.name,
            email=pending_employee.email,
            position_id=position.id,
            pto_balance_hours=60.0  # Default PTO balance
        )

        # Update pending employee status
        pending_employee.status = 'approved'
        pending_employee.approved_at = get_eastern_time()
        pending_employee.approved_by_id = current_user.id

        db.session.add(new_member)
        db.session.commit()

        flash(f'Employee {pending_employee.name} has been approved and added to the {pending_employee.team} team.', 'success')
        return redirect(url_for('dashboard'))

    @app.route('/deny_employee/<int:employee_id>', methods=['POST'])
    @roles_required('admin', 'clinical', 'superadmin')
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
            flash('You do not have permission to deny this employee.', 'error')
            return redirect(url_for('dashboard'))

        # Update pending employee status
        pending_employee.status = 'denied'
        pending_employee.approved_at = get_eastern_time()
        pending_employee.approved_by_id = current_user.id

        # Add denial reason if provided
        denial_reason = request.form.get('denial_reason', '')
        if denial_reason:
            pending_employee.denial_reason = denial_reason

        db.session.commit()

        flash(f'Employee registration for {pending_employee.name} has been denied.', 'info')
        return redirect(url_for('dashboard'))

    @app.route('/workqueue/in_progress')
    @roles_required('admin', 'clinical', 'superadmin')
    def workqueue_in_progress():
        """View in-progress PTO requests with checklist"""
        current_user = get_current_user()

        # Get in-progress requests based on role
        if current_user.role == 'superadmin':
            in_progress_requests = PTORequest.query.filter_by(status='in_progress').all()
        elif current_user.role == 'admin':
            in_progress_requests = PTORequest.query.filter_by(status='in_progress', manager_team='admin').all()
        elif current_user.role == 'clinical':
            in_progress_requests = PTORequest.query.filter_by(status='in_progress', manager_team='clinical').all()
        else:
            in_progress_requests = []

        return render_template('workqueue_in_progress.html', requests=in_progress_requests, now=get_eastern_time)

    @app.route('/workqueue/approved')
    @roles_required('admin', 'clinical', 'superadmin')
    def workqueue_approved():
        """View approved PTO requests"""
        current_user = get_current_user()

        # Get approved requests based on role
        if current_user.role == 'superadmin':
            approved_requests = PTORequest.query.filter_by(status='approved').all()
        elif current_user.role == 'admin':
            approved_requests = PTORequest.query.filter_by(status='approved', manager_team='admin').all()
        elif current_user.role == 'clinical':
            approved_requests = PTORequest.query.filter_by(status='approved', manager_team='clinical').all()
        else:
            approved_requests = []

        from datetime import datetime
        return render_template('workqueue_approved.html', requests=approved_requests, now=get_eastern_time, datetime=datetime)

    @app.route('/workqueue/completed')
    @roles_required('admin', 'clinical', 'superadmin')
    def workqueue_completed():
        """View completed PTO requests"""
        current_user = get_current_user()

        # Get completed requests based on role
        if current_user.role == 'superadmin':
            completed_requests = PTORequest.query.filter_by(status='completed').all()
        elif current_user.role == 'admin':
            completed_requests = PTORequest.query.filter_by(status='completed', manager_team='admin').all()
        elif current_user.role == 'clinical':
            completed_requests = PTORequest.query.filter_by(status='completed', manager_team='clinical').all()
        else:
            completed_requests = []

        return render_template('workqueue_completed.html', requests=completed_requests, now=get_eastern_time)

    @app.route('/update_checklist/<int:request_id>', methods=['POST'])
    @roles_required('admin', 'clinical', 'superadmin')
    def update_checklist(request_id):
        """Update checklist items for in-progress request"""
        pto_request = PTORequest.query.get_or_404(request_id)

        # Update checklist items
        pto_request.timekeeping_entered = request.form.get('timekeeping_entered') == 'on'
        pto_request.coverage_arranged = request.form.get('coverage_arranged') == 'on'

        # If both are complete, move to approved status
        if pto_request.timekeeping_entered and pto_request.coverage_arranged:
            pto_request.status = 'approved'
            flash(f'PTO request for {pto_request.member.name} is now fully approved!', 'success')

            # No email sent when checklist is completed (per updated requirements)

        pto_request.updated_at = get_eastern_time()
        db.session.commit()

        return redirect(url_for('workqueue_in_progress'))

    @app.route('/check_and_complete_requests')
    def check_and_complete_requests():
        """Check for PTO requests that should be marked as completed based on end date"""
        from datetime import datetime, date

        today = date.today()

        # Find approved requests where end date has passed
        approved_requests = PTORequest.query.filter_by(status='approved').all()

        completed_count = 0
        for request in approved_requests:
            try:
                end_date = datetime.strptime(request.end_date, '%Y-%m-%d').date()
                if end_date < today:
                    request.status = 'completed'
                    request.completed_date = get_eastern_time()
                    completed_count += 1
            except:
                pass

        if completed_count > 0:
            db.session.commit()
            flash(f'{completed_count} PTO requests marked as completed.', 'info')

        return redirect(url_for('dashboard'))

    @app.route('/logout')
    def logout():
        """Logout current user"""
        from auth import logout_user
        logout_user()
        flash('You have been logged out.', 'success')
        return redirect(url_for('index'))

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500