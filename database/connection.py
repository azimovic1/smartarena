from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import event, update

from .models import Order, Stadium
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
pg = {"url": "postgresql+asyncpg://postgres:getout04@localhost:5432/postgres", "poolclass": "AsyncAdaptedQueuePool"}
slite = {"url": "sqlite+aiosqlite:///database/db.sqlite3", "connect_args": {"check_same_thread": False}}
mysql = "mysql+aiomysql://sql:$Money04@localhost/smartarena"
engine = create_async_engine(**slite)
Session = async_sessionmaker(engine)


@event.listens_for(Order, "after_insert")
def create_available_hours_for_order(mapper, session, target):
    # if target.start_time and target.hour:
    #     end_time = target.start_time + timedelta(hours=target.hour)
    #
    #     insert_stmt = insert(AvailableHour).values(
    #         available_hour_start=target.start_time,
    #         available_hour_end=end_time,
    #         stadium_id=target.stadium_id
    #     )

    stmt = update(Stadium).where(Stadium.id == target.stadium_id).values(
        number_of_orders=Stadium.number_of_orders + 1)
    # session.execute(insert_stmt)
    session.execute(stmt)
