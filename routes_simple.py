from flask import render_template, request, redirect, url_for, flash, jsonify, session
from database import db
from models import PTORequest, TeamMember, Manager, User, PendingEmployee, Position
from pto_system import PTOTrackerSystem
from auth import roles_required, authenticate_user, login_user, logout_user, get_current_user
from datetime import datetime

def register_routes(app):
    # Initialize the PTO system
    pto_system = PTOTrackerSystem()

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

        # Get approved requests this month for admin team
        from datetime import datetime, timedelta
        current_month_start = datetime.now().replace(day=1)
        approved_this_month = PTORequest.query.filter_by(status='approved', manager_team='admin').filter(
            PTORequest.updated_at >= current_month_start
        ).count()

        # Get total and denied counts
        total_requests = PTORequest.query.filter_by(manager_team='admin').count()
        denied_requests = PTORequest.query.filter_by(status='denied', manager_team='admin').count()

        stats = {
            'pending': len(pending_requests),
            'approved_this_month': approved_this_month,
            'total': total_requests,
            'denied': denied_requests
        }

        return render_template('dashboard_admin.html', requests=pending_requests, stats=stats)

    @app.route('/dashboard/clinical')
    @roles_required('clinical', 'superadmin')
    def clinical_dashboard():
        """Clinical dashboard"""
        requests = pto_system.get_requests_by_team('clinical')
        return render_template('dashboard_clinical.html', requests=requests)

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

    @app.route('/submit_request', methods=['POST'])
    def submit_request():
        """Handle PTO request submission or new employee registration"""
        try:
            # Get form data
            team = request.form.get('team')
            position = request.form.get('position')
            name = request.form.get('name')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            pto_type = request.form.get('pto_type')
            reason = request.form.get('reason')

            # Find the team member by name and position
            member = TeamMember.query.join(Position).filter(
                TeamMember.name == name,
                Position.name == position,
                Position.team == team
            ).first()

            if not member:
                flash(f'Employee {name} not found in {team} team', 'error')
                return redirect(url_for('index'))

            # Create PTO request with proper member relationship
            pto_request = PTORequest(
                member_id=member.id,
                start_date=start_date,
                end_date=end_date,
                pto_type=pto_type,
                reason=reason,
                manager_team=team,
                status='pending'
            )

            db.session.add(pto_request)
            db.session.commit()

            flash(f'PTO request submitted successfully for {name}!', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            flash(f'Error submitting PTO request: {str(e)}', 'error')
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
            # Determine colors based on status
            color = '#28a745' if request.status == 'approved' else '#ffc107'
            text_color = '#fff' if request.status == 'approved' else '#000'

            # Calculate duration in business days
            try:
                duration = request.duration_days  # This now uses business days calculation
            except:
                duration = 1

            # Create event for FullCalendar
            event = {
                'id': f'pto-{request.id}',
                'title': f'{request.member.name} - {request.pto_type}',
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
        stats = {
            'total_employees': len(team_members),
            'total_pto_hours': sum(member.pto_balance_hours or 0 for member in team_members)
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
        employee = TeamMember.query.get_or_404(employee_id)
        return render_template('employee_detail.html', employee=employee)

    @app.route('/employee/edit/<int:employee_id>', methods=['GET', 'POST'])
    @roles_required('admin', 'clinical', 'superadmin')
    def edit_employee(employee_id):
        """Edit employee details"""
        employee = TeamMember.query.get_or_404(employee_id)

        if request.method == 'POST':
            try:
                employee.name = request.form.get('name')
                employee.email = request.form.get('email')
                employee.phone = request.form.get('phone')  # Add phone field
                pto_balance = float(request.form.get('pto_balance', employee.pto_balance_hours))
                employee.pto_balance_hours = pto_balance

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
        """Approve a PTO request"""
        try:
            pto_request = PTORequest.query.get_or_404(request_id)
            pto_request.status = 'approved'
            pto_request.updated_at = datetime.now()

            db.session.commit()
            flash(f'PTO request for {pto_request.member.name} has been approved!', 'success')

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
            pto_request.updated_at = datetime.now()
            pto_request.denial_reason = denial_reason

            db.session.commit()
            flash(f'PTO request for {pto_request.member.name} has been denied.', 'warning')

        except Exception as e:
            flash(f'Error denying request: {str(e)}', 'error')

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