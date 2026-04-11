import json
import os
from datetime import date, timedelta
from pathlib import Path

from src.models.calendar_events import CalendarEvent, CalendarEventCreate, AnnualCalendar
from src.models.common import Platform


DATA_DIR = Path(__file__).parent.parent / "data"


class EventsCalendarService:

    def __init__(self):
        self._events: list[CalendarEvent] = []
        self._custom_events: list[CalendarEvent] = []
        self._load_events()

    def _load_events(self):
        events_file = DATA_DIR / "india_events_2026.json"
        if events_file.exists():
            with open(events_file) as f:
                raw = json.load(f)
            self._events = [CalendarEvent(**e) for e in raw]

    def get_all_events(self, year: int | None = None) -> list[CalendarEvent]:
        all_events = self._events + self._custom_events
        if year:
            all_events = [e for e in all_events if e.date_start.year == year]
        return sorted(all_events, key=lambda e: e.date_start)

    def get_annual_calendar(self, year: int) -> AnnualCalendar:
        events = self.get_all_events(year=year)
        return AnnualCalendar(year=year, events=events, total_events=len(events))

    def get_upcoming_events(self, days_ahead: int = 30) -> list[CalendarEvent]:
        today = date.today()
        cutoff = today + timedelta(days=days_ahead)
        return [
            e for e in self.get_all_events()
            if (e.date_start >= today and e.date_start <= cutoff)
            or (e.date_start <= today <= e.date_end)
        ]

    def get_active_events(self, target_date: date) -> list[CalendarEvent]:
        return [
            e for e in self.get_all_events()
            if e.date_start <= target_date <= e.date_end
        ]

    def get_events_with_preevent(self, target_date: date) -> list[CalendarEvent]:
        results = []
        for e in self.get_all_events():
            pre_start = e.date_start - timedelta(days=e.pre_event_days)
            post_end = e.date_end + timedelta(days=e.post_event_days)
            if pre_start <= target_date <= post_end:
                results.append(e)
        return results

    def get_events_for_platform(self, platform: Platform, target_date: date) -> list[CalendarEvent]:
        return [
            e for e in self.get_events_with_preevent(target_date)
            if platform in e.platforms
        ]

    def add_custom_event(self, event: CalendarEventCreate) -> CalendarEvent:
        cal_event = CalendarEvent(**event.model_dump())
        self._custom_events.append(cal_event)
        return cal_event
