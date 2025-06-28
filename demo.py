#!/usr/bin/env python3
"""
Demo script for the Event Scheduler System
This script demonstrates the core functionality of the Event Scheduler API
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

def print_separator(title):
    """Print a formatted separator with title"""
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")

def print_response(response, title):
    """Print formatted API response"""
    print(f"\n{title}:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def demo_health_check():
    """Demo health check endpoint"""
    print_separator("HEALTH CHECK")
    
    response = requests.get(f"{API_BASE}/health")
    print_response(response, "Health Check")

def demo_create_events():
    """Demo creating multiple events"""
    print_separator("CREATING EVENTS")
    
    events = [
        {
            "title": "Team Standup Meeting",
            "description": "Daily team standup to discuss progress and blockers",
            "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
            "end_time": (datetime.now() + timedelta(hours=1, minutes=30)).isoformat(),
            "recurring": "daily"
        },
        {
            "title": "Client Presentation",
            "description": "Present project progress to the client",
            "start_time": (datetime.now() + timedelta(hours=3)).isoformat(),
            "end_time": (datetime.now() + timedelta(hours=4, minutes=30)).isoformat()
        },
        {
            "title": "Code Review Session",
            "description": "Review pull requests and discuss code quality",
            "start_time": (datetime.now() + timedelta(hours=6)).isoformat(),
            "end_time": (datetime.now() + timedelta(hours=7)).isoformat(),
            "recurring": "weekly"
        }
    ]
    
    created_events = []
    for i, event_data in enumerate(events, 1):
        print(f"\nCreating Event {i}: {event_data['title']}")
        response = requests.post(
            f"{API_BASE}/events",
            json=event_data,
            headers={"Content-Type": "application/json"}
        )
        print_response(response, f"Create Event {i}")
        
        if response.status_code == 201:
            created_events.append(response.json()['event'])
    
    return created_events

def demo_get_all_events():
    """Demo getting all events"""
    print_separator("GETTING ALL EVENTS")
    
    response = requests.get(f"{API_BASE}/events")
    print_response(response, "Get All Events")
    
    if response.status_code == 200:
        events = response.json()['events']
        print(f"\nTotal Events: {len(events)}")
        for event in events:
            print(f"- {event['title']} (ID: {event['id']})")

def demo_get_event_by_id(event_id):
    """Demo getting a specific event"""
    print_separator(f"GETTING EVENT BY ID: {event_id}")
    
    response = requests.get(f"{API_BASE}/events/{event_id}")
    print_response(response, f"Get Event {event_id}")

def demo_update_event(event_id):
    """Demo updating an event"""
    print_separator(f"UPDATING EVENT: {event_id}")
    
    update_data = {
        "title": "Updated Team Standup Meeting",
        "description": "Updated daily team standup with new agenda items"
    }
    
    response = requests.put(
        f"{API_BASE}/events/{event_id}",
        json=update_data,
        headers={"Content-Type": "application/json"}
    )
    print_response(response, f"Update Event {event_id}")

def demo_search_events():
    """Demo searching events"""
    print_separator("SEARCHING EVENTS")
    
    # Search for "meeting"
    response = requests.get(f"{API_BASE}/events/search?q=meeting")
    print_response(response, "Search for 'meeting'")
    
    # Search for "client"
    response = requests.get(f"{API_BASE}/events/search?q=client")
    print_response(response, "Search for 'client'")

def demo_get_upcoming_events():
    """Demo getting upcoming events"""
    print_separator("GETTING UPCOMING EVENTS")
    
    # Get events in next 2 hours
    response = requests.get(f"{API_BASE}/events/upcoming?hours=2")
    print_response(response, "Upcoming Events (next 2 hours)")
    
    # Get events in next 5 hours
    response = requests.get(f"{API_BASE}/events/upcoming?hours=5")
    print_response(response, "Upcoming Events (next 5 hours)")

def demo_error_handling():
    """Demo error handling"""
    print_separator("ERROR HANDLING DEMO")
    
    # Try to get non-existent event
    print("\n1. Getting non-existent event:")
    response = requests.get(f"{API_BASE}/events/999")
    print_response(response, "Get Non-existent Event")
    
    # Try to create event with invalid data
    print("\n2. Creating event with invalid data:")
    invalid_data = {
        "title": "Invalid Event",
        "description": "Event with end time before start time",
        "start_time": "2024-01-15T11:00:00",
        "end_time": "2024-01-15T10:00:00"
    }
    response = requests.post(
        f"{API_BASE}/events",
        json=invalid_data,
        headers={"Content-Type": "application/json"}
    )
    print_response(response, "Create Invalid Event")
    
    # Try to create event with missing fields
    print("\n3. Creating event with missing fields:")
    incomplete_data = {
        "title": "Incomplete Event"
    }
    response = requests.post(
        f"{API_BASE}/events",
        json=incomplete_data,
        headers={"Content-Type": "application/json"}
    )
    print_response(response, "Create Incomplete Event")

def demo_reminder_system():
    """Demo the reminder system"""
    print_separator("REMINDER SYSTEM")
    
    print("The reminder system runs in the background and checks for upcoming events every minute.")
    print("It will display reminders for events due within the next hour.")
    print("\nTo see reminders in action:")
    print("1. Create an event scheduled for the next 30-60 minutes")
    print("2. Wait for the reminder to appear in the console")
    print("3. The reminder will show automatically every minute")

def main():
    """Main demo function"""
    print("🚀 Event Scheduler System Demo")
    print("This demo will showcase all the features of the Event Scheduler API")
    
    # Check if server is running
    try:
        demo_health_check()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the server!")
        print("Please make sure the Flask application is running:")
        print("python app.py")
        return
    
    # Run all demos
    try:
        # Create events
        created_events = demo_create_events()
        
        # Get all events
        demo_get_all_events()
        
        # Get specific event
        if created_events:
            demo_get_event_by_id(created_events[0]['id'])
        
        # Update event
        if created_events:
            demo_update_event(created_events[0]['id'])
        
        # Search events
        demo_search_events()
        
        # Get upcoming events
        demo_get_upcoming_events()
        
        # Error handling
        demo_error_handling()
        
        # Reminder system info
        demo_reminder_system()
        
        print_separator("DEMO COMPLETED")
        print("✅ All demos completed successfully!")
        print("\nThe Event Scheduler System is now running with:")
        print("- Automatic reminders every minute")
        print("- Data persistence in events.json")
        print("- Full REST API functionality")
        
        print("\nYou can continue using the API or test with Postman collection.")
        print("Press Ctrl+C to stop the application.")
        
        # Keep the demo running to show reminders
        while True:
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\n\n👋 Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")

if __name__ == "__main__":
    main() 
 