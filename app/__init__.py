from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.new_quiz_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'abcxyz'

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# Khởi tạo người dùng admin nếu chưa tồn tại
from app.models import User
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin_user = User(username='admin', role='admin')
        admin_user.set_password('admin')  # Đặt mật khẩu cho admin
        db.session.add(admin_user)
        db.session.commit()

# Import models








# Import routes
from app import routes
