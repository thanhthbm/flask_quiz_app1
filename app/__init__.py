# app/__init__.py
from flask import Flask
from .extensions import db, migrate, csrf
from .utils.auth import load_logged_in_user
import os
from dotenv import load_dotenv
import click  # ✅ thêm

load_dotenv()

def register_cli(app: Flask):
    @app.cli.command("seed-admin")
    def seed_admin():
        """Tạo tài khoản admin mặc định."""
        from .models import User
        from .extensions import db

        if User.query.filter_by(username="admin").first():
            click.echo("Admin already exists.")
            return

        try:
            admin = User(username="admin", role="admin")
            admin.set_password("admin123")
        except AttributeError:
            # fallback nếu chưa có set_password()
            from werkzeug.security import generate_password_hash
            admin = User(
                username="admin",
                role="admin",
                password_hash=generate_password_hash("admin123")
            )

        db.session.add(admin)
        db.session.commit()
        click.echo("✅ Admin created: admin/ admin123")

def create_app():
    app = Flask(__name__)

    app.config.from_object("config.Config")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me")

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    from .blueprints.main import bp as main_bp
    from .blueprints.auth import bp as auth_bp
    from .blueprints.admin import bp as admin_bp
    from .blueprints.quiz import bp as quiz_bp

    app.register_blueprint(main_bp, url_prefix="/")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(quiz_bp, url_prefix="/quiz")

    @app.before_request
    def _load_user():
        load_logged_in_user()

    @app.template_filter("format_time")
    def format_time(td):
        if not td:
            return "-"
        total = int(td.total_seconds())
        hh, rem = divmod(total, 3600)
        mm, ss = divmod(rem, 60)
        return f"{hh:02d}:{mm:02d}:{ss:02d}"

    register_cli(app)

    return app
