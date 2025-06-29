import json
from datetime import datetime
from event import Event # Assuming event.py is in the same directory

class EventManager:
    def __init__(self, storage_file='events.json'):
        self.storage_file = storage_file
        self.events = self._load_events()

    def _load_events(self):
        try:
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
                # Convert dictionary data back into Event objects
                return [Event.from_dict(item) for item in data]
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            # Handle empty or corrupted JSON files
            return []

    def _save_events(self):
        with open(self.storage_file, 'w') as f:
            # Convert Event objects to dictionaries for JSON serialization
            json.dump([event.to_dict() for event in self.events], f, indent=4)

    def add_event(self, event):
        self.events.append(event)
        self._save_events()
        return event

    def get_event(self, event_id):
        for event in self.events:
            if event.id == event_id:
                return event
        return None

    def get_all_events(self, expand_recurring=True, after=None):
        # Return all events, optionally expanding recurring events to their next occurrence
        after = after or datetime.now()
        result = []
        for event in self.events:
            if expand_recurring and event.recurrence != 'none':
                next_occ = event.next_occurrence(after)
                if next_occ:
                    # Create a copy with updated times
                    e_dict = event.to_dict().copy()
                    e_dict['start_time'] = next_occ[0].isoformat()
                    e_dict['end_time'] = next_occ[1].isoformat()
                    result.append(Event.from_dict(e_dict))
            else:
                result.append(event)
        # Sort by start time ascending
        return sorted(result, key=lambda e: datetime.fromisoformat(e.start_time))

    def update_event(self, event_id, new_data):
        event = self.get_event(event_id)
        if event:
            # Update only provided fields, keeping existing if not provided
            event.title = new_data.get('title', event.title)
            event.description = new_data.get('description', event.description)
            event.recurrence = new_data.get('recurrence', event.recurrence)
            event.email = new_data.get('email', event.email)

            # Validate and update start_time and end_time if provided
            updated_start_time = new_data.get('start_time')
            updated_end_time = new_data.get('end_time')

            if updated_start_time:
                try:
                    event.start_time = datetime.fromisoformat(updated_start_time).isoformat()
                except ValueError:
                    raise ValueError("New start time must be a valid ISO 8601 datetime string.")
            if updated_end_time:
                try:
                    event.end_time = datetime.fromisoformat(updated_end_time).isoformat()
                except ValueError:
                    raise ValueError("New end time must be a valid ISO 8601 datetime string.")

            # Re-validate start/end time relationship after updates
            if datetime.fromisoformat(event.start_time) >= datetime.fromisoformat(event.end_time):
                raise ValueError("Updated start time cannot be greater than or equal to updated end time.")

            self._save_events()
            return event
        return None

    def delete_event(self, event_id):
        initial_len = len(self.events)
        self.events = [event for event in self.events if event.id != event_id]
        if len(self.events) < initial_len:
            self._save_events()
            return True # Event was found and deleted
        return False # Event not found