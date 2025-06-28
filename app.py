from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta
import schedule
import time
import threading
from dateutil import parser

app = Flask(__name__)
CORS(app)

# File to store events
EVENTS_FILE = 'events.json'

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Event Scheduler System</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 30px;
        }
        .container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }
        .card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #333;
        }
        input, textarea, select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 25px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin-right: 10px;
        }
        button:hover {
            opacity: 0.9;
        }
        .event-list {
            max-height: 400px;
            overflow-y: auto;
        }
        .event-item {
            background: #f8f9fa;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }
        .event-title {
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        .event-details {
            color: #666;
            font-size: 14px;
        }
        .search-box {
            margin-bottom: 20px;
        }
        .status {
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 15px;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .api-info {
            background: #e3f2fd;
            padding: 20px;
            border-radius: 10px;
            margin-top: 30px;
        }
        .endpoint {
            background: #f5f5f5;
            padding: 10px;
            margin: 5px 0;
            border-radius: 3px;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📅 Event Scheduler System</h1>
        <p>Manage your events, meetings, and appointments efficiently</p>
    </div>

    <div class="container">
        <div class="card">
            <h2>➕ Create New Event</h2>
            <form id="eventForm">
                <div class="form-group">
                    <label for="title">Title:</label>
                    <input type="text" id="title" name="title" required>
                </div>
                <div class="form-group">
                    <label for="description">Description:</label>
                    <textarea id="description" name="description" rows="3" required></textarea>
                </div>
                <div class="form-group">
                    <label for="start_time">Start Time:</label>
                    <input type="datetime-local" id="start_time" name="start_time" required>
                </div>
                <div class="form-group">
                    <label for="end_time">End Time:</label>
                    <input type="datetime-local" id="end_time" name="end_time" required>
                </div>
                <div class="form-group">
                    <label for="recurring">Recurring:</label>
                    <select id="recurring" name="recurring">
                        <option value="">None</option>
                        <option value="daily">Daily</option>
                        <option value="weekly">Weekly</option>
                        <option value="monthly">Monthly</option>
                    </select>
                </div>
                <button type="submit">Create Event</button>
            </form>
            <div id="formStatus"></div>
        </div>

        <div class="card">
            <h2>📋 Events List</h2>
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="Search events..." style="width: 70%;">
                <button onclick="searchEvents()">Search</button>
                <button onclick="loadEvents()">Refresh</button>
            </div>
            <div id="eventsList" class="event-list"></div>
        </div>
    </div>

    <div class="api-info">
        <h2>🔧 API Endpoints</h2>
        <p>This system also provides a REST API for programmatic access:</p>
        <div class="endpoint">GET /api/health - Health check</div>
        <div class="endpoint">GET /api/events - Get all events</div>
        <div class="endpoint">POST /api/events - Create new event</div>
        <div class="endpoint">GET /api/events/{id} - Get specific event</div>
        <div class="endpoint">PUT /api/events/{id} - Update event</div>
        <div class="endpoint">DELETE /api/events/{id} - Delete event</div>
        <div class="endpoint">GET /api/events/search?q={query} - Search events</div>
        <div class="endpoint">GET /api/events/upcoming?hours={hours} - Get upcoming events</div>
    </div>

    <script>
        // Load events on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadEvents();
            setCurrentDateTime();
        });

        // Set current datetime for form inputs
        function setCurrentDateTime() {
            const now = new Date();
            const localDateTime = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
            document.getElementById('start_time').value = localDateTime;
            
            const endTime = new Date(now.getTime() + 60 * 60000); // 1 hour later
            const endDateTime = new Date(endTime.getTime() - endTime.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
            document.getElementById('end_time').value = endDateTime;
        }

        // Handle form submission
        document.getElementById('eventForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = {
                title: document.getElementById('title').value,
                description: document.getElementById('description').value,
                start_time: document.getElementById('start_time').value + ':00',
                end_time: document.getElementById('end_time').value + ':00',
                recurring: document.getElementById('recurring').value || null
            };

            fetch('/api/events', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showStatus('Event created successfully!', 'success');
                    document.getElementById('eventForm').reset();
                    setCurrentDateTime();
                    loadEvents();
                } else {
                    showStatus('Error: ' + data.error, 'error');
                }
            })
            .catch(error => {
                showStatus('Error: ' + error.message, 'error');
            });
        });

        // Load all events
        function loadEvents() {
            fetch('/api/events')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    displayEvents(data.events);
                } else {
                    showStatus('Error loading events: ' + data.error, 'error');
                }
            })
            .catch(error => {
                showStatus('Error: ' + error.message, 'error');
            });
        }

        // Display events in the list
        function displayEvents(events) {
            const eventsList = document.getElementById('eventsList');
            if (events.length === 0) {
                eventsList.innerHTML = '<p>No events found.</p>';
                return;
            }

            eventsList.innerHTML = events.map(event => `
                <div class="event-item">
                    <div class="event-title">${event.title}</div>
                    <div class="event-details">
                        <strong>Description:</strong> ${event.description}<br>
                        <strong>Start:</strong> ${formatDateTime(event.start_time)}<br>
                        <strong>End:</strong> ${formatDateTime(event.end_time)}<br>
                        ${event.recurring ? `<strong>Recurring:</strong> ${event.recurring}<br>` : ''}
                        <strong>ID:</strong> ${event.id}
                    </div>
                    <button onclick="deleteEvent(${event.id})" style="background: #dc3545; margin-top: 10px;">Delete</button>
                </div>
            `).join('');
        }

        // Search events
        function searchEvents() {
            const query = document.getElementById('searchInput').value;
            if (!query) {
                loadEvents();
                return;
            }

            fetch(`/api/events/search?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    displayEvents(data.events);
                } else {
                    showStatus('Error searching events: ' + data.error, 'error');
                }
            })
            .catch(error => {
                showStatus('Error: ' + error.message, 'error');
            });
        }

        // Delete event
        function deleteEvent(eventId) {
            if (confirm('Are you sure you want to delete this event?')) {
                fetch(`/api/events/${eventId}`, {
                    method: 'DELETE'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showStatus('Event deleted successfully!', 'success');
                        loadEvents();
                    } else {
                        showStatus('Error deleting event: ' + data.error, 'error');
                    }
                })
                .catch(error => {
                    showStatus('Error: ' + error.message, 'error');
                });
            }
        }

        // Show status message
        function showStatus(message, type) {
            const statusDiv = document.getElementById('formStatus');
            statusDiv.innerHTML = `<div class="status ${type}">${message}</div>`;
            setTimeout(() => {
                statusDiv.innerHTML = '';
            }, 5000);
        }

        // Format datetime for display
        function formatDateTime(dateTimeString) {
            const date = new Date(dateTimeString);
            return date.toLocaleString();
        }
    </script>
</body>
</html>
"""

class EventScheduler:
    def __init__(self, events_file=None):
        self.events_file = events_file or EVENTS_FILE
        self.events = []
        self.load_events()
    
    def load_events(self):
        """Load events from JSON file"""
        if os.path.exists(self.events_file):
            try:
                with open(self.events_file, 'r') as file:
                    self.events = json.load(file)
            except json.JSONDecodeError:
                self.events = []
        else:
            self.events = []
    
    def save_events(self):
        """Save events to JSON file"""
        with open(self.events_file, 'w') as file:
            json.dump(self.events, file, indent=2, default=str)
    
    def add_event(self, title, description, start_time, end_time, recurring=None):
        """Add a new event"""
        # Generate next available ID
        next_id = 1
        if self.events:
            next_id = max(event['id'] for event in self.events) + 1
        
        event = {
            'id': next_id,
            'title': title,
            'description': description,
            'start_time': start_time,
            'end_time': end_time,
            'recurring': recurring,
            'created_at': datetime.now().isoformat()
        }
        self.events.append(event)
        self.save_events()
        return event
    
    def get_all_events(self):
        """Get all events sorted by start time"""
        return sorted(self.events, key=lambda x: x['start_time'])
    
    def get_event_by_id(self, event_id):
        """Get event by ID"""
        for event in self.events:
            if event['id'] == event_id:
                return event
        return None
    
    def update_event(self, event_id, title=None, description=None, start_time=None, end_time=None, recurring=None):
        """Update an existing event"""
        event = self.get_event_by_id(event_id)
        if not event:
            return None
        
        if title is not None:
            event['title'] = title
        if description is not None:
            event['description'] = description
        if start_time is not None:
            event['start_time'] = start_time
        if end_time is not None:
            event['end_time'] = end_time
        if recurring is not None:
            event['recurring'] = recurring
        
        self.save_events()
        return event
    
    def delete_event(self, event_id):
        """Delete an event"""
        event = self.get_event_by_id(event_id)
        if not event:
            return False
        
        self.events.remove(event)
        self.save_events()
        return True
    
    def search_events(self, query):
        """Search events by title or description"""
        query = query.lower()
        results = []
        for event in self.events:
            if (query in event['title'].lower() or 
                query in event['description'].lower()):
                results.append(event)
        return results
    
    def get_upcoming_events(self, hours=1):
        """Get events that are due within the specified hours"""
        now = datetime.now()
        upcoming = []
        for event in self.events:
            try:
                start_time = parser.parse(event['start_time'])
                time_diff = start_time - now
                if timedelta(0) <= time_diff <= timedelta(hours=hours):
                    upcoming.append(event)
            except (ValueError, TypeError):
                # Skip events with invalid datetime
                continue
        return upcoming

# Initialize the scheduler
scheduler = EventScheduler()

def check_reminders():
    """Check for upcoming events and display reminders"""
    upcoming = scheduler.get_upcoming_events(1)  # Next hour
    if upcoming:
        print("\n=== REMINDERS ===")
        for event in upcoming:
            start_time = parser.parse(event['start_time'])
            print(f"REMINDER: {event['title']} starts at {start_time.strftime('%H:%M')}")
        print("================\n")

# Start reminder thread
def start_reminder_thread():
    """Start the reminder checking thread"""
    schedule.every().minute.do(check_reminders)
    while True:
        schedule.run_pending()
        time.sleep(60)

reminder_thread = threading.Thread(target=start_reminder_thread, daemon=True)
reminder_thread.start()

# API Routes

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get all events"""
    try:
        events = scheduler.get_all_events()
        return jsonify({'success': True, 'events': events}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/events', methods=['POST'])
def create_event():
    """Create a new event"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'description', 'start_time', 'end_time']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Validate datetime format
        try:
            start_time = parser.parse(data['start_time'])
            end_time = parser.parse(data['end_time'])
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid datetime format'}), 400
        
        # Validate that end_time is after start_time
        if end_time <= start_time:
            return jsonify({'success': False, 'error': 'End time must be after start time'}), 400
        
        # Create event
        event = scheduler.add_event(
            title=data['title'],
            description=data['description'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            recurring=data.get('recurring')
        )
        
        return jsonify({'success': True, 'event': event}), 201
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    """Get a specific event"""
    try:
        event = scheduler.get_event_by_id(event_id)
        if not event:
            return jsonify({'success': False, 'error': 'Event not found'}), 404
        
        return jsonify({'success': True, 'event': event}), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    """Update an existing event"""
    try:
        data = request.get_json()
        
        # Validate datetime format if provided
        if 'start_time' in data:
            try:
                start_time = parser.parse(data['start_time'])
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid start_time format'}), 400
        
        if 'end_time' in data:
            try:
                end_time = parser.parse(data['end_time'])
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid end_time format'}), 400
        
        # Validate that end_time is after start_time if both are provided
        if 'start_time' in data and 'end_time' in data:
            if end_time <= start_time:
                return jsonify({'success': False, 'error': 'End time must be after start time'}), 400
        
        # Update event
        event = scheduler.update_event(
            event_id=event_id,
            title=data.get('title'),
            description=data.get('description'),
            start_time=data.get('start_time'),
            end_time=data.get('end_time'),
            recurring=data.get('recurring')
        )
        
        if not event:
            return jsonify({'success': False, 'error': 'Event not found'}), 404
        
        return jsonify({'success': True, 'event': event}), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    """Delete an event"""
    try:
        success = scheduler.delete_event(event_id)
        if not success:
            return jsonify({'success': False, 'error': 'Event not found'}), 404
        
        return jsonify({'success': True, 'message': 'Event deleted successfully'}), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/events/search', methods=['GET'])
def search_events():
    """Search events by title or description"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'success': False, 'error': 'Search query is required'}), 400
        
        results = scheduler.search_events(query)
        return jsonify({'success': True, 'events': results}), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/events/upcoming', methods=['GET'])
def get_upcoming_events():
    """Get upcoming events within specified hours"""
    try:
        hours = request.args.get('hours', 1, type=int)
        upcoming = scheduler.get_upcoming_events(hours)
        return jsonify({'success': True, 'events': upcoming}), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'success': True, 'status': 'healthy'}), 200

if __name__ == '__main__':
    print("Event Scheduler System starting...")
    print("Reminder system is active - checking every minute")
    app.run(debug=True, host='0.0.0.0', port=5000) 