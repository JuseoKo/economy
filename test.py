from table.base import DBConnection
from sqlalchemy import text


db = DBConnection().sync_db()
result = db.execute(text("SELECT version()"))
print(result.fetchone())