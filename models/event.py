from sqlobject import *


class Event(SQLObject):
    channel_id = IntCol()
    message_id = IntCol()
    date = DateCol()
    time = TimeCol()
  