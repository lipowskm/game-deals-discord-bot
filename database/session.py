import databases
import sqlalchemy

import settings

engine = sqlalchemy.create_engine(settings.DATABASE_URL)
database = databases.Database(url=settings.DATABASE_URL, ssl='allow')