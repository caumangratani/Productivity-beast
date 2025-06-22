from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

class SheetsService:
    def __init__(self, credentials: Credentials):
        self.service = build('sheets', 'v4', credentials=credentials)
    
    async def create_spreadsheet(self, title: str):
        """Create new spreadsheet"""
        spreadsheet = {
            'properties': {
                'title': title
            },
            'sheets': [
                {'properties': {'title': 'Tasks'}},
                {'properties': {'title': 'Projects'}},
                {'properties': {'title': 'Performance Report'}},
                {'properties': {'title': 'Team Analytics'}},
                {'properties': {'title': 'Eisenhower Matrix'}}
            ]
        }
        
        result = self.service.spreadsheets().create(
            body=spreadsheet
        ).execute()
        
        spreadsheet_id = result['spreadsheetId']
        
        # Setup initial headers for each sheet
        await self._setup_sheet_headers(spreadsheet_id)
        
        return spreadsheet_id
    
    async def _setup_sheet_headers(self, spreadsheet_id: str):
        """Setup headers for all sheets"""
        batch_data = [
            # Tasks sheet headers
            {
                'range': 'Tasks!A1:J1',
                'values': [['Task ID', 'Title', 'Description', 'Due Date', 'Priority', 'Status', 'Eisenhower Quadrant', 'Assigned To', 'Created At', 'Completed At']]
            },
            # Projects sheet headers
            {
                'range': 'Projects!A1:H1',
                'values': [['Project ID', 'Name', 'Description', 'Owner', 'Team Members', 'Status', 'Created At', 'Due Date']]
            },
            # Performance Report headers
            {
                'range': 'Performance Report!A1:G1',
                'values': [['Date', 'User', 'Tasks Completed', 'Completion Rate', 'Performance Score', 'Focus Time', 'Productivity Notes']]
            },
            # Team Analytics headers
            {
                'range': 'Team Analytics!A1:F1',
                'values': [['Team Member', 'Role', 'Tasks Assigned', 'Tasks Completed', 'Performance Score', 'Last Activity']]
            },
            # Eisenhower Matrix headers
            {
                'range': 'Eisenhower Matrix!A1:E1',
                'values': [['Task', 'Urgent', 'Important', 'Quadrant', 'Recommended Action']]
            }
        ]
        
        body = {
            'valueInputOption': 'RAW',
            'data': batch_data
        }
        
        return self.service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=body
        ).execute()
    
    async def batch_export_tasks(self, spreadsheet_id: str, tasks_data: List[Dict]):
        """Export tasks to Google Sheets with Eisenhower Matrix analysis"""
        
        # Prepare task data
        task_rows = []
        eisenhower_rows = []
        
        for task in tasks_data:
            # Tasks sheet row
            task_rows.append([
                task.get('id', ''),
                task.get('title', ''),
                task.get('description', ''),
                task.get('due_date', ''),
                task.get('priority', ''),
                task.get('status', ''),
                task.get('eisenhower_quadrant', ''),
                task.get('assigned_to', ''),
                task.get('created_at', ''),
                task.get('completed_at', '')
            ])
            
            # Eisenhower Matrix analysis
            quadrant = task.get('eisenhower_quadrant', 'decide')
            urgent = 'Yes' if quadrant in ['do', 'delegate'] else 'No'
            important = 'Yes' if quadrant in ['do', 'decide'] else 'No'
            
            action_mapping = {
                'do': 'Schedule immediately - Peak focus time',
                'decide': 'Schedule in advance - Deep work blocks',
                'delegate': 'Assign to team member or automate',
                'delete': 'Consider eliminating or deferring'
            }
            
            eisenhower_rows.append([
                task.get('title', ''),
                urgent,
                important,
                quadrant.title(),
                action_mapping.get(quadrant, 'Review priority')
            ])
        
        # Clear existing data and add new data
        batch_data = [
            {
                'range': f'Tasks!A2:J{len(task_rows)+1}',
                'values': task_rows
            },
            {
                'range': f'Eisenhower Matrix!A2:E{len(eisenhower_rows)+1}',
                'values': eisenhower_rows
            }
        ]
        
        # Clear old data first
        clear_batch = [
            {'range': 'Tasks!A2:J1000'},
            {'range': 'Eisenhower Matrix!A2:E1000'}
        ]
        
        clear_body = {'ranges': [item['range'] for item in clear_batch]}
        self.service.spreadsheets().values().batchClear(
            spreadsheetId=spreadsheet_id,
            body=clear_body
        ).execute()
        
        # Add new data
        body = {
            'valueInputOption': 'RAW',
            'data': batch_data
        }
        
        return self.service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=body
        ).execute()
    
    async def export_projects(self, spreadsheet_id: str, projects_data: List[Dict]):
        """Export projects to Google Sheets"""
        
        project_rows = []
        for project in projects_data:
            team_members = ', '.join(project.get('team_members', []))
            project_rows.append([
                project.get('id', ''),
                project.get('name', ''),
                project.get('description', ''),
                project.get('owner_id', ''),
                team_members,
                project.get('status', ''),
                project.get('created_at', ''),
                project.get('due_date', '')
            ])
        
        # Clear existing data
        self.service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range='Projects!A2:H1000'
        ).execute()
        
        # Add new data
        body = {
            'values': project_rows
        }
        
        return self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f'Projects!A2:H{len(project_rows)+1}',
            valueInputOption='RAW',
            body=body
        ).execute()
    
    async def create_productivity_report(self, spreadsheet_id: str, report_data: Dict):
        """Create automated daily/weekly productivity reports"""
        
        # Performance Report sheet
        report_rows = [
            ['📊 PRODUCTIVITY DASHBOARD', f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"],
            [''],
            ['🎯 KEY METRICS', ''],
            ['Total Tasks Completed', report_data.get('completed_tasks', 0)],
            ['Total Tasks Assigned', report_data.get('total_tasks', 0)],
            ['Completion Rate', f"{report_data.get('completion_rate', 0):.1f}%"],
            ['Performance Score', f"{report_data.get('performance_score', 0):.1f}/10"],
            [''],
            ['⏰ TIME ANALYSIS', ''],
            ['Total Focus Time', f"{report_data.get('focus_time_hours', 0):.1f} hours"],
            ['Average Task Duration', f"{report_data.get('avg_task_duration', 0):.1f} hours"],
            ['Most Productive Hour', report_data.get('peak_hour', 'N/A')],
            [''],
            ['🎭 EISENHOWER MATRIX BREAKDOWN', ''],
            ['Do First (Urgent & Important)', report_data.get('do_tasks', 0)],
            ['Schedule (Important, Not Urgent)', report_data.get('decide_tasks', 0)],
            ['Delegate (Urgent, Not Important)', report_data.get('delegate_tasks', 0)],
            ['Eliminate (Neither Urgent nor Important)', report_data.get('delete_tasks', 0)],
            [''],
            ['📈 TRENDS & INSIGHTS', ''],
            ['Week-over-Week Change', f"{report_data.get('weekly_change', 0):+.1f}%"],
            ['Productivity Trend', report_data.get('trend', 'Stable')],
            ['Top Achievement', report_data.get('top_achievement', 'Great progress!')],
            [''],
            ['🎯 RECOMMENDATIONS', ''],
            ['Primary Focus Area', report_data.get('focus_area', 'Continue current approach')],
            ['Optimization Tip', report_data.get('optimization_tip', 'Maintain consistency')],
            ['Next Week Goal', report_data.get('next_week_goal', 'Set weekly targets')]
        ]
        
        # Clear existing report
        self.service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range='Performance Report!A1:G1000'
        ).execute()
        
        # Add report data
        body = {
            'values': report_rows
        }
        
        return self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Performance Report!A1',
            valueInputOption='RAW',
            body=body
        ).execute()
    
    async def export_team_analytics(self, spreadsheet_id: str, team_data: List[Dict]):
        """Export team performance analytics"""
        
        team_rows = []
        for member in team_data:
            team_rows.append([
                member.get('name', ''),
                member.get('role', ''),
                member.get('tasks_assigned', 0),
                member.get('tasks_completed', 0),
                f"{member.get('performance_score', 0):.1f}",
                member.get('last_activity', '')
            ])
        
        # Clear existing data
        self.service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range='Team Analytics!A2:F1000'
        ).execute()
        
        # Add team data
        body = {
            'values': team_rows
        }
        
        return self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f'Team Analytics!A2:F{len(team_rows)+1}',
            valueInputOption='RAW',
            body=body
        ).execute()
    
    async def import_tasks_from_sheet(self, spreadsheet_id: str, range_name: str = 'Tasks!A2:J'):
        """Import tasks from existing Google Sheets"""
        result = self.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        tasks = []
        
        for row in values:
            if len(row) >= 6:  # Ensure minimum required columns
                task = {
                    'id': row[0] if len(row) > 0 else '',
                    'title': row[1] if len(row) > 1 else '',
                    'description': row[2] if len(row) > 2 else '',
                    'due_date': row[3] if len(row) > 3 else '',
                    'priority': row[4] if len(row) > 4 else '',
                    'status': row[5] if len(row) > 5 else '',
                    'eisenhower_quadrant': row[6] if len(row) > 6 else '',
                    'assigned_to': row[7] if len(row) > 7 else '',
                    'created_at': row[8] if len(row) > 8 else '',
                    'completed_at': row[9] if len(row) > 9 else ''
                }
                tasks.append(task)
        
        return tasks
    
    async def create_eisenhower_dashboard(self, spreadsheet_id: str, tasks_data: List[Dict]):
        """Create visual Eisenhower Matrix dashboard"""
        
        # Count tasks by quadrant
        quadrant_counts = {'do': 0, 'decide': 0, 'delegate': 0, 'delete': 0}
        quadrant_tasks = {'do': [], 'decide': [], 'delegate': [], 'delete': []}
        
        for task in tasks_data:
            quadrant = task.get('eisenhower_quadrant', 'decide')
            quadrant_counts[quadrant] += 1
            quadrant_tasks[quadrant].append(task.get('title', 'Untitled'))
        
        # Create dashboard layout
        dashboard_rows = [
            ['🎯 EISENHOWER MATRIX DASHBOARD', '', '', ''],
            ['', '', '', ''],
            ['URGENT', '', 'NOT URGENT', ''],
            ['', '', '', ''],
            ['🔥 DO FIRST', f"({quadrant_counts['do']} tasks)", '📅 SCHEDULE', f"({quadrant_counts['decide']} tasks)"],
            ['IMPORTANT', '', 'IMPORTANT', ''],
            [''],
            ['Top tasks:', '', 'Top tasks:', ''],
        ]
        
        # Add top tasks for each quadrant
        max_tasks_show = 5
        for i in range(max_tasks_show):
            do_task = quadrant_tasks['do'][i] if i < len(quadrant_tasks['do']) else ''
            decide_task = quadrant_tasks['decide'][i] if i < len(quadrant_tasks['decide']) else ''
            dashboard_rows.append([f"• {do_task}", '', f"• {decide_task}", ''])
        
        dashboard_rows.extend([
            ['', '', '', ''],
            ['🤝 DELEGATE', f"({quadrant_counts['delegate']} tasks)", '🗑️ ELIMINATE', f"({quadrant_counts['delete']} tasks)"],
            ['NOT IMPORTANT', '', 'NOT IMPORTANT', ''],
            [''],
            ['Top tasks:', '', 'Top tasks:', ''],
        ])
        
        # Add delegate and delete tasks
        for i in range(max_tasks_show):
            delegate_task = quadrant_tasks['delegate'][i] if i < len(quadrant_tasks['delegate']) else ''
            delete_task = quadrant_tasks['delete'][i] if i < len(quadrant_tasks['delete']) else ''
            dashboard_rows.append([f"• {delegate_task}", '', f"• {delete_task}", ''])
        
        # Add summary and recommendations
        dashboard_rows.extend([
            ['', '', '', ''],
            ['📊 PRODUCTIVITY INSIGHTS', '', '', ''],
            ['Total Tasks', len(tasks_data), '', ''],
            ['Urgent Tasks', quadrant_counts['do'] + quadrant_counts['delegate'], '', ''],
            ['Important Tasks', quadrant_counts['do'] + quadrant_counts['decide'], '', ''],
            ['', '', '', ''],
            ['🎯 RECOMMENDATIONS', '', '', ''],
            ['• Focus on DO FIRST tasks immediately', '', '', ''],
            ['• Schedule DECIDE tasks in your calendar', '', '', ''],
            ['• Find ways to delegate or automate', '', '', ''],
            ['• Question if ELIMINATE tasks are necessary', '', '', '']
        ])
        
        # Clear and update the Eisenhower Matrix sheet
        self.service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range='Eisenhower Matrix!A1:D1000'
        ).execute()
        
        body = {
            'values': dashboard_rows
        }
        
        return self.service.spreadsheets().values().update(
            spreadsheet_id=spreadsheet_id,
            range='Eisenhower Matrix!A1',
            valueInputOption='RAW',
            body=body
        ).execute()
    
    async def schedule_automated_exports(self, user_id: str, schedule_type: str = 'daily'):
        """
        Schedule automated exports (daily/weekly reports)
        This would integrate with APScheduler or similar
        """
        schedule_config = {
            'user_id': user_id,
            'schedule_type': schedule_type,
            'last_export': datetime.utcnow().isoformat(),
            'next_export': (datetime.utcnow() + timedelta(days=1 if schedule_type == 'daily' else 7)).isoformat(),
            'export_types': ['tasks', 'projects', 'performance_report', 'team_analytics']
        }
        
        return schedule_config