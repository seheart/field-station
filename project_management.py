#!/usr/bin/env python3
"""
Field Station - Project Management & SDLC Integration
Creates formal tickets, epics, sprints, and project structure
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

class TicketType(Enum):
    EPIC = "epic"
    STORY = "story"
    BUG = "bug"
    TASK = "task"
    SUBTASK = "subtask"

class TicketStatus(Enum):
    BACKLOG = "backlog"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    CODE_REVIEW = "code_review"
    QA_TESTING = "qa_testing"
    DONE = "done"
    BLOCKED = "blocked"

class Priority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class Ticket:
    id: str
    title: str
    description: str
    ticket_type: TicketType
    status: TicketStatus
    priority: Priority
    assignee: Optional[str] = None
    reporter: str = "System"
    epic_id: Optional[str] = None
    parent_id: Optional[str] = None
    story_points: Optional[int] = None
    sprint_id: Optional[str] = None
    created_date: str = None
    updated_date: str = None
    due_date: Optional[str] = None
    labels: List[str] = None
    acceptance_criteria: List[str] = None
    qa_test_ids: List[str] = None
    
    def __post_init__(self):
        if self.created_date is None:
            self.created_date = datetime.now().isoformat()
        if self.updated_date is None:
            self.updated_date = datetime.now().isoformat()
        if self.labels is None:
            self.labels = []
        if self.acceptance_criteria is None:
            self.acceptance_criteria = []
        if self.qa_test_ids is None:
            self.qa_test_ids = []

@dataclass
class Epic:
    id: str
    title: str
    description: str
    status: TicketStatus
    priority: Priority
    start_date: str
    target_date: str
    progress: float = 0.0
    ticket_ids: List[str] = None
    
    def __post_init__(self):
        if self.ticket_ids is None:
            self.ticket_ids = []

@dataclass
class Sprint:
    id: str
    name: str
    start_date: str
    end_date: str
    goal: str
    status: str = "active"
    ticket_ids: List[str] = None
    capacity_points: int = 20
    committed_points: int = 0
    
    def __post_init__(self):
        if self.ticket_ids is None:
            self.ticket_ids = []

class ProjectManager:
    """Manages Field Station project tickets, epics, and sprints"""
    
    def __init__(self):
        self.tickets_file = "project_tickets.json"
        self.epics_file = "project_epics.json"
        self.sprints_file = "project_sprints.json"
        self.load_project_data()
    
    def load_project_data(self):
        """Load existing project data"""
        self.tickets = self.load_json_file(self.tickets_file, {})
        self.epics = self.load_json_file(self.epics_file, {})
        self.sprints = self.load_json_file(self.sprints_file, {})
    
    def load_json_file(self, filename: str, default: Any) -> Any:
        """Load JSON file with fallback"""
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        return default
    
    def save_project_data(self):
        """Save all project data"""
        with open(self.tickets_file, 'w') as f:
            json.dump(self.tickets, f, indent=2, default=str)
        with open(self.epics_file, 'w') as f:
            json.dump(self.epics, f, indent=2, default=str)
        with open(self.sprints_file, 'w') as f:
            json.dump(self.sprints, f, indent=2, default=str)
    
    def create_ticket(self, ticket: Ticket) -> str:
        """Create a new ticket"""
        self.tickets[ticket.id] = asdict(ticket)
        self.save_project_data()
        return ticket.id
    
    def create_epic(self, epic: Epic) -> str:
        """Create a new epic"""
        self.epics[epic.id] = asdict(epic)
        self.save_project_data()
        return epic.id
    
    def create_sprint(self, sprint: Sprint) -> str:
        """Create a new sprint"""
        self.sprints[sprint.id] = asdict(sprint)
        self.save_project_data()
        return sprint.id
    
    def get_tickets_by_epic(self, epic_id: str) -> List[Dict]:
        """Get all tickets for an epic"""
        return [ticket for ticket in self.tickets.values() 
                if ticket.get('epic_id') == epic_id]
    
    def get_tickets_by_sprint(self, sprint_id: str) -> List[Dict]:
        """Get all tickets for a sprint"""
        return [ticket for ticket in self.tickets.values() 
                if ticket.get('sprint_id') == sprint_id]
    
    def update_epic_progress(self, epic_id: str):
        """Update epic progress based on ticket completion"""
        if epic_id not in self.epics:
            return
        
        tickets = self.get_tickets_by_epic(epic_id)
        if not tickets:
            return
        
        completed = sum(1 for ticket in tickets if ticket.get('status') == 'done')
        total = len(tickets)
        progress = (completed / total) * 100 if total > 0 else 0
        
        self.epics[epic_id]['progress'] = progress
        self.save_project_data()

def create_field_station_project_structure():
    """Create complete Field Station project structure"""
    pm = ProjectManager()
    
    print("🏗️  Creating Field Station Project Structure...")
    print("=" * 60)
    
    # Create Epics
    epics_data = [
        {
            "id": "FS-EPIC-001",
            "title": "Core Game Engine & UI Framework",
            "description": "Build the foundational game engine, UI framework, and core game mechanics",
            "priority": Priority.CRITICAL,
            "start_date": "2024-09-01",
            "target_date": "2024-12-01"
        },
        {
            "id": "FS-EPIC-002", 
            "title": "User Experience & Interface Design",
            "description": "Design and implement all user interfaces, menus, and user experience flows",
            "priority": Priority.HIGH,
            "start_date": "2024-10-01",
            "target_date": "2024-11-15"
        },
        {
            "id": "FS-EPIC-003",
            "title": "Quality Assurance & Testing Framework", 
            "description": "Build comprehensive QA framework with automated testing and user story validation",
            "priority": Priority.HIGH,
            "start_date": "2024-11-01",
            "target_date": "2024-12-15"
        },
        {
            "id": "FS-EPIC-004",
            "title": "Documentation & Project Management",
            "description": "Create comprehensive documentation, wiki, and project management systems",
            "priority": Priority.MEDIUM,
            "start_date": "2024-11-15",
            "target_date": "2025-01-01"
        },
        {
            "id": "FS-EPIC-005",
            "title": "Game Features & Content",
            "description": "Implement core game features, farming mechanics, and game content",
            "priority": Priority.HIGH,
            "start_date": "2024-12-01", 
            "target_date": "2025-03-01"
        }
    ]
    
    for epic_data in epics_data:
        epic = Epic(
            id=epic_data["id"],
            title=epic_data["title"],
            description=epic_data["description"],
            status=TicketStatus.IN_PROGRESS,
            priority=epic_data["priority"],
            start_date=epic_data["start_date"],
            target_date=epic_data["target_date"]
        )
        pm.create_epic(epic)
        print(f"📋 Created Epic: {epic.id} - {epic.title}")
    
    # Create Current Sprint
    current_sprint = Sprint(
        id="FS-SPRINT-001",
        name="Sprint 1: QA Framework & Documentation",
        start_date="2024-09-01",
        end_date="2024-09-15", 
        goal="Complete QA framework implementation and documentation system",
        capacity_points=25
    )
    pm.create_sprint(current_sprint)
    print(f"🏃 Created Sprint: {current_sprint.name}")
    
    # Create Tickets based on current work
    tickets_data = [
        # Epic 1: Core Game Engine
        {
            "id": "FS-001",
            "title": "Fix Enter Key Feedback in Farm Name Input",
            "description": "When user presses Enter in farm name field, provide visual feedback that the action was processed",
            "type": TicketType.BUG,
            "priority": Priority.HIGH,
            "epic_id": "FS-EPIC-002",
            "sprint_id": "FS-SPRINT-001",
            "story_points": 3,
            "acceptance_criteria": [
                "Enter key press provides visual feedback",
                "Field state clearly indicates input was accepted",
                "User knows what happened after pressing Enter"
            ],
            "qa_test_ids": ["US003"]
        },
        {
            "id": "FS-002", 
            "title": "Fix Menu Click Detection Issues",
            "description": "Main menu items are not responding to mouse clicks for navigation",
            "type": TicketType.BUG,
            "priority": Priority.CRITICAL,
            "epic_id": "FS-EPIC-002",
            "sprint_id": "FS-SPRINT-001", 
            "story_points": 5,
            "acceptance_criteria": [
                "All menu items respond to mouse clicks",
                "Navigation works correctly between pages", 
                "Click detection rectangles are properly defined"
            ],
            "qa_test_ids": ["US001", "US010"]
        },
        {
            "id": "FS-003",
            "title": "Implement Hover Effects for Menu Items",
            "description": "Add hover effects and icon display when user hovers over menu items",
            "type": TicketType.STORY,
            "priority": Priority.MEDIUM,
            "epic_id": "FS-EPIC-002",
            "story_points": 2,
            "acceptance_criteria": [
                "Icons appear on menu item hover",
                "Smooth hover transitions",
                "Consistent hover behavior across all menu items"
            ]
        },
        # Epic 3: QA Framework  
        {
            "id": "FS-004",
            "title": "Enhanced User Flow QA Testing",
            "description": "Improve user flow QA framework to achieve higher success rates",
            "type": TicketType.TASK,
            "priority": Priority.HIGH,
            "epic_id": "FS-EPIC-003",
            "sprint_id": "FS-SPRINT-001",
            "story_points": 8,
            "acceptance_criteria": [
                "User flow QA success rate > 80%",
                "All user stories have automated tests",
                "Screenshot validation working",
                "Error reporting improved"
            ]
        },
        {
            "id": "FS-005",
            "title": "Issue Tracker Integration",
            "description": "Complete integration with Jira/GitHub for automatic issue creation",
            "type": TicketType.STORY,
            "priority": Priority.MEDIUM,
            "epic_id": "FS-EPIC-003",
            "sprint_id": "FS-SPRINT-001",
            "story_points": 5,
            "acceptance_criteria": [
                "QA failures automatically create tickets",
                "Integration works with multiple platforms",
                "Proper ticket categorization and labeling"
            ]
        },
        # Epic 4: Documentation
        {
            "id": "FS-006",
            "title": "Dark Mode Wiki Implementation", 
            "description": "Implement dark mode wiki server for project documentation",
            "type": TicketType.STORY,
            "priority": Priority.LOW,
            "epic_id": "FS-EPIC-004",
            "story_points": 3,
            "status": TicketStatus.DONE,
            "acceptance_criteria": [
                "Dark mode styling implemented",
                "All documentation accessible via browser",
                "Professional GitHub-style theming",
                "Navigation between docs works"
            ]
        },
        {
            "id": "FS-007",
            "title": "User Stories Documentation",
            "description": "Create comprehensive user stories documentation with acceptance criteria",
            "type": TicketType.TASK,
            "priority": Priority.MEDIUM,
            "epic_id": "FS-EPIC-004",
            "story_points": 2,
            "status": TicketStatus.DONE,
            "acceptance_criteria": [
                "All 10 user stories documented",
                "Acceptance criteria defined",
                "Test steps specified",
                "Integration with QA framework"
            ]
        },
        # Epic 5: Game Features
        {
            "id": "FS-008",
            "title": "Farm Setup Form Validation",
            "description": "Implement comprehensive form validation for farm setup page",
            "type": TicketType.STORY,
            "priority": Priority.HIGH,
            "epic_id": "FS-EPIC-005",
            "story_points": 5,
            "acceptance_criteria": [
                "Empty farm name disables START button",
                "Season selection required for form submission",
                "Clear visual feedback for validation states",
                "Error messages for invalid inputs"
            ],
            "qa_test_ids": ["US004"]
        },
        {
            "id": "FS-009",
            "title": "Keyboard Navigation Support",
            "description": "Add full keyboard navigation support for menu system",
            "type": TicketType.STORY, 
            "priority": Priority.MEDIUM,
            "epic_id": "FS-EPIC-002",
            "story_points": 8,
            "acceptance_criteria": [
                "Arrow keys navigate menu items",
                "Enter key activates selected items", 
                "Visual indication of selected item",
                "Tab navigation through form fields"
            ],
            "qa_test_ids": ["US002"]
        },
        {
            "id": "FS-010",
            "title": "SDLC Integration & CI/CD Pipeline",
            "description": "Set up complete SDLC integration with automated testing and deployment",
            "type": TicketType.TASK,
            "priority": Priority.MEDIUM,
            "epic_id": "FS-EPIC-003",
            "story_points": 13,
            "acceptance_criteria": [
                "Pre-commit hooks implemented",
                "CI/CD pipeline configured",
                "Automated QA testing in pipeline", 
                "Deployment gates based on QA results"
            ]
        }
    ]
    
    for ticket_data in tickets_data:
        ticket = Ticket(
            id=ticket_data["id"],
            title=ticket_data["title"], 
            description=ticket_data["description"],
            ticket_type=ticket_data["type"],
            status=ticket_data.get("status", TicketStatus.BACKLOG),
            priority=ticket_data["priority"],
            epic_id=ticket_data.get("epic_id"),
            sprint_id=ticket_data.get("sprint_id"),
            story_points=ticket_data.get("story_points"),
            acceptance_criteria=ticket_data.get("acceptance_criteria", []),
            qa_test_ids=ticket_data.get("qa_test_ids", [])
        )
        pm.create_ticket(ticket)
        print(f"🎫 Created Ticket: {ticket.id} - {ticket.title}")
    
    # Update epic progress
    for epic_id in pm.epics.keys():
        pm.update_epic_progress(epic_id)
    
    print(f"\n✅ Project structure created successfully!")
    print(f"📊 Created: {len(pm.epics)} epics, {len(pm.tickets)} tickets, {len(pm.sprints)} sprints")
    
    return pm

def generate_project_reports(pm: ProjectManager):
    """Generate project status reports"""
    print("\n" + "=" * 60)
    print("📊 FIELD STATION PROJECT STATUS REPORT")
    print("=" * 60)
    
    # Epic Status
    print("\n🏗️  EPIC STATUS:")
    for epic_id, epic_data in pm.epics.items():
        tickets = pm.get_tickets_by_epic(epic_id)
        completed = sum(1 for t in tickets if t.get('status') == 'done')
        total = len(tickets)
        progress = epic_data.get('progress', 0)
        
        print(f"  {epic_id}: {epic_data['title']}")
        print(f"    Progress: {progress:.1f}% ({completed}/{total} tickets)")
        print(f"    Priority: {epic_data['priority']} | Target: {epic_data['target_date']}")
    
    # Sprint Status
    print(f"\n🏃 CURRENT SPRINT:")
    for sprint_id, sprint_data in pm.sprints.items():
        tickets = pm.get_tickets_by_sprint(sprint_id)
        committed_points = sum(t.get('story_points', 0) for t in tickets)
        completed_points = sum(t.get('story_points', 0) for t in tickets if t.get('status') == 'done')
        
        print(f"  {sprint_data['name']}")
        print(f"    Goal: {sprint_data['goal']}")
        print(f"    Capacity: {sprint_data['capacity_points']} points")
        print(f"    Committed: {committed_points} points")
        print(f"    Completed: {completed_points} points ({completed_points/committed_points*100:.1f}%)")
        print(f"    Period: {sprint_data['start_date']} to {sprint_data['end_date']}")
    
    # High Priority Tickets
    print(f"\n🔥 HIGH PRIORITY TICKETS:")
    high_priority = [t for t in pm.tickets.values() 
                    if t.get('priority') in ['critical', 'high'] and t.get('status') != 'done']
    for ticket in sorted(high_priority, key=lambda x: x.get('priority')):
        print(f"  {ticket['id']}: {ticket['title']}")
        print(f"    Status: {ticket['status']} | Points: {ticket.get('story_points', 'N/A')}")
        print(f"    Epic: {ticket.get('epic_id', 'None')}")
    
    # QA Integration Status  
    print(f"\n🧪 QA INTEGRATION STATUS:")
    qa_tickets = [t for t in pm.tickets.values() if t.get('qa_test_ids')]
    print(f"  Tickets with QA Tests: {len(qa_tickets)}")
    print(f"  Total User Stories: 10")
    print(f"  QA Framework Status: ✅ Implemented")
    print(f"  Current QA Success Rate: 20% (needs improvement)")

def main():
    """Set up Field Station project management"""
    pm = create_field_station_project_structure()
    generate_project_reports(pm)
    
    print(f"\n💡 Next Steps:")
    print(f"  1. Review created tickets and epics")
    print(f"  2. Assign team members to tickets")
    print(f"  3. Set up integration with Jira/GitHub")
    print(f"  4. Begin sprint planning")
    print(f"  5. Configure CI/CD pipeline")
    
    print(f"\n📁 Files Created:")
    print(f"  • project_tickets.json - All project tickets")
    print(f"  • project_epics.json - Epic definitions")
    print(f"  • project_sprints.json - Sprint planning")

if __name__ == "__main__":
    main()