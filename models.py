from datetime import datetime, date, time
from typing import Optional, Union
from pydantic import BaseModel, validator

class MeetingModel(BaseModel):
    title: Optional[str]
    notes: Optional[str] = None
    email: Optional[str] = None
    date: Union[date, str, None]
    time: Union[time, str, None]
    is_ready: bool = False

    @validator("date", pre=True, allow_reuse=True)
    def parse_date(cls, value):
        if value is None:
            return None
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                # ISO datetime format (e.g., "2024-07-04T08:00:00")
                return datetime.fromisoformat(value).date()
            except ValueError:
                try:
                    # Date only (e.g., "2024-07-04")
                    return datetime.strptime(value, "%Y-%m-%d").date()
                except ValueError:
                    raise ValueError(f"Geçersiz tarih formatı: {value}")
        return None

    @validator("time", pre=True, allow_reuse=True)
    def parse_timee(cls, value):
        if value is None:
            return None
        if isinstance(value, time):
            return value
        if isinstance(value, str):
            try:
                # ISO datetime format (e.g., "2024-07-04T08:00:00")
                return datetime.fromisoformat(value).time()
            except ValueError:
                try:
                    # Date only (e.g., "2024-07-04")
                    return datetime.strptime(value, "%H:%M").time()
                except ValueError:
                    raise ValueError(f"Geçersiz tarih formatı: {value}")
        return None

    def __bool__(self):
        return self.title is not None and self.is_ready

from dataclasses import dataclass
from email_validator import validate_email
from email_validator.exceptions_types import ValidatedEmail


@dataclass
class MeetingFormModel:
    title: str
    email: ValidatedEmail
    notes: str
    date: Union[date]
    time: Union[time]


    @staticmethod
    def __validate_email(email) -> ValidatedEmail | None:
        try:
            return validate_email(email)
        except:
            return None

    def __bool__(self):
        return all([
            (email := self.email) and self.__validate_email(email),
            len(self.title) > 5,
            bool(self.date),
            bool(self.time),
        ])

    @property
    def __dict__(self) -> dict:
        return {
            "title": self.title,
            "notes": self.notes,
            "email": self.email,
            "date": f'{self.date} {self.time}'
        }

class ApiHostModel:
    def __init__(self, host: str):
        self.__HOST: str = host

    def __str__(self):
        return self.__HOST

    def __join__(self, item: str):
        path = "/".join([self.__HOST, item])
        return ApiHostModel(path)

    def __truediv__(self, other):
        return self.__join__(other)

    def __add__(self, other):
        return ApiHostModel(host=self.__HOST + other)

