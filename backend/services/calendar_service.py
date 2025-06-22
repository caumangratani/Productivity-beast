from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta
import json
from typing import List, Dict, Optional
import asyncio
import os

class CalendarService:
    def __init__(self, credentials: Credentials):
        self.service = build('calendar', 'v3', credentials=credentials)
    
    async def create_event(self, event_data: dict):
        """Create calendar event with auto-scheduling optimization"""
        event = {
            'summary': event_data['title'],
            'description': event_data.get('description', ''),
            'start': {
                'dateTime': event_data['start_time'],
                'timeZone': event_data.get('timeZone', 'UTC'),
            },
            'end': {
                'dateTime': event_data['end_time'],
                'timeZone': event_data.get('timeZone', 'UTC'),
            },
            'attendees': [{'email': email} for email in event_data.get('attendees', [])],
            'conferenceData': {
                'createRequest': {
                    'requestId': f"meet-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            } if event_data.get('create_meet_link') else None
        }
        
        return self.service.events().insert(
            calendarId='primary',
            body=event,
            conferenceDataVersion=1 if event_data.get('create_meet_link') else None
        ).execute()
    
    async def get_events(self, start_date: datetime, end_date: datetime):
        """Get calendar events in date range"""
        events_result = self.service.events().list(
            calendarId='primary',
            timeMin=start_date.isoformat() + 'Z',
            timeMax=end_date.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        return events_result.get('items', [])
    
    async def find_optimal_time_slot(self, duration_minutes: int, priority_level: str = "medium"):
        """
        Auto-scheduler: Find optimal time slot based on Eisenhower Matrix priority
        """
        now = datetime.utcnow()
        search_days = 14 if priority_level in ["urgent", "high"] else 7
        end_search = now + timedelta(days=search_days)
        
        # Get existing events
        existing_events = await self.get_events(now, end_search)
        
        # Define optimal time blocks based on priority
        optimal_blocks = self._get_optimal_time_blocks(priority_level)
        
        # Find free slots
        for day_offset in range(search_days):
            current_day = now + timedelta(days=day_offset)
            
            for time_block in optimal_blocks:
                start_time = current_day.replace(
                    hour=time_block['start_hour'], 
                    minute=0, 
                    second=0, 
                    microsecond=0
                )
                end_time = start_time + timedelta(minutes=duration_minutes)
                
                # Skip weekends for work tasks (unless urgent)
                if start_time.weekday() >= 5 and priority_level not in ["urgent"]:
                    continue
                
                # Check if slot is free
                is_free = await self._is_time_slot_free(start_time, end_time, existing_events)
                
                if is_free:
                    return {
                        'start_time': start_time.isoformat(),
                        'end_time': end_time.isoformat(),
                        'available': True,
                        'priority_block': time_block['name'],
                        'optimization_score': time_block['score']
                    }
        
        return {'available': False, 'message': 'No optimal slots found in the search period'}
    
    def _get_optimal_time_blocks(self, priority_level: str) -> List[Dict]:
        """Get optimal time blocks based on productivity research and priority"""
        blocks = {
            "urgent": [  # Immediate scheduling - any available time
                {"name": "Peak Focus (9-11 AM)", "start_hour": 9, "score": 10},
                {"name": "Post-Lunch Energy (2-4 PM)", "start_hour": 14, "score": 8},
                {"name": "Morning Start (8-9 AM)", "start_hour": 8, "score": 7},
                {"name": "Late Morning (11 AM-12 PM)", "start_hour": 11, "score": 6},
                {"name": "Afternoon (4-5 PM)", "start_hour": 16, "score": 5}
            ],
            "high": [  # Important tasks - prime focus times
                {"name": "Peak Focus (9-11 AM)", "start_hour": 9, "score": 10},
                {"name": "Morning Deep Work (8-9 AM)", "start_hour": 8, "score": 9},
                {"name": "Post-Lunch Energy (2-3 PM)", "start_hour": 14, "score": 8}
            ],
            "medium": [  # Regular tasks - good productive times
                {"name": "Late Morning (11 AM-12 PM)", "start_hour": 11, "score": 7},
                {"name": "Early Afternoon (1-2 PM)", "start_hour": 13, "score": 6},
                {"name": "Mid Afternoon (3-4 PM)", "start_hour": 15, "score": 6}
            ],
            "low": [  # Less important - any reasonable time
                {"name": "End of Day Wrap-up (4-5 PM)", "start_hour": 16, "score": 4},
                {"name": "Late Afternoon (5-6 PM)", "start_hour": 17, "score": 3}
            ]
        }
        return blocks.get(priority_level, blocks["medium"])
    
    async def _is_time_slot_free(self, start_time: datetime, end_time: datetime, existing_events: List) -> bool:
        """Check if a time slot is free"""
        for event in existing_events:
            if 'start' not in event or 'end' not in event:
                continue
                
            event_start_str = event['start'].get('dateTime') or event['start'].get('date')
            event_end_str = event['end'].get('dateTime') or event['end'].get('date')
            
            if not event_start_str or not event_end_str:
                continue
            
            try:
                # Handle both datetime and date formats
                if 'T' in event_start_str:
                    event_start = datetime.fromisoformat(event_start_str.replace('Z', '+00:00'))
                    event_end = datetime.fromisoformat(event_end_str.replace('Z', '+00:00'))
                else:
                    # All-day events
                    continue
                
                # Remove timezone info for comparison
                if event_start.tzinfo:
                    event_start = event_start.replace(tzinfo=None)
                if event_end.tzinfo:
                    event_end = event_end.replace(tzinfo=None)
                
                # Check for overlap
                if (start_time < event_end and end_time > event_start):
                    return False
            except Exception:
                continue
        
        return True
    
    async def extract_meeting_intelligence(self, event_id: str):
        """
        Extract meeting intelligence for Meeting Intelligence feature
        """
        try:
            event = self.service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            meeting_data = {
                'event_id': event_id,
                'title': event.get('summary', ''),
                'start_time': event['start'].get('dateTime', ''),
                'end_time': event['end'].get('dateTime', ''),
                'duration_minutes': self._calculate_duration(
                    event['start'].get('dateTime', ''),
                    event['end'].get('dateTime', '')
                ),
                'attendees': [
                    {
                        'email': attendee.get('email', ''),
                        'name': attendee.get('displayName', ''),
                        'response_status': attendee.get('responseStatus', 'needsAction')
                    } 
                    for attendee in event.get('attendees', [])
                ],
                'location': event.get('location', ''),
                'description': event.get('description', ''),
                'meet_link': self._extract_meet_link(event),
                'organizer': {
                    'email': event.get('organizer', {}).get('email', ''),
                    'name': event.get('organizer', {}).get('displayName', '')
                },
                'meeting_type': self._classify_meeting_type(event),
                'preparation_needed': self._assess_preparation_needed(event)
            }
            
            return meeting_data
            
        except Exception as e:
            raise Exception(f"Failed to extract meeting intelligence: {str(e)}")
    
    def _calculate_duration(self, start_time: str, end_time: str) -> int:
        """Calculate meeting duration in minutes"""
        try:
            start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            duration = end - start
            return int(duration.total_seconds() / 60)
        except:
            return 0
    
    def _extract_meet_link(self, event: dict) -> Optional[str]:
        """Extract Google Meet link from event"""
        # Check conference data
        conference_data = event.get('conferenceData', {})
        entry_points = conference_data.get('entryPoints', [])
        
        for entry_point in entry_points:
            if entry_point.get('entryPointType') == 'video':
                return entry_point.get('uri')
        
        # Check description for meet links
        description = event.get('description', '')
        if 'meet.google.com' in description:
            import re
            meet_links = re.findall(r'https://meet\.google\.com/[a-z0-9\-]+', description)
            if meet_links:
                return meet_links[0]
        
        return None
    
    def _classify_meeting_type(self, event: dict) -> str:
        """Classify meeting type based on title and attendees"""
        title = event.get('summary', '').lower()
        attendee_count = len(event.get('attendees', []))
        
        # One-on-one
        if attendee_count <= 2:
            return '1:1'
        
        # Team meetings
        if any(keyword in title for keyword in ['standup', 'daily', 'scrum', 'team']):
            return 'team_standup'
        
        # Review meetings
        if any(keyword in title for keyword in ['review', 'retrospective', 'demo']):
            return 'review'
        
        # Planning meetings
        if any(keyword in title for keyword in ['planning', 'brainstorm', 'strategy']):
            return 'planning'
        
        # Large meetings
        if attendee_count > 10:
            return 'large_group'
        
        return 'general'
    
    def _assess_preparation_needed(self, event: dict) -> Dict:
        """Assess what preparation might be needed for the meeting"""
        title = event.get('summary', '').lower()
        description = event.get('description', '').lower()
        
        preparation = {
            'agenda_needed': False,
            'materials_needed': False,
            'presentation_needed': False,
            'decision_making': False,
            'estimated_prep_time': 0
        }
        
        # Check for agenda needs
        if any(keyword in title for keyword in ['planning', 'strategy', 'brainstorm']):
            preparation['agenda_needed'] = True
            preparation['estimated_prep_time'] += 15
        
        # Check for materials
        if any(keyword in description for keyword in ['document', 'report', 'data', 'analysis']):
            preparation['materials_needed'] = True
            preparation['estimated_prep_time'] += 30
        
        # Check for presentation
        if any(keyword in title for keyword in ['demo', 'presentation', 'pitch', 'showcase']):
            preparation['presentation_needed'] = True
            preparation['estimated_prep_time'] += 45
        
        # Check for decision making
        if any(keyword in title for keyword in ['decision', 'approval', 'sign-off', 'review']):
            preparation['decision_making'] = True
            preparation['estimated_prep_time'] += 20
        
        return preparation
    
    async def create_task_deadline_events(self, tasks: List[Dict]):
        """
        Sync task deadlines with Google Calendar
        Part of the Task & Project Manager integration
        """
        created_events = []
        
        for task in tasks:
            if not task.get('due_date'):
                continue
            
            try:
                # Create event for task deadline
                due_date = datetime.fromisoformat(task['due_date'].replace('Z', ''))
                
                # Create a 30-minute deadline reminder
                reminder_start = due_date - timedelta(minutes=30)
                
                event_data = {
                    'title': f"⏰ Task Deadline: {task['title']}",
                    'description': f"Task: {task['title']}\nDescription: {task.get('description', '')}\nPriority: {task.get('priority', 'medium')}\nEisenhower Quadrant: {task.get('eisenhower_quadrant', 'decide')}",
                    'start_time': reminder_start.isoformat(),
                    'end_time': due_date.isoformat(),
                    'attendees': []
                }
                
                event = await self.create_event(event_data)
                created_events.append({
                    'task_id': task['id'],
                    'event_id': event['id'],
                    'event_link': event.get('htmlLink')
                })
                
            except Exception as e:
                print(f"Error creating deadline event for task {task.get('id')}: {str(e)}")
                continue
        
        return created_events
    
    async def suggest_eisenhower_scheduling(self, tasks: List[Dict]):
        """
        Suggest optimal scheduling based on Eisenhower Matrix
        Advanced Auto-Scheduler feature
        """
        suggestions = []
        
        # Group tasks by Eisenhower quadrant
        quadrants = {
            'do': [],      # Urgent & Important
            'decide': [],  # Important & Not Urgent  
            'delegate': [],# Urgent & Not Important
            'delete': []   # Neither Urgent nor Important
        }
        
        for task in tasks:
            quadrant = task.get('eisenhower_quadrant', 'decide')
            quadrants[quadrant].append(task)
        
        # Schedule DO quadrant tasks immediately (within 24 hours)
        for task in quadrants['do']:
            estimated_duration = task.get('estimated_duration', 60)
            optimal_slot = await self.find_optimal_time_slot(estimated_duration, "urgent")
            
            if optimal_slot['available']:
                suggestions.append({
                    'task_id': task['id'],
                    'task_title': task['title'],
                    'quadrant': 'do',
                    'suggested_time': optimal_slot['start_time'],
                    'duration': estimated_duration,
                    'priority_block': optimal_slot.get('priority_block'),
                    'reasoning': 'Urgent & Important - Schedule immediately',
                    'action': 'schedule_now'
                })
        
        # Schedule DECIDE quadrant tasks in optimal focus times
        for task in quadrants['decide']:
            estimated_duration = task.get('estimated_duration', 90)
            optimal_slot = await self.find_optimal_time_slot(estimated_duration, "high")
            
            if optimal_slot['available']:
                suggestions.append({
                    'task_id': task['id'],
                    'task_title': task['title'],
                    'quadrant': 'decide',
                    'suggested_time': optimal_slot['start_time'],
                    'duration': estimated_duration,
                    'priority_block': optimal_slot.get('priority_block'),
                    'reasoning': 'Important but not urgent - Schedule in peak focus time',
                    'action': 'schedule_focused'
                })
        
        # Suggest delegation for DELEGATE quadrant
        for task in quadrants['delegate']:
            suggestions.append({
                'task_id': task['id'],
                'task_title': task['title'],
                'quadrant': 'delegate',
                'suggested_time': None,
                'duration': 0,
                'reasoning': 'Urgent but not important - Consider delegating',
                'action': 'delegate',
                'delegation_suggestions': [
                    'Assign to team member with available capacity',
                    'Automate if possible',
                    'Simplify the requirements'
                ]
            })
        
        # Suggest deletion/deferral for DELETE quadrant
        for task in quadrants['delete']:
            suggestions.append({
                'task_id': task['id'],
                'task_title': task['title'],
                'quadrant': 'delete',
                'suggested_time': None,
                'duration': 0,
                'reasoning': 'Neither urgent nor important - Consider eliminating',
                'action': 'eliminate',
                'elimination_options': [
                    'Delete if not necessary',
                    'Defer to later date',
                    'Batch with similar low-priority tasks'
                ]
            })
        
        return {
            'suggestions': suggestions,
            'summary': {
                'do_tasks': len(quadrants['do']),
                'decide_tasks': len(quadrants['decide']),
                'delegate_tasks': len(quadrants['delegate']),
                'delete_tasks': len(quadrants['delete']),
                'total_scheduled': len([s for s in suggestions if s['action'] in ['schedule_now', 'schedule_focused']])
            }
        }