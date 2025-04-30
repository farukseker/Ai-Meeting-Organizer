from datetime import datetime, date
from typing import Optional, Union
from pydantic import BaseModel, validator

class MeetingModel(BaseModel):
    title: Optional[str]
    notes: Optional[str] = None
    email: Optional[str] = None
    date: Union[date, str, None]
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

    def __bool__(self):
        return self.title is not None and self.is_ready
