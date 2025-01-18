# TODO: Split this into multiple files

# pip install todoist-api-python google-api-python-client google-auth-httplib2 google-auth-oauthlib
# ~/.credentials will need to be copied to wherever this is installed.

# If Google Calendar stops authenticating, go here:
#   https://google-calendar-simple-api.readthedocs.io/en/latest/getting_started.html#getting-started
# and download the .json file to ~/.credentials and delete token.pickle.

from todoist_api_python.api_async import TodoistAPIAsync
from todoist_api_python.api import TodoistAPI
import gkeepapi
import platform
import webcolors
from gcsa.google_calendar import GoogleCalendar
from gcsa.recurrence import Recurrence
from functools import partial
from kivy.core.window import Window
from kivy.factory import Factory
from kivymd.app import MDApp
from kivy.graphics import Color, Line, RoundedRectangle
from kivy.clock import Clock
from kivy.uix.layout import Layout
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogButtonContainer, MDDialogSupportingText, MDDialogContentContainer
from kivymd.uix.divider import MDDivider
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDListItem, MDListItemHeadlineText, MDListItemTrailingCheckbox, MDListItemSupportingText, MDListItemLeadingIcon
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem
from kivymd.uix.widget import MDWidget
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
#from kivy.app import App, ConfigParser
#from kivy.uix.button import Button
import sys
from datetime import datetime, timedelta, date
import pytz
import keyring

# Use keyring.set_password(service, email, password) to set the password
user_email = "aarondeno11@gmail.com"
google_oauth_key = keyring.get_password("google_oauth", user_email)
todoist_api_key = keyring.get_password("todoist_api", user_email)

if platform.system() in ('Linux'):
    start_format = "%-I:%M%p"
else:
    start_format = "%#I:%M%p"

def FindDialogRoot(instance):
    while(type(instance) != MDDialog):
        if hasattr(instance, 'parent'):
            instance = instance.parent
        else:
            raise Exception("Unable to find dialog in instance hierachy")
        
    return instance

def FindChildByID(instance, id):
    if(hasattr(instance, "children")):
        for child in instance.children:
            if hasattr(child, "id") and child.id == id:
                return child
            else:
                if hasattr(child, "children"):
                    returned = FindChildByID(child, id)
                    if returned:
                        return returned

    return None

class Lists:
    def __init__(self):
        try:
            self.keep = gkeepapi.Keep()
            self.keep.authenticate(user_email, google_oauth_key)
        except Exception as error:
            print(f"Error logging into to Google Keep:\n   {error}")
            sys.exit(-1)

        try:
            self.todoist_api = TodoistAPI(todoist_api_key)
        except Exception as error:
            print(f"Error logging into to Todoist:\n   {error}")
            sys.exit(-1)

    def update(self):
        try:
            self.todoist_tasks = self.todoist_api.get_tasks()
        except Exception as error:
            print(f"Error loading tasks from Todoist:\n   {error}")
            sys.exit(-1)

        try:
            self.keep_all = self.keep.all()
            self.keep_lists = [ node for node in self.keep_all if type(node) == gkeepapi.node.List ]
        except Exception as error:
            print(f"Error downloading data:\n   {error}")
            sys.exit(-1)

class Notes:
    def __init__(self):
        try:
            self.keep = gkeepapi.Keep()
            self.keep.authenticate(user_email, google_oauth_key)
        except Exception as error:
            print(f"Error logging into to Google Keep:\n   {error}")
            sys.exit(-1)

    def update(self):
        try:
            self.keep_all = self.keep.all()
            self.keep_notes = [ node for node in self.keep_all if type(node) == gkeepapi.node.Note]
        except Exception as error:
            print(f"Error downloading data:\n   {error}")
            sys.exit(-1)

class Calendars:
    color_overrides = {'mint_green': [0.596, 0.984, 0.596], 'charcoal': [0.85, 0.85, 0.85]}
    def __init__(self):
        self._displayDates = []
        self._enabledCalendars = ['aarondeno11@gmail.com', 'en.usa#holiday@group.v.calendar.google.com']
        self._enabledProjects = ['Appointments (Outlook)', 'Inbox', 'Maintenance', 'Birthdays', "Soft ToDo's"]

        try:
            self.todoist_api = TodoistAPI(todoist_api_key)
        except Exception as error:
            print(f"Error logging into to Todoist:\n   {error}")
            sys.exit(-1)

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

