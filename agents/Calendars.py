from todoist_api_python.api import TodoistAPI, Task
from gcsa.google_calendar import GoogleCalendar
from gcsa.event import Event
from datetime import datetime, timedelta, date, timezone
import keyring
import sys
import webcolors
import platform
import dateutil
import pickle
import time
from globals import user_email, todoist_api_key

class CalendarEvent:
    def __init__(self, item, calendars, calendar_id):
        self._item = item
        self._calendars = calendars
        self._calendar_id = calendar_id

        if platform.system() in ('Linux'):
            self._start_format = "%-I:%M%p"
        else:
            self._start_format = "%#I:%M%p"
        self._start_format = f"{self._start_format} on %A, %B %d, %Y"
    
class GoogleEvent(CalendarEvent):
    def __init__(self, event, calendars, calendar_id):
        super().__init__(event, calendars, calendar_id)

    @property
    def isGoogleEvent(self):
        return True
    
    @property
    def isTodoistEvent(self):
        return False
    
    @property
    def reminders(self):
        if self._item.default_reminders:
            return "10 minutes before"
        elif len(self._item.reminders) > 0:
            return self._item.reminders[0]
        else:
            return "No reminders set"
        
    @property
    def is_recurring(self):
        return self._item.recurring_event_id
    
    @property
    def name(self):
        return self._item.summary
    
    @property
    def start_pretty(self):
        return self._item.start.strftime(self._start_format)
    
    @property
    def start_date(self):
        return self._item.start
    
    @property
    def start_datetime(self):
        return self._item.start
    
    @property
    def end(self):
        return self._item.end
    
    @property
    def colors(self):
        return self._calendars.google_colors[self._calendar_id].values()
    
    @property
    def organizer(self):
        return self._item.organizer.display_name
    
    @property
    def visibility(self):
        return self._item.visibility
    
    @property
    def description(self):
        return self._item.description


class TodoistEvent(CalendarEvent):
    def __init__(self, item, calendars, project_id):
        super().__init__(item, calendars, project_id)
        self._project_id = project_id

    @property
    def isGoogleEvent(self):
        return False
    
    @property
    def isTodoistEvent(self):
        return True
    
    @property
    def reminders(self):
        return "No reminders set"
    
    @property
    def is_recurring(self):
        return self._item.due.is_recurring

    @property
    def recurrence(self):
        return self._item.due.string
    
    @property
    def name(self):
        return self._item.content
    
    @property
    def start_pretty(self):
        if self._item.due.datetime:
            return dateutil.parser.parse(self._item.due.datetime).strftime(self._start_format)
        else:
            # Convert date to datetime
            return dateutil.parser.parse(self._item.due.date).strftime(self._start_format)
    
    @property
    def start_date(self):
        if self._item.due.datetime:
            return dateutil.parser.parse(self._item.due.datetime).date()
        else:
            # Convert date to datetime
            return dateutil.parser.parse(self._item.due.date).date()
        
    @property
    def start_datetime(self):
        if self._item.due.datetime:
            return dateutil.parser.parse(self._item.due.datetime)
        else:
            # Convert date to datetime
            return dateutil.parser.parse(self._item.due.date)
    
    @property
    def end(self):
        return self._item.due.date
    
    @property
    def colors(self):
        return self._calendars.todoist_colors[self._project_id], [0, 0, 0]
    
    @property
    def organizer(self):
        if self._item.creator_id in self._calendars.todoist_collaborators[self._project_id]:
            return self._calendars.todoist_collaborators[self._project_id][self._item.creator_id].name
        else:
            return self._item.creator_id
    
    @property
    def visibility(self):
        return "N/A"
    
    @property
    def description(self):
        return self._item.description

    #def moveDateTime(self, new_date):
    #    self._calendars.todoist_api.update_task(self._item.id, due_date=str(new_date))

    def updateEvent(self, name=None, due_date=None, due_time=None, priority=None, description=None, recurrence=None):
        if name and name != self._item.content:
            self._calendars.todoist_api.update_task(self._item.id, content=name)

        new_due = None
        if due_date or due_time:
            if due_date and due_time:
                new_due = datetime.strptime(f"{due_date} {due_time}", "%Y-%m-%d %H:%M")
            elif due_date:
                new_due = datetime.combine(datetime.strptime(due_date, "%Y-%m-%d"), self.start_datetime.time())
            elif due_time:
                new_due = datetime.combine(self.start_date, datetime.strptime(due_time, "%H:%M").time())
            
            if recurrence:
                self._calendars.todoist_api.update_task(self._item.id, due_datetime=new_due.isoformat(), due_string=recurrence)
            else:
                self._calendars.todoist_api.update_task(self._item.id, due_datetime=new_due.isoformat(), due_string=self._item.due.string)
        if priority and self._item.priority != priority:
            self._calendars.todoist_api.update_task(self._item.id, priority=priority)
        if description and self._item.description != description:
            self._calendars.todoist_api.update_task(self._item.id, description=description)
        #if recurrence and self._item.due.string != recurrence:
        #    self._calendars.todoist_api.update_task(self._item.id, due_string=recurrence)

    def deleteEvent(self):
        self._calendars.todoist_api.delete_task(self._item.id)

    def completeEvent(self):
        self._calendars.todoist_api.close_task(self._item.id)

    def addEvent(self, name=None, due_date=None, due_time=None, priority=None, description=None, recurrence=None):
        new_due = None

        if recurrence:
            self._calendars.todoist_api.add_task(content=name, 
                                                priority=priority, 
                                                description=description, 
                                                due_string=recurrence)
        else:
            if due_date or due_time:
                if due_date and due_time:
                    new_due = datetime.strptime(f"{due_date} {due_time}", "%Y-%m-%d %H:%M")
                elif due_date:
                    new_due = datetime.combine(datetime.strptime(due_date, "%Y-%m-%d"), self.start_datetime.time())
                elif due_time:
                    new_due = datetime.combine(self.start_date, datetime.strptime(due_time, "%H:%M").time())
    
            self._calendars.todoist_api.add_task(content=name, 
                                                due_datetime=new_due, 
                                                priority=priority, 
                                                description=description, 
                                                due_string=recurrence)

