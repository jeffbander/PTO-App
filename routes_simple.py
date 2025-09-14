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
        requests = pto_system.get_requests_by_team('admin')
        return render_template('dashboard_admin.html', requests=requests)

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
        flash('PTO request submission is under maintenance.', 'warning')
        return redirect(url_for('index'))

    @app.route('/calendar')
    def calendar():
        """Calendar view of PTO requests"""
        return render_template('calendar.html', requests=[], calendar_events=[])

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
        return render_template('employees.html', team_members=[], stats={})

    @app.route('/pending_employees')
    @roles_required('admin', 'clinical', 'superadmin')
    def pending_employees():
        """View pending employee registrations"""
        return render_template('pending_employees.html', pending_employees=[], total_pending=0)

    @app.route('/add_employee', methods=['GET'])
    @roles_required('admin', 'clinical', 'superadmin')
    def add_employee():
        """Add new employee form"""
        return render_template('add_employee.html')

    @app.route('/approve_request/<int:request_id>')
    @roles_required('admin', 'clinical', 'superadmin', 'moa_supervisor', 'echo_supervisor')
    def approve_request(request_id):
        """Approve a PTO request"""
        flash('Request approval is under maintenance.', 'warning')
        return redirect(url_for('dashboard'))

    @app.route('/deny_request/<int:request_id>', methods=['POST'])
    @roles_required('admin', 'clinical', 'superadmin', 'moa_supervisor', 'echo_supervisor')
    def deny_request(request_id):
        """Deny a PTO request"""
        flash('Request denial is under maintenance.', 'warning')
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