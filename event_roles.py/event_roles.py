class EventRoleAssistant:
    def __init__(self, role, context=None):
        self.role = role.lower()
        self.context = context or {}

    def get_features(self):
        if self.role == "organizer":
            return self.organizer_features()
        elif self.role == "guest":
            return self.guest_features()
        elif self.role == "attendee":
            return self.attendee_features()
        elif self.role == "volunteer":
            return self.volunteer_features()
        elif self.role == "staff":
            return self.staff_features()
        elif self.role == "security":
            return self.security_features()
        else:
            return "❌ Role not recognized."

    def organizer_features(self):
        return "📊 Organizer: Manage tickets, schedules, announcements, documents."

    def guest_features(self):
        return "🎟 Guest: VIP seating, calendar reminders, food ordering, parking."

    def attendee_features(self):
        return "🙌 Attendee: Live updates, nearby restaurants, social sharing, feedback."

    def volunteer_features(self):
        return "🤝 Volunteer: Task assignments, communication, emergency coordination."

    def staff_features(self):
        return "👷 Staff: Shift scheduling, resource allocation, setup checklist."

    def security_features(self):
        return "🚨 Security: Emergency alerts, crowd monitoring, lost & found."
