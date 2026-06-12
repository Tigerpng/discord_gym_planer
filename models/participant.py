from sqlobject import *

class Event(SQLObject):
  name = StringCol()
  driver = BoolCol()
  event = ForeignKey('User')
