import uuid
from datetime import datetime, timedelta

class Event:
    def __init__(self, title, description, start_time, end_time, event_id=None, recurrence='none', email=None):
        if not title or not start_time or not end_time:
            raise ValueError("Title, start time, and end time are required.")

        try:
            # Ensure times are in ISO 8601 format and valid
            self.start_time = datetime.fromisoformat(start_time).isoformat()
            self.end_time = datetime.fromisoformat(end_time).isoformat()
        except ValueError:
            raise ValueError("Start time and end time must be valid ISO 8601 datetime strings (e.g., YYYY-MM-DDTHH:MM:SS).")

        if datetime.fromisoformat(self.start_time) >= datetime.fromisoformat(self.end_time):
            raise ValueError("Start time must be before end time.")

        self.id = event_id if event_id else str(uuid.uuid4())
        self.title = title
        self.description = description if description is not None else ""
        self.recurrence = recurrence  # 'none', 'daily', 'weekly', 'monthly'
        self.email = email

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "recurrence": self.recurrence,
            "email": self.email
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            event_id=data.get("id"),
            title=data.get("title"),
            description=data.get("description"),
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            recurrence=data.get("recurrence", 'none'),
            email=data.get("email")
        )

    def next_occurrence(self, after=None):
        """
        Returns the next occurrence (start_time, end_time) as datetime objects after the given datetime (or now).
        Returns None if no next occurrence.
        """
        after = after or datetime.now()
        start = datetime.fromisoformat(self.start_time)
        end = datetime.fromisoformat(self.end_time)
        if self.recurrence == 'none':
            if start > after:
                return (start, end)
            return None
        # For recurring events, find the next occurrence after 'after'
        while start <= after:
            if self.recurrence == 'daily':
                start += timedelta(days=1)
                end += timedelta(days=1)
            elif self.recurrence == 'weekly':
                start += timedelta(weeks=1)
                end += timedelta(weeks=1)
            elif self.recurrence == 'monthly':
                # Simple monthly increment: add 30 days
                start += timedelta(days=30)
                end += timedelta(days=30)
            else:
                break
        return (start, end) if start > after else None