from models import PTORequest, TeamMember, Manager, Position
from database import db
from email_service import EmailService
from datetime import datetime

class PTOTrackerSystem:
    """Main system class for managing PTO requests"""
    
    def __init__(self):
        self.email_service = EmailService()

    def get_staff_directory(self):
        """Dynamic staff directory from database"""
        staff_directory = {'clinical': {}, 'admin': {}}
        
        # Get all team members from database
        team_members = TeamMember.query.join(Position).all()
        
        for member in team_members:
            team = member.team
            position = member.position.name
            
            # Initialize team if not exists
            if team not in staff_directory:
                staff_directory[team] = {}
                
            # Initialize position if not exists
            if position not in staff_directory[team]:
                staff_directory[team][position] = []
                
            # Add member to directory
            staff_directory[team][position].append({
                'name': member.name,
                'email': member.email
            })
        
        return staff_directory

    def add_employee(self, employee_data):
        """Add a new employee"""
        position = Position.query.filter_by(name=employee_data['position']).first()
        if not position:
            raise ValueError(f"Invalid position: {employee_data['position']}")

        existing_employee = TeamMember.query.filter_by(email=employee_data['email']).first()
        if existing_employee:
            raise ValueError("Employee with this email already exists.")

        new_employee = TeamMember(
            name=employee_data['name'],
            email=employee_data['email'],
            position_id=position.id,
            pto_balance_hours=employee_data.get('pto_balance', 60.0)
        )

        if 'pto_refresh_date' in employee_data and employee_data['pto_refresh_date']:
            new_employee.pto_refresh_date = datetime.strptime(employee_data['pto_refresh_date'], '%Y-%m-%d').date()

        db.session.add(new_employee)
        db.session.commit()
        return new_employee

    def edit_employee(self, employee_id, employee_data):
        """Edit an existing employee"""
        employee = TeamMember.query.get_or_404(employee_id)

        position = Position.query.filter_by(name=employee_data['position']).first()
        if not position:
            raise ValueError(f"Invalid position: {employee_data['position']}")

        employee.name = employee_data['name']
        employee.email = employee_data['email']
        employee.position_id = position.id
        employee.pto_balance_hours = float(employee_data.get('pto_balance', employee.pto_balance_hours))
        employee.sick_balance_hours = float(employee_data.get('sick_balance', employee.sick_balance_hours))

        if 'pto_refresh_date' in employee_data and employee_data['pto_refresh_date']:
            employee.pto_refresh_date = datetime.strptime(employee_data['pto_refresh_date'], '%Y-%m-%d').date()
        else:
            employee.pto_refresh_date = None

        db.session.commit()
        return employee

    def delete_employee(self, employee_id):
        """Delete an employee"""
        employee = TeamMember.query.get_or_404(employee_id)
        has_requests = PTORequest.query.filter_by(member_id=employee.id).count() > 0

        if has_requests:
            # Soft delete
            employee.name = f"[INACTIVE] {employee.name}"
            employee.email = f"inactive_{employee.id}@{employee.email}"
            db.session.commit()
            return f'Employee marked as inactive (has historical PTO records).'
        else:
            # Hard delete
            db.session.delete(employee)
            db.session.commit()
            return 'Employee deleted successfully!'
    
    def add_request(self, member_data, pto_data):
        """Add a new PTO request"""
        # Create or get team member
        member = TeamMember.query.filter_by(email=member_data['email']).first()
        if not member:
            member = TeamMember(
                name=member_data['name'],
                email=member_data['email'],
                team=member_data['team'],
                position=member_data['position']
            )
            db.session.add(member)
            db.session.flush()  # Get the ID

        # Check if this is a call-out (should be auto-approved)
        is_call_out = pto_data.get('is_call_out', False)

        # Create PTO request with auto-approval for call-outs
        request = PTORequest(
            member_id=member.id,
            start_date=pto_data['start_date'],
            end_date=pto_data['end_date'],
            pto_type=pto_data['pto_type'],
            manager_team=member.manager_team,
            is_partial_day=pto_data.get('is_partial_day', False),
            start_time=pto_data.get('start_time'),
            end_time=pto_data.get('end_time'),
            reason=pto_data.get('reason'),
            is_call_out=is_call_out,
            status='approved' if is_call_out else 'pending'  # Auto-approve call-outs
        )

        db.session.add(request)
        db.session.flush()  # Get the ID before deducting balance

        # If call-out, automatically deduct from sick balance
        if is_call_out and member:
            hours_to_deduct = request.duration_hours
            current_sick_balance = float(member.sick_balance_hours)
            new_sick_balance = max(0, current_sick_balance - hours_to_deduct)
            member.sick_balance_hours = new_sick_balance

        db.session.commit()

        return request
    
    def get_requests_by_team(self, team):
        """Get all requests for a specific manager team"""
        return PTORequest.query.filter_by(manager_team=team).all()
    
    def get_all_requests(self):
        """Get all requests (for superadmin)"""
        return PTORequest.query.all()
    
    def approve_request(self, request_id, manager):
        """Approve a PTO request"""
        request = PTORequest.query.get(request_id)
        if request and request.status == 'pending':
            request.status = 'approved'

            # Deduct from appropriate balance based on request type
            if request.member:
                hours_to_deduct = request.duration_hours

                # Call-outs always deduct from sick time balance
                if request.is_call_out:
                    current_sick_balance = float(request.member.sick_balance_hours)
                    new_sick_balance = max(0, current_sick_balance - hours_to_deduct)
                    request.member.sick_balance_hours = new_sick_balance
                else:
                    # Regular PTO deducts from PTO balance
                    current_pto_balance = float(request.member.pto_balance_hours)
                    new_pto_balance = max(0, current_pto_balance - hours_to_deduct)
                    request.member.pto_balance_hours = new_pto_balance

            db.session.commit()
            return True
        return False
    
    def deny_request(self, request_id, denial_reason, manager):
        """Deny a PTO request"""
        request = PTORequest.query.get(request_id)
        if request and request.status == 'pending':
            request.status = 'denied'
            request.denial_reason = denial_reason
            db.session.commit()
            return True
        return False