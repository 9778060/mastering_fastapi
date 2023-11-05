import databases
import sqlalchemy
from config import config

metadata = sqlalchemy.MetaData()

post_table = sqlalchemy.Table(
    "posts",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("body", sqlalchemy.String)
)

comments_table = sqlalchemy.Table(
    "comments",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("body", sqlalchemy.String),
    sqlalchemy.Column("post_id", sqlalchemy.ForeignKey("posts.id"), nullable=False)
)


engine = sqlalchemy.create_engine(
    url=config.DATABASE_URL
)

metadata.create_all(engine)
database = databases.Database(
    url=config.DATABASE_URL,
    force_rollback=config.DB_FORCE_ROLL_BACK

)
