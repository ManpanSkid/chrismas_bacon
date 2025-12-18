from db.database import get_sqlite_db, get_postgres_db
from db.schema import OrderDB

def migrate_orders():
    with get_sqlite_db() as sqlite_db, get_postgres_db() as pg_db:
        orders = sqlite_db.query(OrderDB).all()

        for order in orders:
            data = {
                c.name: getattr(order, c.name)
                for c in OrderDB.__table__.columns
            }
            pg_db.merge(OrderDB(**data))

        pg_db.commit()

        return {"migrated": len(orders)}
