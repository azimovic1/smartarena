import datetime
import json
import logging
import re
from datetime import timedelta
from sqlalchemy import select, func, exists, and_, or_, text, delete, update
from sqlalchemy.orm import joinedload, selectinload
from telebot.types import InputMediaPhoto

from utils.config import log_level, regions_file_path
from .models import Stadium, Order, User, Base
from .connection import engine

logger = logging.getLogger(__name__)
logger.setLevel(log_level)


async def update_stadium_fields(stadium_id, sts, conn):
    try:
        if 'image_urls' in sts and isinstance(sts['image_urls'], list):
            sts['image_urls'] = json.dumps(sts['image_urls'])

        async with conn() as db:
            q = update(Stadium).where(Stadium.id == stadium_id).values(**sts)
            await db.execute(q)
            await db.commit()
        return "Yangilandi"
    except Exception as e:
        logger.error(f"error updating field {sts}, {e}", exc_info=True)
        return "Hatolik yuz berdi admin bilan bog'laning"


async def get_region_id_from_db(stadium_id, conn):
    try:
        async with conn() as db:
            stadium_region = (await db.execute(select(Stadium.region).where(Stadium.id == stadium_id))).scalar()
        with open(regions_file_path, "r", encoding="utf-8") as file:
            region_id = list(filter(lambda x: x["name"] == stadium_region, json.load(file)["regions"]))[0]["id"]
        return region_id
    except Exception as e:
        logger.error(f"erron reteiving region_id{e}", exc_info=True)
        return False


async def refresh_stadium_manage(stadium_id, conn):
    try:
        async with conn() as db:
            s_query = select(Stadium).where(Stadium.id == stadium_id)
            stadium = (await db.execute(s_query)).scalar()
            if len(stadium.image_urls) > 0:
                images = [InputMediaPhoto(i) for i in json.loads(stadium.image_urls)]
            else:
                images = []
            message = f"""
<b>Nomi:</b> {stadium.name}
<b>Ma'lumot:</b> {stadium.description}
<b>Narxi:</b> {stadium.price} so'm/soat
<b>Ochilish vaqti:</b> {stadium.opening_time}
<b>Yopilish vaqti:</b> {stadium.closing_time}
<b>Viloyat:</b> {stadium.region}
<b>Tuman:</b> <i>{stadium.district}</i>"""
            return True, stadium, message, images
    except Exception as e:
        logger.error(f"error refreshing stadium {e}", exc_info=True)
        return False, None, "Hatolik yuz berdi admin bilan bog'laning", []


async def delete_stadium_with_id(conn, stadium_id):
    try:
        async with conn() as db:
            query = delete(Stadium).where(Stadium.id == stadium_id)
            await db.execute(query)
            await db.commit()
        return True, "Stadionlar\ntanlang", "Stadion o'chirildi"
    except Exception as e:
        logger.error(f"Error deleting the stadium {e}", exc_info=True)
        return False, "Hatolik yuz berdi admin bilan bog'laning", "Hatolik yuz berdi"


async def get_stadium_details_from_db(conn, data):
    try:
        async with conn() as db:
            s_query = select(Stadium).where(Stadium.id == data)
            stadium = (await db.execute(s_query)).scalar()
            images = [InputMediaPhoto(i) for i in json.loads(stadium.image_urls)]
            message = f"""
<b>Nomi:</b> {stadium.name}
<b>Ma'lumot:</b> {stadium.description}
<b>Narxi:</b> {stadium.price} so'm/soat
<b>Ochilish vaqti:</b> {stadium.opening_time}
<b>Yopilish vaqti:</b> {stadium.closing_time}
<b>Viloyat:</b> {stadium.region}
<b>Tuman:</b> <i>{stadium.district}</i>"""
        return images, message, stadium.location
    except Exception as e:
        logger.error(f"error occured in manage sts:{e}", exc_info=True)
        return [], "Hatolik Yuz berdi", None


async def fetch_stadium_with_owner_id(owner_id, conn, no_left=False):
    """:return: an iterable obj with tuples stadium(name, id)"""
    try:
        stadiums_query = select(Stadium.name, Stadium.id).where(Stadium.user_id == owner_id)
        async with conn() as db:
            stadiums = (await db.execute(stadiums_query)).fetchall()
            logger.info(stadiums)
        if len(stadiums) < 1:
            return (None, "stadionlar qolmadi") if no_left else (None, "Sizda stadionlar mavjud emas")
        else:
            return stadiums, "Stadionlar"

    except Exception as e:
        logger.error(f"error fetching data in managa stadium {e}", exc_info=True)
        return False, "Hatolik yuz berdi admin bilan bog'laning!"


