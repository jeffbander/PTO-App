"""
Script to update clinical team employees.
Removes all existing clinical employees and adds the new list.
Run once with: python update_clinical_employees.py
"""

from app import app, db
from models import TeamMember, Position, PTORequest

# New clinical employees data
NEW_EMPLOYEES = [
    # CVI MOAs
    {"name": "Daisy Melendez", "email": "Daisy.Melendez@mountsinai.org", "phone": "6464090730", "position": "CVI MOAs"},
    {"name": "Joluse Raoul", "email": "joluse.raoul@mountsinai.org", "phone": "3473620477", "position": "CVI MOAs"},
    {"name": "Hilda Ianova", "email": "hilda.ivanova@mountsinai.org", "phone": "6469124101", "position": "CVI MOAs"},
    {"name": "Nicole Herrera", "email": "Nicole.Herrera@mountsinai.org", "phone": "9177470556", "position": "CVI MOAs"},
    {"name": "Youteen Gurung", "email": "Youteen.Gurung@mountsinai.org", "phone": "9295854533", "position": "CVI MOAs"},
    {"name": "Letika Sepulveda", "email": "Letika.Sepulveda@mountsinai.org", "phone": "3473179212", "position": "CVI MOAs"},
    {"name": "Nina Morena", "email": "NinaMorena.Leite@mountsinai.org", "phone": "7189131973", "position": "CVI MOAs"},
    {"name": "Katherine Valdez", "email": "Katherine.Valdez@mountsinai.org", "phone": "9175399822", "position": "CVI MOAs"},
    {"name": "Anthony Figueroa", "email": "Anthony.Figueroa@mountsinai.org", "phone": "9292953752", "position": "CVI MOAs"},
    {"name": "Chanelle Nieves", "email": "Chanelle.Nieves@mountsinai.org", "phone": "", "position": "CVI MOAs"},

    # CVI Echo Techs
    {"name": "Karina Vaysfeld", "email": "Karina.Vaysfeld@mountsinai.org", "phone": "9179741300", "position": "CVI Echo Techs"},
    {"name": "Anna Alymova (Kloshka)", "email": "Anna.Kloshka@mountsinai.org", "phone": "6466420242", "position": "CVI Echo Techs"},
    {"name": "Nancy Saldutto", "email": "Nancy.Saldutto@mountsinai.org", "phone": "8622235625", "position": "CVI Echo Techs"},
    {"name": "Lisa Morris", "email": "Lisa.Morris@mountsinai.org", "phone": "3475562451", "position": "CVI Echo Techs"},
    {"name": "Linda Pacheco", "email": "Linda.Pacheco@mountsinai.org", "phone": "3473200120", "position": "CVI Echo Techs"},

    # 4th Floor Echo Techs
    {"name": "Ewa Sulewska-Korzeniecki", "email": "Ewa.SulewskaKorzeniecki@mountsinai.org", "phone": "", "position": "4th Floor Echo Techs"},
    {"name": "Sonal Patel", "email": "Sonal.Patel2@mountsinai.org", "phone": "9176585921", "position": "4th Floor Echo Techs"},
    {"name": "Tomy Baptiste", "email": "Tomy.Baptiste@mountsinai.org", "phone": "", "position": "4th Floor Echo Techs"},

    # Other positions
    {"name": "Akua Kusi", "email": "Akua.Kusi@mountsinai.org", "phone": "6466674949", "position": "EKG Tech (4th Floor)"},
    {"name": "Daouda Diabate", "email": "Daouda.Diabate@mountsinai.org", "phone": "6465235727", "position": "Cardiac CT Techs (4th Floor)"},
    {"name": "Marcelino Guerrero", "email": "Marcelino.Guerrero@mountsinai.org", "phone": "9737695847", "position": "Nuclear Tech (CVI)"},
    {"name": "Wendy Gomez", "email": "wendy.gomez@mountsinai.org", "phone": "3472389411", "position": "Vascular Tech"},
]

def update_clinical_employees():
    with app.app_context():
        print("=" * 50)
        print("Updating Clinical Team Employees")
        print("=" * 50)

        # Step 1: Get all clinical positions
        clinical_positions = Position.query.filter_by(team='clinical').all()
        clinical_pos_ids = [p.id for p in clinical_positions]
        print(f"\nFound {len(clinical_positions)} clinical positions")

        # Step 2: Get and delete existing clinical employees
        existing_clinical = TeamMember.query.filter(TeamMember.position_id.in_(clinical_pos_ids)).all()
        print(f"Found {len(existing_clinical)} existing clinical employees to remove")

        for emp in existing_clinical:
            # Delete their PTO requests first
            pto_count = PTORequest.query.filter_by(member_id=emp.id).delete()
            print(f"  - Deleting {emp.name} (removed {pto_count} PTO requests)")
            db.session.delete(emp)

        db.session.commit()
        print("Existing clinical employees deleted.")

        # Step 3: Ensure all required positions exist
        required_positions = set(emp["position"] for emp in NEW_EMPLOYEES)
        print(f"\nRequired positions: {required_positions}")

        position_map = {}
        for pos_name in required_positions:
            pos = Position.query.filter_by(name=pos_name).first()
            if not pos:
                pos = Position(name=pos_name, team='clinical')
                db.session.add(pos)
                db.session.commit()
                print(f"  Created new position: {pos_name}")
            else:
                print(f"  Position exists: {pos_name}")
            position_map[pos_name] = pos.id

        # Step 4: Add new employees
        print(f"\nAdding {len(NEW_EMPLOYEES)} new clinical employees...")

        for emp_data in NEW_EMPLOYEES:
            new_emp = TeamMember(
                name=emp_data["name"],
                email=emp_data["email"],
                phone=emp_data["phone"] or None,
                position_id=position_map[emp_data["position"]],
                pto_balance_hours=128,  # 16 days * 8 hours
                sick_balance_hours=56   # 7 days * 8 hours
            )
            db.session.add(new_emp)
            print(f"  + Added: {emp_data['name']} ({emp_data['position']})")

        db.session.commit()

        # Verify
        final_count = TeamMember.query.filter(TeamMember.position_id.in_(
            [p.id for p in Position.query.filter_by(team='clinical').all()]
        )).count()

        print("\n" + "=" * 50)
        print(f"DONE! Clinical team now has {final_count} employees")
        print("=" * 50)

if __name__ == "__main__":
    update_clinical_employees()
