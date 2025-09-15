#!/usr/bin/env python3
"""
Field Station - Issue Tracker Integration
Automatically creates tickets from QA failures in Jira, GitHub, Linear, etc.
"""

import json
import requests
import sys
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

@dataclass
class QAIssue:
    """Represents a QA issue that needs to be tracked"""
    title: str
    description: str
    severity: str  # "High", "Medium", "Low"
    issue_type: str  # "Bug", "User Story", "Technical Debt"
    component: str  # "UI", "Navigation", "Form Validation"
    user_story_id: Optional[str] = None
    test_step: Optional[str] = None
    screenshot_path: Optional[str] = None
    reproduction_steps: List[str] = None

class IssueTracker(Enum):
    JIRA = "jira"
    GITHUB = "github"
    LINEAR = "linear"
    AZURE_DEVOPS = "azure"
    LOCAL_JSON = "local"  # For demo/testing

class IssueTrackerIntegration:
    """Universal issue tracker integration"""
    
    def __init__(self, tracker_type: IssueTracker, config: Dict[str, Any]):
        self.tracker_type = tracker_type
        self.config = config
        self.session = requests.Session()
        self._setup_authentication()
    
    def _setup_authentication(self):
        """Setup authentication based on tracker type"""
        if self.tracker_type == IssueTracker.JIRA:
            if 'token' in self.config:
                self.session.headers.update({
                    'Authorization': f'Bearer {self.config["token"]}',
                    'Content-Type': 'application/json'
                })
            elif 'username' in self.config and 'password' in self.config:
                self.session.auth = (self.config['username'], self.config['password'])
        
        elif self.tracker_type == IssueTracker.GITHUB:
            if 'token' in self.config:
                self.session.headers.update({
                    'Authorization': f'token {self.config["token"]}',
                    'Accept': 'application/vnd.github.v3+json'
                })
        
        elif self.tracker_type == IssueTracker.LINEAR:
            if 'api_key' in self.config:
                self.session.headers.update({
                    'Authorization': self.config['api_key'],
                    'Content-Type': 'application/json'
                })
    
    def create_issue(self, qa_issue: QAIssue) -> Optional[str]:
        """Create an issue in the configured tracker"""
        try:
            if self.tracker_type == IssueTracker.JIRA:
                return self._create_jira_issue(qa_issue)
            elif self.tracker_type == IssueTracker.GITHUB:
                return self._create_github_issue(qa_issue)
            elif self.tracker_type == IssueTracker.LINEAR:
                return self._create_linear_issue(qa_issue)
            elif self.tracker_type == IssueTracker.LOCAL_JSON:
                return self._create_local_issue(qa_issue)
            else:
                print(f"Unsupported tracker: {self.tracker_type}")
                return None
        except Exception as e:
            print(f"Error creating issue: {e}")
            return None
    
    def _create_jira_issue(self, qa_issue: QAIssue) -> Optional[str]:
        """Create a Jira issue"""
        url = f"{self.config['base_url']}/rest/api/2/issue"
        
        # Map severity to Jira priority
        priority_map = {"High": "1", "Medium": "3", "Low": "4"}
        
        payload = {
            "fields": {
                "project": {"key": self.config['project_key']},
                "summary": qa_issue.title,
                "description": self._format_jira_description(qa_issue),
                "issuetype": {"name": "Bug"},
                "priority": {"id": priority_map.get(qa_issue.severity, "3")},
                "labels": ["qa-automation", f"component-{qa_issue.component.lower()}"]
            }
        }
        
        if qa_issue.user_story_id:
            payload["fields"]["labels"].append(f"user-story-{qa_issue.user_story_id}")
        
        response = self.session.post(url, json=payload)
        if response.status_code == 201:
            issue_key = response.json()['key']
            print(f"✅ Created Jira issue: {issue_key}")
            return issue_key
        else:
            print(f"❌ Failed to create Jira issue: {response.status_code} - {response.text}")
            return None
    
    def _create_github_issue(self, qa_issue: QAIssue) -> Optional[str]:
        """Create a GitHub issue"""
        url = f"https://api.github.com/repos/{self.config['owner']}/{self.config['repo']}/issues"
        
        labels = ["qa-automation", f"component:{qa_issue.component.lower()}", f"severity:{qa_issue.severity.lower()}"]
        if qa_issue.user_story_id:
            labels.append(f"user-story:{qa_issue.user_story_id}")
        
        payload = {
            "title": qa_issue.title,
            "body": self._format_github_description(qa_issue),
            "labels": labels
        }
        
        response = self.session.post(url, json=payload)
        if response.status_code == 201:
            issue_number = response.json()['number']
            issue_url = response.json()['html_url']
            print(f"✅ Created GitHub issue: #{issue_number} - {issue_url}")
            return str(issue_number)
        else:
            print(f"❌ Failed to create GitHub issue: {response.status_code} - {response.text}")
            return None
    
    def _create_local_issue(self, qa_issue: QAIssue) -> str:
        """Create a local JSON issue for demo purposes"""
        issues_file = "qa_issues.json"
        
        # Load existing issues
        issues = []
        if os.path.exists(issues_file):
            with open(issues_file, 'r') as f:
                issues = json.load(f)
        
        # Create new issue
        issue_id = f"QA-{len(issues) + 1}"
        new_issue = {
            "id": issue_id,
            "created_at": datetime.now().isoformat(),
            "status": "Open",
            **asdict(qa_issue)
        }
        
        issues.append(new_issue)
        
        # Save back to file
        with open(issues_file, 'w') as f:
            json.dump(issues, f, indent=2)
        
        print(f"✅ Created local issue: {issue_id}")
        return issue_id
    
    def _format_jira_description(self, qa_issue: QAIssue) -> str:
        """Format description for Jira"""
        desc = f"*Automated QA Issue*\n\n"
        desc += f"*Component:* {qa_issue.component}\n"
        desc += f"*Severity:* {qa_issue.severity}\n\n"
        desc += f"*Description:*\n{qa_issue.description}\n\n"
        
        if qa_issue.user_story_id:
            desc += f"*User Story:* {qa_issue.user_story_id}\n"
        
        if qa_issue.test_step:
            desc += f"*Failed Test Step:* {qa_issue.test_step}\n"
        
        if qa_issue.reproduction_steps:
            desc += f"\n*Reproduction Steps:*\n"
            for i, step in enumerate(qa_issue.reproduction_steps, 1):
                desc += f"{i}. {step}\n"
        
        desc += f"\n*Generated by:* Field Station QA Automation"
        return desc
    
    def _format_github_description(self, qa_issue: QAIssue) -> str:
        """Format description for GitHub"""
        desc = f"## Automated QA Issue\n\n"
        desc += f"**Component:** {qa_issue.component}  \n"
        desc += f"**Severity:** {qa_issue.severity}  \n"
        desc += f"**Type:** {qa_issue.issue_type}  \n\n"
        desc += f"### Description\n{qa_issue.description}\n\n"
        
        if qa_issue.user_story_id:
            desc += f"**User Story:** {qa_issue.user_story_id}\n\n"
        
        if qa_issue.test_step:
            desc += f"**Failed Test Step:** {qa_issue.test_step}\n\n"
        
        if qa_issue.reproduction_steps:
            desc += f"### Reproduction Steps\n"
            for i, step in enumerate(qa_issue.reproduction_steps, 1):
                desc += f"{i}. {step}\n"
        
        desc += f"\n---\n*Generated by Field Station QA Automation*"
        return desc