async def get_filtered_stadiums(conn, region_filter, district_filter, combined_datetime, hour_filter, stadium_id=None):
    """:return: On success list of stadium obj"""
    async with (conn() as session):
        requested_end_time_str = (combined_datetime + timedelta(hours=hour_filter)).strftime('%Y-%m-%d %H:%M:%S')
        combined_datetime_str = combined_datetime.strftime('%Y-%m-%d %H:%M:%S')

        query = (
            select(Stadium)
            .filter(
                ~exists().where(
                    and_(
                        Order.stadium_id == Stadium.id,
                        or_(
                            # Case 1: An existing booking starts within the requested time slot
                            and_(
                                Order.start_time >= func.datetime(combined_datetime_str),
                                Order.start_time < func.datetime(requested_end_time_str),
                            ),
                            # Case 2: An existing booking envelops the requested time slot
                            and_(
                                Order.start_time <= func.datetime(combined_datetime_str),
                                text("datetime(orders.start_time, '+' || orders.hour || ' hours')") > func.datetime(
                                    combined_datetime_str),
                            ),
                            # Case 3: An existing booking ends within the requested time slot
                            and_(
                                text("datetime(orders.start_time, '+' || orders.hour || ' hours')") > func.datetime(
                                    combined_datetime_str),
                                text("datetime(orders.start_time, '+' || orders.hour || ' hours')") <= func.datetime(
                                    requested_end_time_str),
                            )
                        )
                    )
                )
            )
        )

        if stadium_id is not None:
            query = query.filter(Stadium.id == stadium_id)
        else:
            query = query.filter(func.lower(Stadium.region).ilike(func.lower(region_filter))).filter(
                func.lower(Stadium.district).ilike(func.lower(district_filter)))
        try:
            result = await session.execute(query)
            stadiums = result.scalars().all()
            return stadiums
        except Exception as e:
            logger.error(e, exc_info=True)
            return []


async def retrieve_upcoming_orders(data, conn, msg):
    today = datetime.datetime.now()
    # logger.debug(data)
    if msg == "📆 Buyurtmalar tarixi":
        _filter_ = Order.start_time <= today
    else:
        _filter_ = Order.start_time >= today
    try:
        upcoming_orders_query = (
            select(Order.start_time, Order.hour, Stadium.name)
            .join(Stadium, Order.stadium_id == Stadium.id)
            .filter(Order.user_id == data["user_id"])
            .filter(_filter_)
        )

        async with conn() as db:
            result = (await db.execute(upcoming_orders_query)).all()
            text_ = ""

            for i in result:
                time = i[0].strftime("%y-%b %d.%H")
                text_ += f"<b>Stadium</b>: {i[2]}\n<b>Boshlanish sana/vaqti</b>: <code>{time}</code>\n<b>Soat</b>: <code>{i[1]}</code>\n\n"
        return text_
    except Exception as e:
        logger.warning(f"error in view booking {e}")


async def add_order_to_db(data, conn):
    """adds a new order"""
    start_time_str = data.pop("start_time")
    date_str = data.pop("date")
    date_object = datetime.datetime.strptime(date_str.replace(":", "-"), "%Y-%m-%d")
    start_time_delta = datetime.datetime.strptime(start_time_str, "%H:%M").time()
    combined_datetime = datetime.datetime.combine(date_object, start_time_delta)
    hour = data.pop("hour")
    new_order = Order(status="Ko'rib chiqilmoqda", start_time=combined_datetime, hour=hour,
                      user_id=data["user_id"],
                      stadium_id=data["stadium_id"])
    try:
        text_ = ""
        async with conn() as db:
            db.add(new_order)
            await db.commit()
            await db.refresh(new_order)
            q_s = select(Stadium).where(Stadium.id == new_order.stadium_id)
            q_u = select(User).where(User.id == new_order.user_id)
            stadium = (await (db.execute(q_s))).scalar()
            user = (await (db.execute(q_u))).scalar()

            text_ += f"""<b>Stadion</b>: <code>{stadium.name}</code>
<b>Boshlanish vaqti</b>: <code>{combined_datetime}</code>
<b>Soat</b>: <code>{hour}</code>

<b>Buyurtmachi</b>: <b>{user.username}</b> 
<b>raqami</b>: <code>{user.number}</code>


#{stadium.region.replace(" ", "_")}, #{stadium.district.replace(" ", "_")}, #{stadium.name.replace(" ", "_")}
                """
        return text_

    except Exception as e:
        logger.error(f"error accured {e}", exc_info=True)
        return "Hatolik yuz berdi"