class Calendars:
    google_enabled = False
    todoist_enabled = True
    color_overrides = {'mint_green': [0.596, 0.984, 0.596], 'charcoal': [0.85, 0.85, 0.85]}
    def __init__(self, screen_obj):
        self._displayDates = []
        self._enabledCalendars = ['aarondeno11@gmail.com', 'en.usa#holiday@group.v.calendar.google.com']
        #self._enabledProjects = ['Appointments (Outlook)', 'Inbox', 'Maintenance', 'Birthdays', "Soft ToDo's"]
        self._enabledProjects = ['Appointments (Outlook)', 'Maintenance', 'Birthdays']
        self._screen_obj = screen_obj

        # Load and save todoist collaborators to save on API calls using pickle
        try:
            with open('todoist_collaborators.pickle', 'rb') as f:
                self.todoist_collaborators = pickle.load(f)
        except:
            self.todoist_collaborators = {}

        # Connect to Todoist
        if Calendars.todoist_enabled:
            try:
                self.todoist_api = TodoistAPI(todoist_api_key)
                temp_projs = self.todoist_api.get_projects()
                self.todoist_projects = {}
                #self.todoist_collaborators = {}
                for project in temp_projs:
                    self.todoist_projects[project.id] = project
                    if not project.id in self.todoist_collaborators:
                        self.todoist_collaborators[project.id] = {}
                        temp_collabs = self.todoist_api.get_collaborators(project.id)
                        for clist in temp_collabs:
                            self.todoist_collaborators[project.id][clist.id] = clist

                with open('todoist_collaborators.pickle', 'wb') as f:
                    pickle.dump(self.todoist_collaborators, f)

                self.todoist_colors = {}
                for project in temp_projs:
                    if project.color in Calendars.color_overrides:
                        self.todoist_colors[project.id] = Calendars.color_overrides[project.color]
                    else:
                        try:
                            self.todoist_colors[project.id] = [ c/255. for c in webcolors.name_to_rgb(project.color) ]
                        except:
                            sub_color = project.color.replace('_', '')
                            self.todoist_colors[project.id] = [ c/255. for c in webcolors.name_to_rgb(sub_color) ]
            except Exception as error:
                print(f"Error logging into to Todoist:\n   {error}")
                sys.exit(-1)

        # Connect to Google Calendar
        if Calendars.google_enabled:
            try:
                self.gcal = GoogleCalendar(user_email)
            except Exception as error:
                print(f"Error logging into to Google Calendar:\n   {error}")
                sys.exit(-1)

        self.update()

    def update(self):
        if Calendars.todoist_enabled:
            print("Loading todoist tasks...")
            done = False
            while not done:
                try:
                    self.todoist_tasks = self.todoist_api.get_tasks()
                except Exception as error:
                    print(f"Error loading tasks from Todoist:\n   {error}")
                    print(f"Trying again in 10 seconds...")
                    time.sleep(10)
                    #sys.exit(-1)
                
                done = True
            print("Done")

        self._displayDates = []

        curr_weekday = self.today.weekday() + 1

        for i in range(curr_weekday):
            this_date = self.today - timedelta(days=curr_weekday - i)
            self._displayDates.append(this_date)

        self._displayDates.append(self.today)

        i = 0
        while(len(self._displayDates) < 35):
            i = i + 1
            self._displayDates.append(self.today + timedelta(i))
        
        def scale_color(hex_color, scale_factor):
            hex_color = hex_color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

            r = max(0, min(255, int(r * scale_factor)))
            g = max(0, min(255, int(g * scale_factor)))
            b = max(0, min(255, int(b * scale_factor)))

            return (r/255, g/255, b/255, 1)
            #return f"#{r:02x}{g:02x}{b:02x}"

        self.google_events = {}
        if Calendars.google_enabled:
            self.google_colors = {}
            for calendar_id in self._enabledCalendars:
                cid = self.gcal.get_calendar_list_entry(calendar_id).color_id
                color = self.gcal.list_calendar_colors()[cid]
                color['background'] = scale_color(color['background'], 0.7)
                color['foreground'] = scale_color(color['foreground'], 1.0)
                self.google_colors[calendar_id] = color
    
            #for project_id, project in self.todoist_projects.items():
            #    if project.name in self._enabledProjects:
            #        self.todoist_colors[project.id] = project.color

            done = False
            while not done: 
                try:
                    for calendar_id in self._enabledCalendars:
                        these_events = self.gcal.get_events(self._displayDates[0], self._displayDates[-1], single_events=True, calendar_id = calendar_id)
                        self.google_events[calendar_id] = list(these_events)
                except Exception as error:
                    print(f"Error loading Google Calendar:\n   {error}")
                    printf("Trying again in 10 seconds...")
                    time.sleep(10)
                    #sys.exit(-1)

                done = True

        self.todoist_events = {}
        if Calendars.todoist_enabled:
            print("Loading todoist details")
            done = False
            while not done:
                try:
                    for project_id in [ p for p in self.todoist_projects if self.todoist_projects[p].name in self._enabledProjects ]:
                        project = self.todoist_projects[project_id]
                        these_events = [ t for t in self.todoist_tasks if t.project_id == project_id ]
                        these_events = [ ev for ev in these_events if hasattr(ev.due, 'date') ]
                        these_events = [ ev for ev in these_events if date.fromisoformat(ev.due.date) >= self._displayDates[0] ]
                        these_events = [ ev for ev in these_events if date.fromisoformat(ev.due.date) <= self._displayDates[-1] ]
                        self.todoist_events[project_id] = these_events
                except Exception as error:
                    print(f"Error loading Todoist Calendar:\n   {error}")
                    print("Trying again in 10 seconds...")
                    time.sleep(10)
                    #sys.exit(-1)

                done = True
            print("Done")

        #print()
        #self.todoist_api.sync()
        #self.keep_service = self.get_keep_service()

    @property
    def now(self):
        return datetime.now()

    @property
    def today(self):
        return datetime.today().date()

    @property
    def month_pretty(self):
        return datetime.strftime(self.today, "%B %Y")

    @property
    def displayDays(self):
        return self._displayDates

    def events(self, this_date):
        to_return = {}
        if Calendars.google_enabled:
            for calendar_id in self._enabledCalendars:
                these_evs = [ e for e in self.google_events[calendar_id] if (type(e.start)==datetime and e.start.date() == this_date) or 
                                                                            (type(e.start)==type(this_date) and e.start == this_date) ]
                #to_return[calendar_id] = these_evs
                to_return[calendar_id] = [ GoogleEvent(e, self, calendar_id) for e in these_evs ]

        if Calendars.todoist_enabled:
            for project_name in self._enabledProjects:
                project = [ p for p in self.todoist_projects.values() if p.name == project_name ][0]
                these_evs = [ e for e in self.todoist_events[project.id] if (date.fromisoformat(e.due.date) == this_date)]
    
                #to_return[project_name] = these_evs
                to_return[project_name] = [ TodoistEvent(e, self, project.id) for e in these_evs ]

        return to_return
    
    def update_event(self, event, name):
        event.summary = name

        self.gcal.update_event(event)

    def addTodoistEvent(self, name=None, description=None, due_date=None, due_time=None, recurrence=None, priority=None):
        new_due = None

        if recurrence:
            resp = self.todoist_api.add_task(content=name, 
                                             #priority=priority, 
                                             description=description, 
                                             due_string=recurrence)
        
        else:
            if due_date or due_time:
                if due_date and due_time:
                    new_due = datetime.strptime(f"{due_date} {due_time}", "%Y-%m-%d %H:%M")
                elif due_date:
                    new_due = datetime.combine(datetime.strptime(due_date, "%Y-%m-%d"), self.start_datetime.time())
                elif due_time:
                    new_due = datetime.combine(self.start_date, datetime.strptime(due_time, "%H:%M").time())

            new_due = new_due.isoformat()

            resp = self.todoist_api.add_task(content=name, 
                                             due_datetime=new_due, 
                                             #priority=priority, 
                                             description=description, 
                                             due_string=recurrence)


    #def add_item(self, item, platform='todoist'):
    #    if platform == 'todoist':
    #        self.add_item_to_todoist(item)
    #    elif platform == 'keep':
    #        self.add_item_to_keep(item)

    #def add_item_to_todoist(self, item):
    #    self.todoist_api.items.add(item, project_id=your_project_id)
    #    self.todoist_api.commit()

    #def add_item_to_keep(self, item):
    #    # Code to add item to Google Keep list
    #    pass 

    #def get_list(self, platform='todoist'):
    #    if platform == 'todoist':
    #        return self.get_list_from_todoist()
    #    elif platform == 'keep':
    #        return self.get_list_from_keep()

    #def get_list_from_todoist(self):
    #    # Code to retrieve list from Todoist
    #    pass 

    #def get_list_from_keep(self):
    #    # Code to retrieve list from Google Keep
    #    pass 