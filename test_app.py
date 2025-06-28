import pytest
import json
import os
import tempfile
from datetime import datetime, timedelta
from app import app, EventScheduler, scheduler

@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def test_scheduler():
    """Create a test scheduler instance"""
    # Use a temporary file for testing
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp:
        test_file = tmp.name
    
    test_scheduler = EventScheduler(events_file=test_file)
    # Ensure clean state
    test_scheduler.events = []
    test_scheduler.save_events()
    
    yield test_scheduler
    
    # Clean up after tests
    if os.path.exists(test_file):
        os.remove(test_file)

def clear_events():
    """Helper function to clear events from the main scheduler"""
    if os.path.exists('events.json'):
        os.remove('events.json')
    scheduler.events = []
    scheduler.save_events()

class TestEventScheduler:
    """Test cases for EventScheduler class"""
    
    def test_add_event(self, test_scheduler):
        """Test adding a new event"""
        event = test_scheduler.add_event(
            title="Test Meeting",
            description="A test meeting",
            start_time="2024-01-15T10:00:00",
            end_time="2024-01-15T11:00:00"
        )
        
        assert event['title'] == "Test Meeting"
        assert event['description'] == "A test meeting"
        assert event['id'] == 1
        assert len(test_scheduler.events) == 1
    
    def test_get_all_events(self, test_scheduler):
        """Test getting all events sorted by start time"""
        # Add events in reverse order
        test_scheduler.add_event(
            title="Later Event",
            description="Later event",
            start_time="2024-01-15T14:00:00",
            end_time="2024-01-15T15:00:00"
        )
        test_scheduler.add_event(
            title="Earlier Event",
            description="Earlier event",
            start_time="2024-01-15T10:00:00",
            end_time="2024-01-15T11:00:00"
        )
        
        events = test_scheduler.get_all_events()
        assert len(events) == 2
        assert events[0]['title'] == "Earlier Event"
        assert events[1]['title'] == "Later Event"
    
    def test_get_event_by_id(self, test_scheduler):
        """Test getting event by ID"""
        event = test_scheduler.add_event(
            title="Test Event",
            description="Test description",
            start_time="2024-01-15T10:00:00",
            end_time="2024-01-15T11:00:00"
        )
        
        found_event = test_scheduler.get_event_by_id(1)
        assert found_event is not None
        assert found_event['title'] == "Test Event"
        
        # Test non-existent event
        not_found = test_scheduler.get_event_by_id(999)
        assert not_found is None
    
    def test_update_event(self, test_scheduler):
        """Test updating an event"""
        event = test_scheduler.add_event(
            title="Original Title",
            description="Original description",
            start_time="2024-01-15T10:00:00",
            end_time="2024-01-15T11:00:00"
        )
        
        updated_event = test_scheduler.update_event(
            event_id=1,
            title="Updated Title",
            description="Updated description"
        )
        
        assert updated_event['title'] == "Updated Title"
        assert updated_event['description'] == "Updated description"
        
        # Test updating non-existent event
        result = test_scheduler.update_event(event_id=999, title="New Title")
        assert result is None
    
    def test_delete_event(self, test_scheduler):
        """Test deleting an event"""
        event = test_scheduler.add_event(
            title="To Delete",
            description="Will be deleted",
            start_time="2024-01-15T10:00:00",
            end_time="2024-01-15T11:00:00"
        )
        
        assert len(test_scheduler.events) == 1
        
        success = test_scheduler.delete_event(1)
        assert success is True
        assert len(test_scheduler.events) == 0
        
        # Test deleting non-existent event
        success = test_scheduler.delete_event(999)
        assert success is False
    
    def test_search_events(self, test_scheduler):
        """Test searching events"""
        test_scheduler.add_event(
            title="Python Meeting",
            description="Discuss Python development",
            start_time="2024-01-15T10:00:00",
            end_time="2024-01-15T11:00:00"
        )
        test_scheduler.add_event(
            title="JavaScript Meeting",
            description="Discuss JavaScript development",
            start_time="2024-01-15T14:00:00",
            end_time="2024-01-15T15:00:00"
        )
        
        # Search by title
        results = test_scheduler.search_events("Python")
        assert len(results) == 1
        assert results[0]['title'] == "Python Meeting"
        
        # Search by description
        results = test_scheduler.search_events("JavaScript")
        assert len(results) == 1
        assert results[0]['title'] == "JavaScript Meeting"
        
        # Search with no results
        results = test_scheduler.search_events("NonExistent")
        assert len(results) == 0
    
    def test_get_upcoming_events(self, test_scheduler):
        """Test getting upcoming events"""
        # Add an event in the future
        future_time = datetime.now() + timedelta(hours=2)
        test_scheduler.add_event(
            title="Future Event",
            description="Event in 2 hours",
            start_time=future_time.isoformat(),
            end_time=(future_time + timedelta(hours=1)).isoformat()
        )
        
        # Add an event in the past
        past_time = datetime.now() - timedelta(hours=2)
        test_scheduler.add_event(
            title="Past Event",
            description="Event 2 hours ago",
            start_time=past_time.isoformat(),
            end_time=(past_time + timedelta(hours=1)).isoformat()
        )
        
        upcoming = test_scheduler.get_upcoming_events(hours=3)
        assert len(upcoming) == 1
        assert upcoming[0]['title'] == "Future Event"