class HomeDisplayApp(MDApp):
    def on_start(self):
        #self.fps_monitor_start()
        super(HomeDisplayApp, self).on_start()

    def build(self):
        Window.size=(1920, 1080)
        #Window.fullscreen = True
    #    cdl = self.root.ids.calendar_day_layout
    #    print(cdl)
    #    pass

    def on_switch_tabs(self, bar: MDNavigationBar, item: MDNavigationItem, item_icon: str, item_text: str):
        if item_text == "Calendar":
            self.root.ids.main_screen_manager.transition.direction = 'right'
            self.root.ids.main_screen_manager.current = "CalendarScreen"
        elif item_text == "Cooking":
            if self.root.ids.main_screen_manager.current == 'CalendarScreen':
                self.root.ids.main_screen_manager.transition.direction = 'left'
            else:
                self.root.ids.main_screen_manager.transition.direction = 'right'
            self.root.ids.main_screen_manager.current = "CookingScreen"
        elif item_text == "3D Print":
            if self.root.ids.main_screen_manager.current == 'CalendarScreen' or self.root.ids.main_screen_manager.current == 'CookingScreen':
                self.root.ids.main_screen_manager.transition.direction = 'left'
            else:
                self.root.ids.main_screen_manager.transition.direction = 'right'
            self.root.ids.main_screen_manager.current = "PrintScreen"
        elif item_text == "Home":
            self.root.ids.main_screen_manager.transition.direction = 'left'
            self.root.ids.main_screen_manager.current = "HomeScreen"

class CalendarScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.day_widgets = []

        self.list_widgets = {}

        self._lists = {}
        self._lists['ABC List'] = ['abc', 'def', 'ghi', 'jkl', 'mno', 'pqr', 'stu', 'vwx', 'yz' ]
        self._lists['123 List'] = ['123', '456', '789', '012', '345', '678', '901', '234' ]
        self._lists['ABC123 List'] = ['abc123', 'def456', 'ghi789', 'jkl0123', 'mno345', 'pqr678', 'stu901', 'vwx234', 'yz56']
        self._lists['Colors'] = ['Red', 'Orange', 'Yellow', 'Green', 'Blue', 'Purple']

        self._displayDays = calendars.displayDays

    def on_kv_post(self, base_widget):
        self.update()

    def update(self):
        self._displayDays = calendars.displayDays

        cdl = self.ids.calendar_day_layout
        cll = self.ids.calendar_list_layout

        cdl.clear_widgets()
        cll.clear_widgets()

        self.ids.calendar_month_label.text = calendars.month_pretty

        for list in self._lists:
            lb = ListBox(list)
            lb.addItems(self._lists[list])
            cll.add_widget(lb)
            self.list_widgets[list] = lb

        for this_day in self._displayDays:
            if this_day < calendars.today:
                if this_day.month < calendars.today.month or this_day.year < calendars.today.year:
                    cd = Factory.CalendarDayPastMonth(this_day.day)
                else:
                    cd = Factory.CalendarDayPast(this_day.day)
            else:
                if this_day.month > calendars.today.month or this_day.year > calendars.today.year:
                    cd = Factory.CalendarDayFutureMonth(this_day.day)
                else:
                    cd = CalendarDay(this_day.day)

            cal_events = calendars.events(this_day)

            cdcl = cd.ids.calendar_day_content_layout
            for calendar_id in cal_events:
                ## TODO: Sort so all-day events show up first
                for ev in cal_events[calendar_id]:
                    if calendar_id in calendars.google_colors:
                        cal_color_bg, cal_color_fg = calendars.google_colors[calendar_id].values()
                        if type(ev.end) == datetime:
                            if ev.end.replace(tzinfo=pytz.utc) < calendars.now.replace(tzinfo=pytz.utc):
                                ev_lbl = CalendarEvent(text=f"[s]{ev.start.strftime(start_format)} {ev.summary}[/s]", fgcolor=cal_color_fg, bgcolor=cal_color_bg, calendar_id=calendar_id, event=ev)
                            else:
                                ev_lbl = CalendarEvent(text=f"[b]{ev.start.strftime(start_format)} {ev.summary}[/b]", fgcolor=cal_color_fg, bgcolor=cal_color_bg, calendar_id=calendar_id, event=ev)
                        else:
                            # All-day even, using 'start' since 'end' is on the next day
                            if ev.start < calendars.now.date():
                                ev_lbl = CalendarEvent(text=f"[s]{ev.summary}[/s]", fgcolor=cal_color_fg, bgcolor=cal_color_bg, calendar_id=calendar_id, event=ev)
                            else:
                                ev_lbl = CalendarEvent(text=f"[b]{ev.summary}[/b]", fgcolor=cal_color_fg, bgcolor=cal_color_bg, calendar_id=calendar_id, event=ev)
                    else:
                        project = [ p for p in calendars.todoist_projects.values() if p.name == calendar_id ][0]
                        bgcolor = calendars.todoist_colors[project.id]
                        if ev.due.datetime:
                            stime = datetime.fromisoformat(ev.due.datetime).strftime(start_format)
                            stime = f"{stime} "
                        else:
                            stime = ''

                        if date.fromisoformat(ev.due.date) < calendars.now.date():
                            ev_lbl = CalendarEvent(text=f"[s]{stime}{ev.content}[/s]", bgcolor=bgcolor, fgcolor=bgcolor, calendar_id=calendar_id, event=ev)
                        else:
                            ev_lbl = CalendarEvent(text=f"[b]{stime}{ev.content}[/b]", bgcolor=bgcolor, fgcolor=bgcolor, calendar_id=calendar_id, event=ev)

                    this_layout = MDBoxLayout(orientation='horizontal')
                    blt = Bullet(size_hint=(0.08, None))
                    blt.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
                    ev_lbl.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
                    #ev_lbl.color = [ 1,1,1,1 ]
                    ##ev_lbl.md_bg_color = calendars.google_colors[calendar_id]['background']
                    this_layout.add_widget(blt)
                    this_layout.add_widget(ev_lbl)
                    cdcl.add_widget(this_layout)

                    #if text == "":
                    #    text = ev.summary
                    #else:
                    #    text = f"{text}\n{ev.summary}"
            #cdcl.text = text
            #cdcl.add_widget(MDWidget())        <<= Why is this here?  Caused gap at bottom of calendar day

            cdl.add_widget(cd)
            self.day_widgets.append(cd)

class CookingScreen(MDScreen):
    pass

class PrintScreen(MDScreen):
    pass

class HomeScreen(MDScreen):
    pass

class CalendarDayBase(MDBoxLayout):
    def __init__(self, daynum, **kwargs):
        super().__init__(**kwargs)
        self._daynum = daynum

        self.ids.calendar_day_number_label.text = str(self._daynum)

class CalendarDayOtherMonthBase(CalendarDayBase):
    pass

#class CalendarDayPastMonth(CalendarDayOtherMonthBase):
#    pass

class CalendarDayFutureMonth(CalendarDayOtherMonthBase):
    pass

class CalendarDay(CalendarDayBase):
    pass

class CalendarDayPast(CalendarDay):
    pass

