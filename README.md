# Event Scheduler System

A comprehensive Python Flask-based REST API for managing events, appointments, and tasks with features like reminders, recurring events, and search functionality.

## Features

### Core Features
- ✅ **Event Creation**: Create events with title, description, start time, and end time
- ✅ **Event Listing**: View all events sorted by start time (earliest first)
- ✅ **Event Updating**: Update any details of existing events
- ✅ **Event Deletion**: Delete events from the system
- ✅ **Persistence**: Events are saved to JSON file and persist between sessions

### Bonus Features
- ✅ **Unit Tests**: Comprehensive test suite using pytest
- ✅ **Reminders**: Automatic reminders for events due within the next hour (checked every minute)
- ✅ **Recurring Events**: Support for daily, weekly, and monthly recurring events
- ✅ **Search**: Search events by title or description
- ✅ **Upcoming Events**: Get events scheduled within specified hours
- ✅ **Error Handling**: Comprehensive error handling and validation
- ✅ **REST API**: Full RESTful API with proper HTTP status codes

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd event-scheduler-system
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

The application will start on `http://localhost:5000`

## API Documentation

### Base URL
```
http://localhost:5000
```

### Endpoints

#### 1. Health Check
- **GET** `/api/health`
- **Description**: Check if the API is running
- **Response**: `{"success": true, "status": "healthy"}`

#### 2. Get All Events
- **GET** `/api/events`
- **Description**: Retrieve all events sorted by start time
- **Response**: 
```json
{
  "success": true,
  "events": [
    {
      "id": 1,
      "title": "Team Meeting",
      "description": "Weekly team sync",
      "start_time": "2024-01-15T10:00:00",
      "end_time": "2024-01-15T11:00:00",
      "recurring": "weekly",
      "created_at": "2024-01-15T09:00:00"
    }
  ]
}
```

#### 3. Create Event
- **POST** `/api/events`
- **Description**: Create a new event
- **Request Body**:
```json
{
  "title": "Team Meeting",
  "description": "Weekly team sync meeting",
  "start_time": "2024-01-15T10:00:00",
  "end_time": "2024-01-15T11:00:00",
  "recurring": "weekly"
}
```
- **Response**: `{"success": true, "event": {...}}`

#### 4. Get Event by ID
- **GET** `/api/events/{id}`
- **Description**: Retrieve a specific event by ID
- **Response**: `{"success": true, "event": {...}}`

#### 5. Update Event
- **PUT** `/api/events/{id}`
- **Description**: Update an existing event (partial updates supported)
- **Request Body**:
```json
{
  "title": "Updated Title",
  "description": "Updated description"
}
```
- **Response**: `{"success": true, "event": {...}}`

#### 6. Delete Event
- **DELETE** `/api/events/{id}`
- **Description**: Delete an event
- **Response**: `{"success": true, "message": "Event deleted successfully"}`

#### 7. Search Events
- **GET** `/api/events/search?q={query}`
- **Description**: Search events by title or description
- **Response**: `{"success": true, "events": [...]}`

#### 8. Get Upcoming Events
- **GET** `/api/events/upcoming?hours={hours}`
- **Description**: Get events scheduled within specified hours (default: 1 hour)
- **Response**: `{"success": true, "events": [...]}`

## Usage Examples

### Using curl

1. **Create an event**
   ```bash
   curl -X POST http://localhost:5000/api/events \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Team Meeting",
       "description": "Weekly team sync meeting",
       "start_time": "2024-01-15T10:00:00",
       "end_time": "2024-01-15T11:00:00",
       "recurring": "weekly"
     }'
   ```

2. **Get all events**
   ```bash
   curl http://localhost:5000/api/events
   ```

3. **Update an event**
   ```bash
   curl -X PUT http://localhost:5000/api/events/1 \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Updated Team Meeting",
       "description": "Updated description"
     }'
   ```

4. **Search events**
   ```bash
   curl "http://localhost:5000/api/events/search?q=meeting"
   ```

5. **Get upcoming events**
   ```bash
   curl "http://localhost:5000/api/events/upcoming?hours=2"
   ```

6. **Delete an event**
   ```bash
   curl -X DELETE http://localhost:5000/api/events/1
   ```

### Using Postman

1. Import the provided Postman collection: `Event_Scheduler_API.postman_collection.json`
2. Set the environment variable `base_url` to `http://localhost:5000`
3. Run the requests in the collection

## Testing

### Run Unit Tests
```bash
pytest test_app.py -v
```

### Test Coverage
The test suite covers:
- Event creation, reading, updating, and deletion
- API endpoint functionality
- Error handling and validation
- Search functionality
- Upcoming events functionality

## Data Storage

Events are stored in a JSON file (`events.json`) in the project root. The file is automatically created when the first event is added and persists data between application restarts.

### Sample Data Structure
```json
[
  {
    "id": 1,
    "title": "Team Meeting",
    "description": "Weekly team sync meeting",
    "start_time": "2024-01-15T10:00:00",
    "end_time": "2024-01-15T11:00:00",
    "recurring": "weekly",
    "created_at": "2024-01-15T09:00:00"
  }
]
```

## Reminder System

The application includes an automatic reminder system that:
- Checks for upcoming events every minute
- Displays reminders for events due within the next hour
- Runs in a background thread to avoid blocking the main application

### Example Reminder Output
```
=== REMINDERS ===
REMINDER: Team Meeting starts at 10:00
================
```

## Error Handling

The API provides comprehensive error handling:

- **400 Bad Request**: Invalid input data, missing required fields
- **404 Not Found**: Event not found
- **500 Internal Server Error**: Server-side errors

### Error Response Format
```json
{
  "success": false,
  "error": "Error message description"
}
```

## Validation Rules

- **Required Fields**: `title`, `description`, `start_time`, `end_time`
- **DateTime Format**: ISO 8601 format (e.g., "2024-01-15T10:00:00")
- **Time Validation**: End time must be after start time
- **Recurring Options**: `daily`, `weekly`, `monthly`, or `null`

## Project Structure

```
event-scheduler-system/
├── app.py                              # Main Flask application
├── test_app.py                         # Unit tests
├── requirements.txt                    # Python dependencies
├── README.md                          # This file
├── Event_Scheduler_API.postman_collection.json  # Postman collection
└── events.json                        # Data storage (created automatically)
```

## Dependencies

- **Flask**: Web framework
- **Flask-CORS**: Cross-origin resource sharing
- **python-dateutil**: Date parsing utilities
- **pytest**: Testing framework
- **pytest-flask**: Flask testing utilities
- **schedule**: Task scheduling for reminders

---

**Note**: This Event Scheduler System is designed to be a robust, production-ready application with comprehensive error handling, testing, and documentation. It can be easily extended with additional features like email notifications, user authentication, or database integration. 