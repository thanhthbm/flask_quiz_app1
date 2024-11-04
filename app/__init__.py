from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_security import SQLAlchemySessionUserDatastore, Security, SQLAlchemyUserDatastore
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

# Khởi tạo Flask app
app = Flask(__name__)

# Cấu hình cho ứng dụng
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.new_quiz_app'
app.config['SECRET_KEY'] = 'abcxyz'

# Khởi tạo SQLAlchemy
db = SQLAlchemy(app)

# Khởi tạo Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Import models sau khi khởi tạo db
from .models import Role, User
user_datastore = SQLAlchemyUserDatastore(db, User, Role)

@login_manager.user_loader
def load_user(user_id):
    return user_datastore.get_user(user_id)


with app.app_context():
    db.create_all()

def create_roles_user():
    with app.app_context():


        with db.session.no_autoflush:  # Ngăn tự động làm mới phiên
            admin_role = Role.query.filter_by(name='admin').first()

            # Tạo người dùng admin nếu chưa tồn tại
            if not User.query.filter_by(username='admin').first():
                admin_user = User(username='admin', password_hash=generate_password_hash('200320045'))
                db.session.add(admin_user)
                db.session.commit()  # Commit trước để có id của admin_user

                # Thêm vai trò cho người dùng admin
                admin_user.roles.append(admin_role)
                db.session.commit()


create_roles_user()
