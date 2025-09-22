from flask.cli import with_appcontext
from app import create_app
from app.extensions import db
from app.models import User
import click

app = create_app()

@app.cli.command("seed-admin")
@with_appcontext
def seed_admin():
    if not User.query.filter_by(username='admin').first():
        u = User(username='admin')
        u.set_password('admin')
        db.session.add(u); db.session.commit()
        click.echo("Admin created (username=admin, password=admin).")
    else:
        click.echo("Admin already exists.")
