from flask.cli import FlaskGroup
from app import app, db, User

cli = FlaskGroup(app)

# docker-compose exec service python manage.py create_db
@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command("seed_db")
def seed_db():
    db.session.add(User(email="michael@mherman.org"))
    db.session.commit()


if __name__ == "__main__":
    cli()