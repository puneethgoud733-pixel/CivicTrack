import click
from flask.cli import AppGroup
from models import db, User, Role

seed_cli = AppGroup('seed', help='Database seeding commands for CivicTrack.')

DEFAULT_ROLES = ['Citizen', 'Field Engineer', 'Department Admin']

DEMO_USERS = [
    {
        'email': 'citizen@civictrack.org',
        'full_name': 'Ananya Sharma',
        'password': 'Password123!',
        'role': 'Citizen'
    },
    {
        'email': 'engineer@civictrack.org',
        'full_name': 'Rajesh Kumar',
        'password': 'Password123!',
        'role': 'Field Engineer'
    },
    {
        'email': 'admin@civictrack.org',
        'full_name': 'Suresh Menon',
        'password': 'AdminPassword123!',
        'role': 'Department Admin'
    }
]

@seed_cli.command('db')
@click.option('--reset', is_flag=True, help='Drop existing tables before seeding.')
def seed_db(reset):
    """Seed default roles and demo users into SQLite."""
    if reset:
        click.echo("Wiping existing database tables...")
        db.drop_all()

    db.create_all()

    # Seed Roles
    click.echo("\n[1/2] Seeding System Roles...")
    role_objects = {}
    for role_name in DEFAULT_ROLES:
        existing_role = Role.query.filter_by(name=role_name).first()
        if not existing_role:
            role_obj = Role(name=role_name)
            db.session.add(role_obj)
            role_objects[role_name] = role_obj
            click.echo(f"  + Added Role: {role_name}")
        else:
            role_objects[role_name] = existing_role

    db.session.commit()

    # Seed Users
    click.echo("\n[2/2] Seeding Demo Users...")
    for user_data in DEMO_USERS:
        existing_user = User.query.filter_by(email=user_data['email']).first()
        if not existing_user:
            user = User(email=user_data['email'], full_name=user_data['full_name'])
            user.set_password(user_data['password'])
            role_to_assign = role_objects.get(user_data['role'])
            if role_to_assign:
                user.roles.append(role_to_assign)
            db.session.add(user)
            click.echo(f"  + Created User: {user_data['email']} ({user_data['role']})")

    db.session.commit()
    click.secho("\nDatabase seeding completed successfully!", fg='green', bold=True)

def init_app(app):
    app.cli.add_command(seed_cli)