class TestAPIEndpoints:
    """Test cases for API endpoints"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/api/health')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert data['status'] == 'healthy'
    
    def test_create_event(self, client):
        """Test creating an event via API"""
        # Clear events before test
        clear_events()
        
        event_data = {
            'title': 'API Test Event',
            'description': 'Test event created via API',
            'start_time': '2024-01-15T10:00:00',
            'end_time': '2024-01-15T11:00:00'
        }
        
        response = client.post('/api/events', 
                             data=json.dumps(event_data),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 201
        assert data['success'] is True
        assert data['event']['title'] == 'API Test Event'
    
    def test_create_event_missing_fields(self, client):
        """Test creating an event with missing required fields"""
        # Clear events before test
        clear_events()
        
        event_data = {
            'title': 'Incomplete Event'
            # Missing description, start_time, end_time
        }
        
        response = client.post('/api/events',
                             data=json.dumps(event_data),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert data['success'] is False
        assert 'Missing required field' in data['error']
    
    def test_create_event_invalid_datetime(self, client):
        """Test creating an event with invalid datetime"""
        # Clear events before test
        clear_events()
        
        event_data = {
            'title': 'Invalid Event',
            'description': 'Event with invalid datetime',
            'start_time': 'invalid-datetime',
            'end_time': '2024-01-15T11:00:00'
        }
        
        response = client.post('/api/events',
                             data=json.dumps(event_data),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert data['success'] is False
        assert 'Invalid datetime format' in data['error']
    
    def test_create_event_end_before_start(self, client):
        """Test creating an event where end time is before start time"""
        # Clear events before test
        clear_events()
        
        event_data = {
            'title': 'Invalid Event',
            'description': 'Event with end before start',
            'start_time': '2024-01-15T11:00:00',
            'end_time': '2024-01-15T10:00:00'
        }
        
        response = client.post('/api/events',
                             data=json.dumps(event_data),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert data['success'] is False
        assert 'End time must be after start time' in data['error']
    
    def test_get_events(self, client):
        """Test getting all events"""
        # Clear events before test
        clear_events()
        
        response = client.get('/api/events')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert 'events' in data
    
    def test_get_event_by_id(self, client):
        """Test getting a specific event by ID"""
        # Clear events before test
        clear_events()
        
        # First create an event
        event_data = {
            'title': 'Test Event',
            'description': 'Test description',
            'start_time': '2024-01-15T10:00:00',
            'end_time': '2024-01-15T11:00:00'
        }
        
        create_response = client.post('/api/events',
                                    data=json.dumps(event_data),
                                    content_type='application/json')
        created_event = json.loads(create_response.data)['event']
        
        # Then get it by ID
        response = client.get(f'/api/events/{created_event["id"]}')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert data['event']['title'] == 'Test Event'
    
    def test_get_nonexistent_event(self, client):
        """Test getting a non-existent event"""
        # Clear events before test
        clear_events()
        
        response = client.get('/api/events/999')
        data = json.loads(response.data)
        
        assert response.status_code == 404
        assert data['success'] is False
        assert 'Event not found' in data['error']
    
    def test_update_event(self, client):
        """Test updating an event"""
        # Clear events before test
        clear_events()
        
        # First create an event
        event_data = {
            'title': 'Original Title',
            'description': 'Original description',
            'start_time': '2024-01-15T10:00:00',
            'end_time': '2024-01-15T11:00:00'
        }
        
        create_response = client.post('/api/events',
                                    data=json.dumps(event_data),
                                    content_type='application/json')
        created_event = json.loads(create_response.data)['event']
        
        # Then update it
        update_data = {
            'title': 'Updated Title',
            'description': 'Updated description'
        }
        
        response = client.put(f'/api/events/{created_event["id"]}',
                            data=json.dumps(update_data),
                            content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert data['event']['title'] == 'Updated Title'
        assert data['event']['description'] == 'Updated description'
    
    def test_delete_event(self, client):
        """Test deleting an event"""
        # Clear events before test
        clear_events()
        
        # First create an event
        event_data = {
            'title': 'To Delete',
            'description': 'Will be deleted',
            'start_time': '2024-01-15T10:00:00',
            'end_time': '2024-01-15T11:00:00'
        }
        
        create_response = client.post('/api/events',
                                    data=json.dumps(event_data),
                                    content_type='application/json')
        created_event = json.loads(create_response.data)['event']
        
        # Then delete it
        response = client.delete(f'/api/events/{created_event["id"]}')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert 'deleted successfully' in data['message']
    
    def test_search_events(self, client):
        """Test searching events"""
        # Clear events before test
        clear_events()
        
        # First create some events
        events = [
            {
                'title': 'Python Meeting',
                'description': 'Discuss Python development',
                'start_time': '2024-01-15T10:00:00',
                'end_time': '2024-01-15T11:00:00'
            },
            {
                'title': 'JavaScript Meeting',
                'description': 'Discuss JavaScript development',
                'start_time': '2024-01-15T14:00:00',
                'end_time': '2024-01-15T15:00:00'
            }
        ]
        
        for event in events:
            client.post('/api/events',
                       data=json.dumps(event),
                       content_type='application/json')
        
        # Search for Python events
        response = client.get('/api/events/search?q=Python')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert len(data['events']) == 1
        assert data['events'][0]['title'] == 'Python Meeting'
    
    def test_search_events_no_query(self, client):
        """Test searching events without query parameter"""
        # Clear events before test
        clear_events()
        
        response = client.get('/api/events/search')
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert data['success'] is False
        assert 'Search query is required' in data['error']
    
    def test_get_upcoming_events(self, client):
        """Test getting upcoming events"""
        # Clear events before test
        clear_events()
        
        response = client.get('/api/events/upcoming?hours=2')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert 'events' in data

if __name__ == '__main__':
    pytest.main([__file__]) 