def parse_qa_failures_to_issues(qa_results: List[Dict]) -> List[QAIssue]:
    """Convert QA test failures into trackable issues"""
    issues = []
    
    for result in qa_results:
        if not result.get('passed', True):
            # Determine severity based on test type and impact
            severity = "High"  # Default
            if "validation" in result.get('test_name', '').lower():
                severity = "Medium"
            elif "error handling" in result.get('test_name', '').lower():
                severity = "Low"
            
            issue = QAIssue(
                title=f"QA Failure: {result.get('test_name', 'Unknown Test')}",
                description=f"Automated QA test failed: {result.get('error_message', 'No details available')}",
                severity=severity,
                issue_type="Bug",
                component="UI" if "ui" in result.get('test_name', '').lower() else "Core",
                reproduction_steps=[
                    "Run automated QA suite",
                    f"Observe failure in: {result.get('test_name')}",
                    f"Error: {result.get('error_message', 'See logs')}"
                ]
            )
            issues.append(issue)
    
    return issues

def create_demo_config():
    """Create demo configuration files for different trackers"""
    
    configs = {
        "jira_config.json": {
            "tracker_type": "jira",
            "base_url": "https://your-domain.atlassian.net",
            "username": "your-email@domain.com",
            "token": "your-api-token",
            "project_key": "FIELDSTATION"
        },
        "github_config.json": {
            "tracker_type": "github", 
            "owner": "your-username",
            "repo": "field-station",
            "token": "ghp_your_github_token"
        },
        "local_config.json": {
            "tracker_type": "local"
        }
    }
    
    for filename, config in configs.items():
        if not os.path.exists(filename):
            with open(filename, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"📝 Created demo config: {filename}")

def main():
    """Demo the issue tracker integration"""
    print("🎯 Field Station Issue Tracker Integration")
    print("=" * 50)
    
    # Create demo config files
    create_demo_config()
    
    # Demo with local tracker
    print("\n📋 Creating demo QA issues...")
    
    config = {"tracker_type": "local"}
    tracker = IssueTrackerIntegration(IssueTracker.LOCAL_JSON, config)
    
    # Demo issues based on actual QA failures
    demo_issues = [
        QAIssue(
            title="Enter key in farm name field provides no feedback",
            description="When user presses Enter in the farm name input field, no visual feedback is provided to indicate the action was processed.",
            severity="High",
            issue_type="Bug",
            component="Form Validation",
            user_story_id="US003",
            test_step="Step 4: press_key K_RETURN",
            reproduction_steps=[
                "Navigate to Farm Setup page",
                "Click in farm name input field",
                "Type a farm name",
                "Press Enter key",
                "Observe no visual feedback or field state change"
            ]
        ),
        QAIssue(
            title="Menu click detection not working for navigation",
            description="Main menu items cannot be clicked to navigate to other pages. Click detection appears broken.",
            severity="High", 
            issue_type="Bug",
            component="Navigation",
            user_story_id="US001",
            test_step="Step 3: click New Game",
            reproduction_steps=[
                "Load main menu",
                "Attempt to click 'New Game' menu item",
                "Observe navigation does not occur",
                "Error: Could not find menu item"
            ]
        )
    ]
    
    # Create issues
    for issue in demo_issues:
        issue_id = tracker.create_issue(issue)
        
    # Show created issues
    if os.path.exists("qa_issues.json"):
        with open("qa_issues.json", 'r') as f:
            issues = json.load(f)
        
        print(f"\n📊 Created {len(issues)} issues:")
        for issue in issues:
            print(f"  {issue['id']}: {issue['title']}")
    
    print(f"\n💡 To use with real trackers:")
    print(f"  1. Edit config files with your credentials")
    print(f"  2. Change tracker_type in config")
    print(f"  3. Run: python3 issue_tracker_integration.py")

if __name__ == "__main__":
    main()