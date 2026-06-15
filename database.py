from sqlobject import *
from datetime import date, time
from typing import List
from pathlib import Path

from models.event import Event
from models.participant import Participant


def get_first_from_querry(querry):
    if querry.count() >= 1:
        result = querry[0]
    else:
        result = None
    return result

class Database:
    def __init__(self, db_path: str = "./data/gym_bot.db"):
        self.db_path = db_path
        self._connect()
        self._init_db()

    def _connect(self):
        sqlhub.processConnection = connectionForURI(
            f"sqlite:{self.db_path}"
        )

    def _init_db(self):
        db_dir = Path("data")
        db_dir.mkdir(exist_ok=True)

        db_file = db_dir / "gym_bot.db"

        sqlhub.processConnection = connectionForURI(
            f"sqlite:{db_file.resolve()}"
        )

        Event.createTable(ifNotExists=True)
        Participant.createTable(ifNotExists=True)

    def create_event(self, channel_id: int, event_date: date, event_time: time) -> int:
        event = Event(
            channel_id=channel_id,
            message_id=None,
            date=event_date,
            time=event_time
        )

        return event

    def get_event(self, event_id: int) -> Event | None:
        try:
            return Event.get(event_id)
        except SQLObjectNotFound:
            return None

    def get_all_events(self) -> list[Event]:
        return list(Event.select())

    def update_message(self, event_id: int, message_id: int):
        event = Event.get(event_id)
        event.message_id = message_id

    def update(self, event_id: int, participants: List[str], drivers: List[str]):
        event = Event.get(event_id)

        # Vorhandene Teilnehmer löschen
        for participant in list(event.participants):
            participant.destroySelf()

        # Neue Teilnehmer anlegen
        for name in participants:
            Participant(
                name=name,
                driver=name in drivers,
                event=event
            )

    def get_participants(
        self,
        event_id: int
    ) -> List[Participant]:
        event = Event.get(event_id)
        return list(event.participants)

    def delete_event(
        self,
        event_id: int
    ):
        event = Event.get(event_id)

        for participant in list(event.participants):
            participant.destroySelf()

        event.destroySelf()
    
    def join_event(
        self,
        event_id: int,
        username: str
    ):
        event = Event.get(event_id)

        participant = get_first_from_querry(Participant.selectBy(event=event, name=username))
        
        if participant:
            participant.destroySelf()
        else:
            Participant(
                name=username,
                driver=False,
                event=event
            )

    def toggle_driver(
        self,
        event_id: int,
        username: str
    ):
        event = Event.get(event_id)

        participant = get_first_from_querry(Participant.selectBy(event=event, name=username))

        if participant is None:
            Participant(
                name=username,
                driver=True,
                event=event
            )
            return

        participant.driver = not participant.driver

    def leave_event(
        self,
        event_id: int,
        username: str
    ):
        event = Event.get(event_id)

        participant = get_first_from_querry(Participant.selectBy(event=event, name=username))

        if participant:
            participant.destroySelf()

    def get_participants(
        self,
        event_id: int
    ) -> list[str]:

        event = Event.get(event_id)

        return [
            p.name
            for p in event.participants
        ]

    def get_drivers(
        self,
        event_id: int
    ) -> list[str]:

        event = Event.get(event_id)

        return [
            p.name
            for p in event.participants
            if p.driver
        ]