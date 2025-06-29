from flask import Flask, request, jsonify, render_template
from event_manager import EventManager
from event import Event
import threading
import time
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
event_manager = EventManager()

# --- Email Notification Helper ---
EMAIL_SENDER = 'your_email@gmail.com'  # Change to your email
EMAIL_PASSWORD = 'your_app_password'    # Use app password for Gmail
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

def send_email_notification(to_email, subject, body):
    if not to_email:
        return
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_SENDER
        msg['To'] = to_email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, [to_email], msg.as_string())
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")

# --- Reminder Feature (Bonus) ---
def reminder_checker():
    reminded = set()
    while True:
        now = datetime.now()
        events = event_manager.get_all_events()
        for event in events:
            event_start_time = datetime.fromisoformat(event.start_time)
            time_until_event = event_start_time - now
            # Unique key for this occurrence
            reminder_key = f"{event.id}:{event.start_time}"
            if timedelta(0) < time_until_event <= timedelta(hours=1):
                if reminder_key not in reminded:
                    print(f"REMINDER: Event '{event.title}' is starting in {int(time_until_event.total_seconds() / 60)} minutes!")
                    if event.email:
                        send_email_notification(
                            event.email,
                            f"Reminder: {event.title}",
                            f"Your event '{event.title}' is starting at {event.start_time}."
                        )
                    reminded.add(reminder_key)
            elif time_until_event < timedelta(0):
                reminded.discard(reminder_key)
        time.sleep(60)

reminder_thread = threading.Thread(target=reminder_checker, daemon=True)
reminder_thread.start()
# --- End Reminder Feature ---

@app.route('/')
def serve_index():
    return render_template('index.html')

@app.route('/events', methods=['POST'])
def create_event():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request must contain JSON data."}), 400
    try:
        new_event = Event(
            title=data.get('title'),
            description=data.get('description'),
            start_time=data.get('start_time'),
            end_time=data.get('end_time'),
            recurrence=data.get('recurrence', 'none'),
            email=data.get('email')
        )
        event_manager.add_event(new_event)
        return jsonify(new_event.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred: " + str(e)}), 500

@app.route('/events', methods=['GET'])
def get_events():
    events = event_manager.get_all_events()
    return jsonify([event.to_dict() for event in events]), 200

@app.route('/events/<event_id>', methods=['GET'])
def get_event_by_id(event_id):
    event = event_manager.get_event(event_id)
    if event:
        return jsonify(event.to_dict()), 200
    return jsonify({"error": "Event not found"}), 404

@app.route('/events/<event_id>', methods=['PUT'])
def update_event(event_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request must contain JSON data."}), 400
    try:
        updated_event = event_manager.update_event(event_id, data)
        if updated_event:
            return jsonify(updated_event.to_dict()), 200
        return jsonify({"error": "Event not found"}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred: " + str(e)}), 500

@app.route('/events/<event_id>', methods=['DELETE'])
def delete_event(event_id):
    if event_manager.delete_event(event_id):
        return jsonify({"message": "Event deleted successfully"}), 200
    return jsonify({"error": "Event not found"}), 404

@app.route('/events/search', methods=['GET'])
def search_events():
    query = request.args.get('query', '').lower()
    if not query:
        return jsonify({"error": "Query parameter is required for search."}), 400
    matching_events = []
    events = event_manager.get_all_events()
    for event in events:
        if query in event.title.lower() or query in event.description.lower():
            matching_events.append(event.to_dict())
    return jsonify(matching_events), 200

if __name__ == '__main__':
    app.run(debug=True)
