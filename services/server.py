from flask.cli import FlaskGroup

from project import app, db, Video


cli = FlaskGroup(app)


@cli.command("create_db")
def create_db():
	db.drop_all()
	db.create_all()
	db.session.commit()

@cli.command("seed_db")
def seed_db():
    db.session.add(Video(video_name="Santiago",video_size=15,url="asds"))
    db.session.add(Video(video_name="Marinaro",video_size=15,url="hhsh"))
    db.session.commit()


if __name__ == "__main__":
	cli()
