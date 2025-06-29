import pytest
import os
import json
from datetime import datetime, timedelta
from event import Event
from event_manager import EventManager

# Define a test storage file
TEST_STORAGE_FILE = 'test_events.json'

# Fixture to set up and tear down a clean EventManager for each test
@pytest.fixture
def manager():
    # Ensure the test file is clean before each test
    if os.path.exists(TEST_STORAGE_FILE):
        os.remove(TEST_STORAGE_FILE)
    yield EventManager(TEST_STORAGE_FILE)
    # Clean up after each test
    if os.path.exists(TEST_STORAGE_FILE):
        os.remove(TEST_STORAGE_FILE)

# --- Test Event Class ---
def test_event_creation_valid():
    start_time = (datetime.now() + timedelta(days=1)).isoformat()
    end_time = (datetime.now() + timedelta(days=1, hours=1)).isoformat()
    event = Event("Test Title", "Test Description", start_time, end_time)
    assert event.title == "Test Title"
    assert event.description == "Test Description"
    assert event.start_time == start_time
    assert event.end_time == end_time
    assert isinstance(event.id, str)

def test_event_creation_missing_required_fields():
    with pytest.raises(ValueError, match="Title, start time, and end time are required."):
        Event(None, "Desc", "2025-07-01T10:00:00", "2025-07-01T11:00:00")
    with pytest.raises(ValueError, match="Title, start time, and end time are required."):
        Event("Title", "Desc", None, "2025-07-01T11:00:00")

def test_event_creation_invalid_time_format():
    with pytest.raises(ValueError, match="Start time and end time must be valid ISO 8601 datetime strings"):
        Event("Title", "Desc", "invalid-time", "2025-07-01T11:00:00")
    with pytest.raises(ValueError, match="Start time and end time must be valid ISO 8601 datetime strings"):
        Event("Title", "Desc", "2025-07-01T10:00:00", "another-invalid-time")

def test_event_creation_start_time_after_end_time():
    with pytest.raises(ValueError, match="Start time must be before end time."):
        Event("Title", "Desc", "2025-07-01T11:00:00", "2025-07-01T10:00:00")
    with pytest.raises(ValueError, match="Start time must be before end time."):
        Event("Title", "Desc", "2025-07-01T10:00:00", "2025-07-01T10:00:00") # Equal times

def test_event_to_dict_and_from_dict():
    start_time = (datetime.now() + timedelta(days=2)).isoformat()
    end_time = (datetime.now() + timedelta(days=2, hours=1)).isoformat()
    original_event = Event("Meeting", "Project X", start_time, end_time)
    event_dict = original_event.to_dict()
    assert event_dict["title"] == "Meeting"
    assert event_dict["description"] == "Project X"
    assert event_dict["start_time"] == start_time
    assert event_dict["end_time"] == end_time

    recreated_event = Event.from_dict(event_dict)
    assert recreated_event.id == original_event.id
    assert recreated_event.title == original_event.title
    assert recreated_event.description == original_event.description
    assert recreated_event.start_time == original_event.start_time
    assert recreated_event.end_time == original_event.end_time

# --- Test EventManager Class ---
def test_add_event(manager):
    start_time = (datetime.now() + timedelta(days=1)).isoformat()
    end_time = (datetime.now() + timedelta(days=1, hours=1)).isoformat()
    event = Event("New Event", "Details", start_time, end_time)
    added_event = manager.add_event(event)
    assert added_event.id == event.id
    assert len(manager.get_all_events()) == 1
    assert manager.get_event(event.id) is not None

def test_get_all_events_sorted(manager):
    now = datetime.now()
    event1 = Event("Event B", "Desc B", (now + timedelta(hours=2)).isoformat(), (now + timedelta(hours=3)).isoformat())
    event2 = Event("Event A", "Desc A", (now + timedelta(hours=1)).isoformat(), (now + timedelta(hours=1, minutes=30)).isoformat())
    event3 = Event("Event C", "Desc C", (now + timedelta(hours=3)).isoformat(), (now + timedelta(hours=4)).isoformat())

    manager.add_event(event1)
    manager.add_event(event3)
    manager.add_event(event2) # Add out of order to check sorting

    all_events = manager.get_all_events()
    assert len(all_events) == 3
    assert all_events[0].title == "Event A"
    assert all_events[1].title == "Event B"
    assert all_events[2].title == "Event C"

