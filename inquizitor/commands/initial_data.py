import click
import logging

from inquizitor.db.session import engine, SessionLocal
from inquizitor.db.init_db import init_db, drop_db
from inquizitor.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init() -> None:
	db = SessionLocal()
	init_db(db, engine)


@click.command()
def initial_data() -> None:
	logger.info("Dropping tables")
	drop_db(engine)
	
	logger.info("Creating initial data")
	init()
	logger.info("Initial data created")

	
@click.command()
def test():
	# click.echo('hello world!')
	click.echo(settings.SQLALCHEMY_DATABASE_URI)