class CalendarEvent(MDLabel):
    def __init__(self, bgcolor, fgcolor, calendar_id, event, **kwargs):
        super().__init__(**kwargs)
        self._bgcolor = bgcolor
        self._fgcolor = fgcolor
        self._calendar_id = calendar_id
        self._event = event

        if sum(bgcolor) > 2.6:
            self.color = [0,0,0,1]
        else:
            self.color = [1,1,1,1]

        with self.canvas.before:
            Color(*bgcolor)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self._rect.pos = [self.pos[0]-2, self.pos[1]-2]
        self._rect.size = [self.size[0]-2, self.size[1]+4]

    def _edit_name(self, instance):
        FindDialogRoot(instance).dismiss()
        MDDialog(
            MDDialogHeadlineText(text=f"Edit Name"),
            MDDialogContentContainer(
            )
        ).open()

    def _save_edit_event(self, instance):
        dlrt = FindDialogRoot(instance)
        dlrt.dismiss()
        name = FindChildByID(dlrt, "Name").text

        if self._event.summary != name:
            calendars.update_event(self._event, name)

        # TODO: Update remaining fields!

        mainapp.root.ids.main_screen_manager.get_screen("CalendarScreen").update()

    def edit_event(self, instance):
        FindDialogRoot(instance).dismiss()

        MDDialog(
            MDDialogHeadlineText(text=f"Editing {self.text}"),
            MDDialogContentContainer(
                MDTextField(MDTextFieldHintText(text="Name"), text=self._event.summary, id="Name"),
            ),
            MDDialogButtonContainer(
               MDButton(
                   MDButtonText(text="Cancel"),
                   on_release=lambda x: FindDialogRoot(x).dismiss()
               ),
               MDButton(
                   MDButtonText(text="Save"),
                   on_release=self._save_edit_event
               )
            )
        ).open()

    def delete_event(self, instance):
        FindDialogRoot(instance).dismiss()

        MDDialog(
            MDDialogHeadlineText(text=f"Delete event: {self.text}?"),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Cancel"),
                    on_release=lambda x: FindDialogRoot(x).dismiss()
                ),
                MDButton(
                    MDButtonText(text="Delete Event"),
                    on_release=self._do_delete_event
                )
            )
        ).open()

    def _do_delete_event(self, instance):
        print("DELETING EVENT")
        FindDialogRoot(instance).dismiss()
        # TODO: IMPLEMENT DELETE
        raise NotImplementedError()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self._event.default_reminders:
                reminder = "10 minutes before"
            elif len(self._event.reminders) > 0:
                reminder = self._event.reminders[0]
            else:
                reminder = "None"

            is_recurr = self._event.recurring_event_id != None

            MDDialog(
                MDDialogHeadlineText(text=self.text),
                MDDialogSupportingText(text=self._event.start.strftime("%a %b %d, %Y - %I:%M %p")),
                MDDialogContentContainer(
                    MDListItem(
                        MDListItemSupportingText(text=f"Organizer: {self._event.organizer}"),
                    ),
                    MDListItem(
                        MDListItemSupportingText(text=f"Reminder: {reminder}")
                    ),
                    MDDivider(),
                    MDListItem(
                        MDListItemLeadingIcon(icon="calendar-lock-outline"),
                        MDListItemSupportingText(text=f"Private: {self._event.visibility == 'private'}")
                    ),
                    orientation="vertical"
                ),
                MDDialogButtonContainer(
                    MDButton(
                        MDButtonText(text="Edit"),
                        style="text",
                        on_release=self.edit_event
                    ),
                    MDButton(
                        MDButtonText(text="Delete"),
                        style="text",
                        on_release=self.delete_event
                    ),
                    MDButton(
                        MDButtonText(text="Close"),
                        style="text",
                        on_release=lambda x: FindDialogRoot(x).dismiss()
                    )
                )
            ).open()

class Bullet(MDWidget):
    pass

class ListBox(MDBoxLayout):
    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self._name = name
        self.ids.list_box_name_label.text = name

        self._items = []

    def addItems(self, item_list):
        lbl = self.ids.list_box_list
        for item in item_list:
            #lbl.add_widget(MDLabel(text=item))
            lbl.add_widget(MDListItem(MDListItemHeadlineText(text=item), MDListItemTrailingCheckbox()))

class ListBoxItem:
    def __init__(self, name, layout):
        self._name = name
        self._state = False
        self._layout = layout

        self._label = MDLabel()
        self._label.text = self._name
        self._layout.add_widget(self._label)

if __name__ == "__main__":
    global lists
    global calendars
    global mainapp
#    lists = Lists()
    calendars = Calendars()

    mainapp = HomeDisplayApp()
    mainapp.run()
    sys.exit(0)

    lists.update()
    calendars.update()
