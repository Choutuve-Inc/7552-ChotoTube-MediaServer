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
    db.session.add(Video(user="Santiago",size=15,url="asds",thumbnail='gdgf',title='primer video'))
    db.session.add(Video(user="Santiago",size=15,url="sfsdf",thumbnail='gdfg',title='segundo video'))
    db.session.commit()


if __name__ == "__main__":
	cli()
