from sqlobject import *
from models.participant import Participant


class Event(SQLObject):
    channel_id = IntCol()
    message_id = IntCol(notNone=False)
    date = DateCol()
    time = TimeCol()
  
    def participants(self):
        return Participant.selectBy(event=self)
