from sqlobject import *

class Participant(SQLObject):
  name = StringCol()
  driver = BoolCol()
  event = ForeignKey('Event')