async def stadium_preview_get_text_image(data, bdata, conn):
    async with conn() as db:
        stadium_q = select(Stadium).where(Stadium.id == data)
        stadium = (await db.execute(stadium_q)).scalar()
        message = f"""<b>Nomi:</b> {stadium.name}
<b>Ma'lumot:</b> {stadium.description}
<b>Narxi:</b> {stadium.price} so'm/soat
<b>Ochilish vaqti:</b> {stadium.opening_time}
<b>Yopilish vaqti:</b> {stadium.closing_time}
<b>Viloyat:</b> {stadium.region}
<b>Tuman:</b> <i>{stadium.district}</i>"""
        bdata["location"] = stadium.location
        image_urls = json.loads(stadium.image_urls)
        images = []
        for i in image_urls:
            images.append(InputMediaPhoto(i))
        return message, images, stadium.name


async def get_ordered_stadiums(telegram_id, region, district, conn):
    """
    :return: On success, -a list of tuples (stadium name, stadium id).   else -> empty list
    """
    try:
        async with conn() as db:
            user_q = select(User.id).where(User.telegram_id == telegram_id)
            user_id = (await db.execute(user_q)).scalar()

            stadium_q = select(Stadium).join(Order, Stadium.id == Order.stadium_id).where(Order.user_id == user_id,
                                                                                          Stadium.region == region,
                                                                                          Stadium.district == district)

            stadiums_result = (await db.execute(stadium_q)).scalars().all()
            stadiums = []

            for stadium in stadiums_result:
                if (stadium.name, stadium.id) not in stadiums:
                    stadiums.append((stadium.name, stadium.id))

            return stadiums
    except Exception as e:
        logger.error(f"error accured rebook {e}", exc_info=True)
        return []


async def user_check(telegram_id, conn):
    try:
        async with conn() as db:
            user_query = select(User).where(User.telegram_id == telegram_id)
            user = (await db.execute(user_query)).scalar()
            return user
    except Exception as e:
        logger.error(f"error in user_check: {e}", exc_info=True)
        return False


async def add_new_user(user_data: dict, conn):
    try:
        async with conn() as db:
            new_user = User(**user_data)
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
        return new_user
    except Exception as e:
        logger.warning(f"Unexpected error occured {e}", exc_info=True)
        return False


async def check_phone_number(phone_number, conn):
    pattern = re.compile(r'^\+998\d{9}$')
    phone_number = phone_number.replace(" ", "")
    match = pattern.match(phone_number)
    if bool(match):
        async with conn() as db:
            user_query = select(User).where(User.number == phone_number)
            user = (await db.execute(user_query)).scalar_one_or_none()
        return True if user is None else False
    else:
        return False


async def create_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def add_stadium_to_database(data, owner_id, conn):
    new_stadium = Stadium(name=data["stadium_name"], description=data["stadium_description"],
                          price=int(data["stadium_price"]), opening_time=data["stadium_open_time"],
                          closing_time=data["stadium_close_time"], region=data["region_name"],
                          district=data["district_name"], location=data["location_data"],
                          user_id=owner_id)
    image_url = "AgACAgIAAxkBAAIH7GYAAUIJnX7KaIPYyW-TxE-Qi6H0kwACodsxGwRBAAFIKVW2T0LSarkBAAMCAANtAAM0BA"
    if len(data["stadium_photo"]) > 0:
        new_stadium.set_image_urls(data["stadium_photo"])
    else:
        new_stadium.set_image_urls([image_url])

    try:
        async with conn() as db:
            db.add(new_stadium)
            await db.commit()
        return True
    except Exception as e:
        logger.error(f"error accured while adding new stadium {e}", exc_info=True)
        return False


