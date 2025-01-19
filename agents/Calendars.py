from todoist_api_python.api import TodoistAPI
from gcsa.google_calendar import GoogleCalendar
from datetime import datetime, timedelta, date
import keyring
import sys
import webcolors
from globals import user_email, todoist_api_key

class Calendars:
    color_overrides = {'mint_green': [0.596, 0.984, 0.596], 'charcoal': [0.85, 0.85, 0.85]}
    def __init__(self):
        self._displayDates = []
        self._enabledCalendars = ['aarondeno11@gmail.com', 'en.usa#holiday@group.v.calendar.google.com']
        self._enabledProjects = ['Appointments (Outlook)', 'Inbox', 'Maintenance', 'Birthdays', "Soft ToDo's"]

        # Connect to Todoist
        try:
            self.todoist_api = TodoistAPI(todoist_api_key)
        except Exception as error:
            print(f"Error logging into to Todoist:\n   {error}")
            sys.exit(-1)

        # Connect to Google Calendar
        try:
            self.gcal = GoogleCalendar(user_email)
        except Exception as error:
            print(f"Error logging into to Google Calendar:\n   {error}")
            sys.exit(-1)

        self.update()

    def update(self):
        try:
            temp_projs = self.todoist_api.get_projects()
            self.todoist_projects = {}
            for project in temp_projs:
                self.todoist_projects[project.id] = project
            self.todoist_tasks = self.todoist_api.get_tasks()
        except Exception as error:
            print(f"Error loading tasks from Todoist:\n   {error}")
            sys.exit(-1)

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

        self.google_events = {}
        try:
            for calendar_id in self._enabledCalendars:
                these_events = self.gcal.get_events(self._displayDates[0], self._displayDates[-1], single_events=True, calendar_id = calendar_id)
                self.google_events[calendar_id] = list(these_events)
        except Exception as error:
            print(f"Error loading Google Calendar:\n   {error}")
            sys.exit(-1)

        self.todoist_events = {}
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
            sys.exit(-1)

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
        for calendar_id in self._enabledCalendars:
            these_evs = [ e for e in self.google_events[calendar_id] if (type(e.start)==datetime and e.start.date() == this_date) or 
                                                                        (type(e.start)==type(this_date) and e.start == this_date) ]
            to_return[calendar_id] = these_evs

        for project_name in self._enabledProjects:
            project = [ p for p in self.todoist_projects.values() if p.name == project_name ][0]
            these_evs = [ e for e in self.todoist_events[project.id] if (date.fromisoformat(e.due.date) == this_date)]

            to_return[project_name] = these_evs

        return to_return
    
    def update_event(self, event, name):
        event.summary = name

        self.gcal.update_event(event)

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