from telebot.asyncio_handler_backends import State, StatesGroup


class Auth(StatesGroup):
    init = State()  #
    name = State()  #
    number = State()  #
    confirm = State()  #


class NeutralState(StatesGroup):
    init = State()  #


class UserState(StatesGroup):
    init = State()
    main = State()  #
    region = State()  #
    district = State()  #
    date = State()  #
    start_time = State()  #
    hour = State()  #
    # preview = State()  #
    # loc_book = State()  #
    re_book = State()
    bookings = State()


class SuperUserState(StatesGroup):
    init = State()
    main = State()  #
    region = State()  #
    district = State()  #
    date = State()  #
    start_time = State()  #
    hour = State()  #
    preview = State()  #
    loc_book = State()  #
    re_book = State()
    bookings = State()


class OwnerState(StatesGroup):
    init = State()
    main = State()  #
    region = State()  #
    district = State()  #
    stadiums = State()
    date = State()  #
    start_time = State()  #
    hour = State()  #
    preview = State()  #
    loc_book = State()  #
    re_book = State()
    bookings = State()


class StadiumState(StatesGroup):
    init = State()
    proceed = State()
    name = State()
    description = State()
    image = State()
    price = State()
    open_time = State()
    close_time = State()
    region = State()
    district = State()
    location = State()
    confirm = State()


class ManageStadiums(StatesGroup):
    choose_stadium = State()
    edit = State()
    update_attr = State()
    name = State()
    desc = State()
    image = State()
    price = State()
    otime = State()
    ctime = State()
    reg = State()
    dist = State()
    loc = State()


class Help(StatesGroup):
    init = State()


class AdminMenu(StatesGroup):
    main = State()
    data = State()
    get_user = State()
    get_admin = State()