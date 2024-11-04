from app import Role, db

def create_roles():
    admin = Role(id = 1, name = 'admin')
    student = Role(id = 2, name = 'student')

    db.session.add(admin)
    db.session.add(student)
    db.session.commit()
    print("Roles create successfully")
create_roles()