async def serialize_users(session):
    try:
        async with session() as db:
            q = select(User).options(joinedload(User.stadiums), joinedload(User.orders))
            result = await db.execute(q)
            users = result.scalars().unique().all()

            serialized_users = []
            for user in users:
                serialized_users.append({
                    "id": user.id,
                    "username": user.username,
                    "telegram_id": user.telegram_id,
                    "number": user.number,
                    "gender": user.gender,
                    "is_admin": user.is_admin,
                    "is_owner": user.is_owner,
                    "is_user": user.is_user,
                    "lang": user.lang,
                    "stadium_ids": [stadium.id for stadium in user.stadiums],
                    "order_ids": [order.id for order in user.orders]
                })
            data = json.dumps(serialized_users, indent=4)
        return data
    except Exception as e:
        logger.error(f"error in serializers {e}", exc_info=True)
        return {}


async def serialize_stadiums(session):
    try:
        async with session() as db:
            q = select(Stadium).options(selectinload(Stadium.orders))

            result = await db.execute(q)
            stadiums = result.scalars().all()
            serialized_stadiums = []
            for stadium in stadiums:
                serialized_stadiums.append({
                    "id": stadium.id,
                    "name": stadium.name,
                    "description": stadium.description,
                    "image_urls": stadium.image_urls,
                    "price": stadium.price,
                    "opening_time": stadium.opening_time,
                    "closing_time": stadium.closing_time,
                    "is_active": stadium.is_active,
                    "region": stadium.region,
                    "district": stadium.district,
                    "location": stadium.location,
                    "number_of_orders": stadium.number_of_orders,
                    "user_id": stadium.user_id,
                })

        data = json.dumps(serialized_stadiums, ensure_ascii=False, indent=4)
        return data
    except Exception as e:
        logger.error(f"error in serializers {e}", exc_info=True)
        return {}


async def serialize_orders(session):
    try:
        async with session() as db:
            q = select(Order)
            result = await db.execute(q)
            orders = result.scalars().all()

        serialized_orders = []
        for order in orders:
            serialized_orders.append({
                "id": order.id,
                "status": order.status,
                "start_time": order.start_time.isoformat() if isinstance(order.start_time, datetime.datetime) else None,
                "hour": order.hour,
                "user_id": order.user_id,
                "stadium_id": order.stadium_id,
            })

        data = json.dumps(serialized_orders, ensure_ascii=False, indent=4)
        return data
    except Exception as e:
        logger.error(f"error in serializers {e}", exc_info=True)
        return {}


async def add_owner_to_db(value, conn, number=False):
    if number:
        value = f"+{value}" if "+" not in value else value
        pattern = re.compile(r'^\+998\d{9}$')
        phone_number = value.replace(" ", "")
        match = pattern.match(phone_number)
        if match:
            q = update(User).where(User.number == value).values(is_user=False, is_owner=True, is_admin=False)
        else:
            return match, "Hato raqam kiritdingiz,\nTo'g'ri raqam shakli: <code>+998987654321</code>"
    else:
        q = update(User).where(User.telegram_id == value[0]).values(is_user=False, is_owner=True, is_admin=False)

    try:
        async with conn() as db:
            result = await db.execute(q)
            if result.rowcount == 0:
                return None, "Bunday User malumotlar basasida mavjud emas🤷‍♂️"
            else:
                await db.commit()
                return True, "Owner qo'shildi✅"
    except Exception as e:
        logger.error(f"error updating user type in db {e}", exc_info=True)
        return False, "Hotolik yuz berdi, @azimovic3 bilan bog'laning"


async def add_admin_to_db(value, conn, number=False):
    if number:
        value = f"+{value}" if "+" not in value else value
        pattern = re.compile(r'^\+998\d{9}$')
        phone_number = value.replace(" ", "")
        match = pattern.match(phone_number)
        if match:
            q = update(User).where(User.number == value).values(is_user=False, is_owner=False, is_admin=True)
        else:
            return match, "Hato raqam kiritdingiz,\nTo'g'ri raqam shakli: <code>+998987654321</code>"
    else:
        q = update(User).where(User.telegram_id == value[0]).values(is_user=False, is_owner=False, is_admin=True)

    try:
        async with conn() as db:
            result = await db.execute(q)
            if result.rowcount == 0:
                return None, "Bunday User malumotlar basasida mavjud emas🤷‍♂️"
            else:
                await db.commit()
                return True, "Owner qo'shildi✅"
    except Exception as e:
        logger.error(f"error updating user type in db {e}", exc_info=True)
        return False, "Hotolik yuz berdi, @azimovic3 bilan bog'laning"
