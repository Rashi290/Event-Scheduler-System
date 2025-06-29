# Event Scheduler System

A simple web-based event scheduler with RESTful API, built using Flask (Python) and a modern HTML/JS frontend. Supports reminders, recurring events, email notifications, and search.

---

## Features

- **Event Creation:** Add new events with title, description, start/end time, recurrence, and optional email notification.
- **Event Listing:** View all scheduled events, sorted by start time (latest at top in UI).
- **Event Updating:** Edit any event's details.
- **Event Deletion:** Remove events from the schedule.
- **Reminders:** Console and email reminders for events due within the next hour (checked every minute).
- **Recurring Events:** Support for daily, weekly, and monthly recurring events.
- **Event Notifications:** Email reminders (uses Gmail SMTP; see below).
- **Search:** Search events by title or description.
- **Frontend:** Modern HTML/JS interface for all features.
- **Persistence:** All data saved in `events.json`.
- **Unit Tests:** Pytest-based tests for backend logic.

---

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd event
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **(Optional) Configure Email Notifications:**
   - Open `app.py` and set `EMAIL_SENDER` and `EMAIL_PASSWORD` to your Gmail and app password.
   - [How to get a Gmail app password?](https://support.google.com/accounts/answer/185833)

---

## Running the Application

1. **Start the Flask server:**
   ```bash
   flask run
   ```
   - The app will run at [http://127.0.0.1:5000](http://127.0.0.1:5000)
   - Reminders will print in the terminal and send emails if configured.

2. **Open the Frontend:**
   - Open your browser and go to [http://127.0.0.1:5000](http://127.0.0.1:5000)
   - You can add, update, delete, search, and view events from the web UI.
   - The "Time Left" column shows how much time is left for each event (auto-updates every minute).

---

## API Endpoints

All endpoints are relative to `http://127.0.0.1:5000`.

### 1. Create Event
- **POST** `/events`
- **Body:**
  ```json
  {
    "title": "Team Meeting",
    "description": "Discuss roadmap",
    "start_time": "2025-07-01T10:00:00",
    "end_time": "2025-07-01T11:00:00",
    "recurrence": "none",      // or "daily", "weekly", "monthly"
    "email": "user@example.com" // optional
  }
  ```
- **Returns:** Event object (201) or error (400)

### 2. Get All Events
- **GET** `/events`
- **Returns:** List of all events (sorted by start time)

### 3. Get Event by ID
- **GET** `/events/<event_id>`
- **Returns:** Event object or error (404)

### 4. Update Event
- **PUT** `/events/<event_id>`
- **Body:** (any fields to update)
- **Returns:** Updated event or error

### 5. Delete Event
- **DELETE** `/events/<event_id>`
- **Returns:** Success message or error

### 6. Search Events
- **GET** `/events/search?query=...`
- **Returns:** List of matching events

---

## Frontend Usage

- Go to [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.
- **Add Event:** Fill the form and click "Add Event".
- **Update Event:** Click "Update" next to an event, edit, and save.
- **Delete Event:** Click "Delete" next to an event.
- **Search:** Use the search bar to filter events by title/description.
- **Recurring Events:** Select recurrence when creating/updating.
- **Email Notification:** Enter your email to get reminders for that event.
- **Time Left:** See how much time is left for each event in the table.

---

## Running Unit Tests

```bash
pytest
```

---

## Notes
- For email notifications, you must use a Gmail account and an app password (not your main password).
- All event data is stored in `events.json` in the project directory.
- The backend and frontend are fully integrated; no extra setup is needed for the UI.

---

## License
MIT