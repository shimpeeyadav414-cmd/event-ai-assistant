from event_roles import EventRoleAssistant

def main():
    print("🎉 Welcome to Event Experience AI Assistant 🎉")

    roles = ["Organizer", "Guest", "Attendee", "Volunteer", "Staff", "Security"]

    for role in roles:
        assistant = EventRoleAssistant(role, context={"location": "Lucknow, India"})
        print(f"\n--- {role} Features ---")
        print(assistant.get_features())

if __name__ == "__main__":
    main()
from calendar_integration import add_event_to_calendar

if __name__ == "__main__":
    print("🎉 Welcome to Event Experience AI Assistant 🎉")
    add_event_to_calendar("Annual Tech Conference - Lucknow")