def test_get_event_by_id(manager):
    start_time = (datetime.now() + timedelta(days=1)).isoformat()
    end_time = (datetime.now() + timedelta(days=1, hours=1)).isoformat()
    event = Event("Specific Event", "Details", start_time, end_time)
    manager.add_event(event)
    retrieved_event = manager.get_event(event.id)
    assert retrieved_event is not None
    assert retrieved_event.title == "Specific Event"

def test_get_event_by_id_not_found(manager):
    assert manager.get_event("non-existent-id") is None

def test_update_event_existing(manager):
    start_time = (datetime.now() + timedelta(days=1)).isoformat()
    end_time = (datetime.now() + timedelta(days=1, hours=1)).isoformat()
    event = Event("Original Title", "Original Desc", start_time, end_time)
    manager.add_event(event)

    new_data = {"title": "Updated Title", "description": "Updated Desc"}
    updated_event = manager.update_event(event.id, new_data)
    assert updated_event is not None
    assert updated_event.title == "Updated Title"
    assert updated_event.description == "Updated Desc"
    assert updated_event.start_time == start_time # Should remain unchanged
    assert manager.get_event(event.id).title == "Updated Title" # Verify persistence

def test_update_event_with_time_change(manager):
    start_time = (datetime.now() + timedelta(days=1)).isoformat()
    end_time = (datetime.now() + timedelta(days=1, hours=1)).isoformat()
    event = Event("Time Test", "Desc", start_time, end_time)
    manager.add_event(event)

    new_start = (datetime.now() + timedelta(days=2)).isoformat()
    new_end = (datetime.now() + timedelta(days=2, hours=2)).isoformat()
    new_data = {"start_time": new_start, "end_time": new_end}
    updated_event = manager.update_event(event.id, new_data)
    assert updated_event.start_time == new_start
    assert updated_event.end_time == new_end

def test_update_event_invalid_time_format(manager):
    start_time = (datetime.now() + timedelta(days=1)).isoformat()
    end_time = (datetime.now() + timedelta(days=1, hours=1)).isoformat()
    event = Event("Time Error Test", "Desc", start_time, end_time)
    manager.add_event(event)
    with pytest.raises(ValueError, match="New start time must be a valid ISO 8601 datetime string."):
        manager.update_event(event.id, {"start_time": "bad-time"})

def test_update_event_start_time_after_end_time_validation(manager):
    start_time = (datetime.now() + timedelta(days=1)).isoformat()
    end_time = (datetime.now() + timedelta(days=1, hours=1)).isoformat()
    event = Event("Overlap Test", "Desc", start_time, end_time)
    manager.add_event(event)
    with pytest.raises(ValueError, match="Updated start time cannot be greater than or equal to updated end time."):
        manager.update_event(event.id, {"start_time": (datetime.now() + timedelta(days=2)).isoformat(),
                                        "end_time": (datetime.now() + timedelta(days=1, hours=2)).isoformat()})

def test_update_event_not_found(manager):
    updated_event = manager.update_event("non-existent-id", {"title": "New"})
    assert updated_event is None

def test_delete_event_existing(manager):
    start_time = (datetime.now() + timedelta(days=1)).isoformat()
    end_time = (datetime.now() + timedelta(days=1, hours=1)).isoformat()
    event = Event("To Be Deleted", "...", start_time, end_time)
    manager.add_event(event)
    assert len(manager.get_all_events()) == 1
    assert manager.delete_event(event.id) is True
    assert len(manager.get_all_events()) == 0
    assert manager.get_event(event.id) is None # Verify it's gone

def test_delete_event_not_found(manager):
    assert manager.delete_event("non-existent-id") is False
    assert len(manager.get_all_events()) == 0 # Should still be 0 if nothing was added

def test_persistence(manager):
    start_time = (datetime.now() + timedelta(days=1)).isoformat()
    end_time = (datetime.now() + timedelta(days=1, hours=1)).isoformat()
    event1 = Event("Persistent Event 1", "Desc 1", start_time, end_time)
    event2 = Event("Persistent Event 2", "Desc 2", (datetime.now() + timedelta(days=2)).isoformat(), (datetime.now() + timedelta(days=2, hours=1)).isoformat())

    manager.add_event(event1)
    manager.add_event(event2)

    # Create a new manager instance to simulate a restart
    new_manager = EventManager(TEST_STORAGE_FILE)
    loaded_events = new_manager.get_all_events()

    assert len(loaded_events) == 2
    assert loaded_events[0].title == "Persistent Event 1"
    assert loaded_events[1].title == "Persistent Event 2"
    assert os.path.exists(TEST_STORAGE_FILE)