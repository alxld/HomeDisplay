from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer, MDDialogSupportingText
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText, MDListItemTrailingCheckbox, MDListItemSupportingText, MDListItemLeadingIcon
from kivymd.uix.label import MDLabel
from kivymd.uix.widget import MDWidget
from kivymd.uix.divider import MDDivider
from kivy.uix.vkeyboard import VKeyboard
from kivymd.uix.pickers import MDModalDatePicker, MDDockedDatePicker, MDTimePickerDialHorizontal

from kivy.clock import Clock
from kivy.factory import Factory
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from kivy.config import Config
from kivy.metrics import dp

from agents.Calendars import Calendars
from agents.Lists import Lists
from Helpers.KivyHelpers import FindDialogRoot, FindChildByID, FindWindowFromWidget
from datetime import datetime, date, timedelta, time
#import platform
import pytz

class CalendarScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._calendars = Calendars()
        self._lists = Lists()

        self.day_widgets = []

        self.list_widgets = {}

        #self._lists = {}
        #self._lists['ABC List'] = ['abc', 'def', 'ghi', 'jkl', 'mno', 'pqr', 'stu', 'vwx', 'yz' ]
        #self._lists['123 List'] = ['123', '456', '789', '012', '345', '678', '901', '234' ]
        #self._lists['ABC123 List'] = ['abc123', 'def456', 'ghi789', 'jkl0123', 'mno345', 'pqr678', 'stu901', 'vwx234', 'yz56']
        #self._lists['Colors'] = ['Red', 'Orange', 'Yellow', 'Green', 'Blue', 'Purple']

        self._displayDays = self._calendars.displayDays

        #if platform.system() in ('Linux'):
        #    self._start_format = "%-I:%M%p"
        #else:
        #    self._start_format = "%#I:%M%p"

    def on_kv_post(self, base_widget):
        self.update()
        Clock.schedule_interval(self.update_callback, 15*60)

    def update_callback(self, dt):
        self.update()

    def update(self):
        Window.set_system_cursor('wait')
        self._calendars.update()
        self._lists.update()

        self._displayDays = self._calendars.displayDays

        cdl = self.ids.calendar_day_layout
        cll = self.ids.calendar_list_layout

        cdl.clear_widgets()
        cll.clear_widgets()

        # Add day names as CalendayDayNameTemplate's from the Factory
        for day in ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']:
            cdl.add_widget(Factory.CalendarDayNameTemplate(text=day))

        self.ids.calendar_month_label.text = self._calendars.month_pretty

        lists_to_show = ['Shopping', "Aaron's ToDo"]
        for listname, list in self._lists.items():
            if not listname in lists_to_show:
                continue
            lb = ListBox(listname)
            #for item in list.items:
            #    #lb.add_widget(MDListItem(MDListItemHeadlineText(text=item._text), MDListItemTrailingCheckbox()))
            #    lb.addItem(item._text)
            lb.addItems(list.items)
            cll.add_widget(lb)
            self.list_widgets[list] = lb

        for this_day in self._displayDays:
            if this_day < self._calendars.today:
                if this_day.month < self._calendars.today.month or this_day.year < self._calendars.today.year:
                    cd = Factory.CalendarDayPastMonth(this_day.day)
                else:
                    cd = Factory.CalendarDayPast(this_day.day)
            else:
                if this_day.month > self._calendars.today.month or this_day.year > self._calendars.today.year:
                    cd = Factory.CalendarDayFutureMonth(this_day.day)
                else:
                    cd = CalendarDay(this_day.day)

            cal_events = self._calendars.events(this_day)

            cdcl = cd.ids.calendar_day_content_layout
            for calendar_id in cal_events:
                ## TODO: Sort so all-day events show up first
                for ev in cal_events[calendar_id]:
                    bgcolor, fgcolor = ev.colors
                    if type(ev.end) == datetime:
                        if ev.end.replace(tzinfo=pytz.utc) < self._calendars.now.replace(tzinfo=pytz.utc):
                            ev_lbl = CalendarItem(text=f"[s]{ev.start_pretty} {ev.name}[/s]", fgcolor=fgcolor, bgcolor=bgcolor, calendar_id=calendar_id, event=ev, screen=self)
                        else:
                            ev_lbl = CalendarItem(text=f"[b]{ev.start_pretty} {ev.name}[/b]", fgcolor=fgcolor, bgcolor=bgcolor, calendar_id=calendar_id, event=ev, screen=self)
                    else:
                        # All-day event, using 'start' since 'end' is on the next day
                        if ev.start_date < self._calendars.now.date():
                            ev_lbl = CalendarItem(text=f"[s]{ev.name}[/s]", fgcolor=fgcolor, bgcolor=bgcolor, calendar_id=calendar_id, event=ev, screen=self)
                        else:
                            ev_lbl = CalendarItem(text=f"[b]{ev.name}[/b]", fgcolor=fgcolor, bgcolor=bgcolor, calendar_id=calendar_id, event=ev, screen=self)
#                    if calendar_id in self._calendars.google_colors:
#                        if type(ev.end) == datetime:
#                            if ev.end.replace(tzinfo=pytz.utc) < self._calendars.now.replace(tzinfo=pytz.utc):
#                                ev_lbl = CalendarItem(text=f"[s]{ev.start_pretty} {ev.name}[/s]", fgcolor=fgcolor, bgcolor=bgcolor, calendar_id=calendar_id, event=ev, screen=self)
#                            else:
#                                ev_lbl = CalendarItem(text=f"[b]{ev.start_pretty} {ev.name}[/b]", fgcolor=fgcolor, bgcolor=bgcolor, calendar_id=calendar_id, event=ev, screen=self)
#                        else:
#                            # All-day even, using 'start' since 'end' is on the next day
#                            if ev.start < self._calendars.now.date():
#                                ev_lbl = CalendarItem(text=f"[s]{ev.name}[/s]", fgcolor=fgcolor, bgcolor=bgcolor, calendar_id=calendar_id, event=ev, screen=self)
#                            else:
#                                ev_lbl = CalendarItem(text=f"[b]{ev.name}[/b]", fgcolor=fgcolor, bgcolor=bgcolor, calendar_id=calendar_id, event=ev, screen=self)
#                    else:
#                        project = [ p for p in self._calendars.todoist_projects.values() if p.name == calendar_id ][0]
#                        bgcolor = self._calendars.todoist_colors[project.id]
#                        if ev.due.datetime:
#                            stime = datetime.fromisoformat(ev.due.datetime).strftime(self._start_format)
#                            stime = f"{stime} "
#                        else:
#                            stime = ''
#
#                        if date.fromisoformat(ev.due.date) < self._calendars.now.date():
#                            ev_lbl = CalendarItem(text=f"[s]{stime}{ev.content}[/s]", bgcolor=bgcolor, fgcolor=bgcolor, calendar_id=calendar_id, event=ev, screen=self)
#                        else:
#                            ev_lbl = CalendarItem(text=f"[b]{stime}{ev.content}[/b]", bgcolor=bgcolor, fgcolor=bgcolor, calendar_id=calendar_id, event=ev, screen=self)

                    this_layout = MDBoxLayout(orientation='horizontal')
                    blt = Bullet(size_hint=(0.08, None))
                    blt.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
                    ev_lbl.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
                    #ev_lbl.color = [ 1,1,1,1 ]
                    ##ev_lbl.md_bg_color = self._calendars.google_colors[calendar_id]['background']
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
        Window.set_system_cursor('arrow')

    def add_event(self):
        MDDialog(
            MDDialogHeadlineText(text="Add Event"),
            MDDialogContentContainer(
                MDTextField(MDTextFieldHintText(text="Name"), id="Name", mode="filled"),
                MDTextField(MDTextFieldHintText(text="Description"), id="Description", mode="filled"),
                MDTextField(MDTextFieldHintText(text="Date"), text=datetime.now().date().strftime("%Y-%m-%d"), id="Date", mode="filled", on_touch_down=self.show_date_picker, readonly=True, focus_behavior=False),
                MDTextField(MDTextFieldHintText(text="Time"), text="12:00", id="Time", mode="filled", on_touch_down=self.show_time_picker, readonly=True, focus_behavior=False),
                MDTextField(MDTextFieldHintText(text="Recurrence"), mode="filled", id="Recurrence"),
                orientation="vertical"
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Cancel"),
                    on_release=lambda x: FindDialogRoot(x).dismiss()
                ),
                MDButton(
                    MDButtonText(text="Save"),
                    on_release=self._save_new_event
                )
            )
        ).open()

    def show_date_picker(self, instance, touch):
        def update_date(dp_instance):
            instance.text = dp_instance.get_date()[0].strftime("%Y-%m-%d")
            dp_instance.dismiss()

        if not instance.collide_point(*touch.pos):
            return False

        start_date = datetime.strptime(instance.text, "%Y-%m-%d")
        self._dp = MDDockedDatePicker(day=start_date.day, month=start_date.month, year=start_date.year, firstweekday=6)
        self._dp.bind(on_ok=update_date, on_cancel=self._dp.dismiss)
        self._dp.open()
        
        self._dp.pos = [Window.width/2 - self._dp.width/2, Window.height/2 - self._dp.height/2] 

        return True

    def show_time_picker(self, instance, touch):
        def update_time(tp_instance):
            instance.text = tp_instance.time.strftime("%H:%M")
            tp_instance.dismiss()

        def switch_to_minutes(tp_instance, touch):
            tp = tp_instance.parent.parent.parent.parent
            if tp.is_open:
                tp._selector.mode = "minute"

            return True
    
        def switch_to_hours(tp_instance, touch):
            tp = tp_instance.parent.parent.parent.parent
            if tp.is_open:
                tp._selector.mode = "hour"

            return True

        if not instance.collide_point(*touch.pos):
            return False

        start_time = datetime.strptime(instance.text, "%H:%M").time()
        self._tp = MDTimePickerDialHorizontal()
        self._tp.ids._time_input.ids.minute.bind(on_touch_down=switch_to_minutes)
        self._tp.ids._time_input.ids.hour.bind(on_touch_down=switch_to_hours)
        self._tp.set_time(start_time)
        #if start_time.hour == 0:
        #    self._tp.set_time(time(12, start_time.minute))
        #else:
        #    self._tp.set_time(start_time)
        #if start_time.hour < 12:
        #    self._tp.am_pm = "am"
        #    self._tp.ids._am_pm_selector.mode = "am"
        #else:
        #    self._tp.am_pm = "pm"
        #    self._tp.ids._am_pm_selector.mode = "pm"

        self._tp.bind(on_ok=update_time, on_cancel=self._tp.dismiss)
        #self._tp.bind(on_selector_hour=self._on_selector_hours)
        self._tp.open()

        self._tp.pos = [Window.width/2 - self._tp.width/2, Window.height/2 - self._tp.height/2]

        self._tp._selector.mode = "hour"
        
        return True

    def _save_new_event(self, instance):
        dlrt = FindDialogRoot(instance)
        dlrt.dismiss()

        name = FindChildByID(dlrt, "Name").text
        descr = FindChildByID(dlrt, "Description").text
        date = FindChildByID(dlrt, "Date").text
        time = FindChildByID(dlrt, "Time").text
        recstr = FindChildByID(dlrt, "Recurrence").text

        self._calendars.addTodoistEvent(name=name, description=descr, due_date=date, due_time=time, recurrence=recstr)
        
        self.update()

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

class CalendarItem(MDLabel):
    def __init__(self, bgcolor, fgcolor, calendar_id, event, screen, **kwargs):
        super().__init__(**kwargs)
        self._bgcolor = bgcolor
        self._fgcolor = fgcolor
        self._calendar_id = calendar_id
        self._event = event
        self._screen = screen

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
        descr = FindChildByID(dlrt, "Description").text
        date = FindChildByID(dlrt, "Date").text
        time = FindChildByID(dlrt, "Time").text
        recstr = FindChildByID(dlrt, "Recurrence").text

        self._event.updateEvent(name=name, description=descr, due_date=date, due_time=time, recurrence=recstr)

        self._screen.update()

    def on_keyboard_closed(self):
        print("Keyboard closed")

    def edit_event(self, instance):
        FindDialogRoot(instance).dismiss()
        this_window = FindWindowFromWidget(instance)
        start_datetime = self._event.start_datetime

        if start_datetime.date() == datetime.now().date():
            this_cont = MDDialogButtonContainer(
               MDButton(
                   MDButtonText(text="Cancel"),
                   on_release=lambda x: FindDialogRoot(x).dismiss()
               ),
               MDButton(
                   MDButtonText(text="Save"),
                   on_release=self._save_edit_event
               ),
               MDButton(
                   MDButtonText(text="Tomorrow"),
                   on_release=self._move_event_tomorrow
               )
            )
        else:
            this_cont = MDDialogButtonContainer(
               MDButton(
                   MDButtonText(text="Cancel"),
                   on_release=lambda x: FindDialogRoot(x).dismiss()
               ),
               MDButton(
                   MDButtonText(text="Save"),
                   on_release=self._save_edit_event
               ),
                MDButton(
                     MDButtonText(text="Today"),
                     on_release=self._move_event_today
                )
            )

        self._dlg = MDDialog(
            MDDialogHeadlineText(text=f"Editing {self.text}"),
            MDDialogContentContainer(
                MDTextField(MDTextFieldHintText(text="Name"), text=self._event.name, id="Name", mode="filled"),
                MDTextField(MDTextFieldHintText(text="Description"), text=self._event.description, id="Description", mode="filled"),
                MDTextField(MDTextFieldHintText(text="Date"), text=start_datetime.date().strftime("%Y-%m-%d"), id="Date", mode="filled", on_touch_down=self.show_date_picker, readonly=True, focus_behavior=False),
                MDTextField(MDTextFieldHintText(text="Time"), text=start_datetime.time().strftime("%H:%M"), id="Time", mode="filled", on_touch_down=self.show_time_picker, readonly=True, focus_behavior=False),
                MDTextField(MDTextFieldHintText(text="Recurrence"), text=self._event.recurrence, id="Recurrence", mode="filled"),
                orientation="vertical"
            ),
            this_cont
        )
        self._dlg.open()

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
        FindDialogRoot(instance).dismiss()
        self._event.deleteEvent()
        self._screen.update()
    
    def show_date_picker(self, instance, touch):
        if not instance.collide_point(*touch.pos):
            return False

        start_date = self._event.start_datetime.date()
        self._dp = MDDockedDatePicker(day=start_date.day, month=start_date.month, year=start_date.year, firstweekday=6)
        self._dp.bind(on_ok=self.on_date_selected, on_cancel=self._dp.dismiss)
        self._dp.open()
        
        self._dp.pos = [Window.width/2 - self._dp.width/2, Window.height/2 - self._dp.height/2] 

        return True
    
    def show_time_picker(self, instance, touch):
        if not instance.collide_point(*touch.pos):
            return False

        start_time = self._event.start_datetime.time()
        self._tp = MDTimePickerDialHorizontal()
        self._tp.ids._time_input.ids.minute.bind(on_touch_down=self._switch_to_minutes)
        self._tp.ids._time_input.ids.hour.bind(on_touch_down=self._switch_to_hours)
        if start_time.hour == 0:
            self._tp.set_time(time(12, start_time.minute))
        else:
            self._tp.set_time(start_time)
        if start_time.hour < 12:
            self._tp.am_pm = "am"
        else:
            self._tp.am_pm = "pm"
        self._tp.bind(on_ok=self.on_time_selected, on_cancel=self._tp.dismiss)
        #self._tp.bind(on_selector_hour=self._on_selector_hours)
        self._tp.open()

        self._tp.pos = [Window.width/2 - self._tp.width/2, Window.height/2 - self._tp.height/2]

        self._tp._selector.mode = "hour"
        
        return True
    
    def _switch_to_minutes(self, instance, other):
        if self._tp.is_open:
            self._tp._selector.mode = "minute"
    
        return True
    
    def _switch_to_hours(self, instance, other):
        if self._tp.is_open:
            self._tp._selector.mode = "hour"

        return True

    def on_date_selected(self, dp):
        date = self._dp.get_date()[0]
        self._dp.dismiss()
        start_date_widget = FindChildByID(self._dlg, "Date")
        start_date_widget.text = date.strftime("%Y-%m-%d")

    def on_time_selected(self, tp):
        time = self._tp.time
        self._tp.dismiss()
        start_time_widget = FindChildByID(self._dlg, "Time")
        start_time_widget.text = time.strftime("%H:%M")
    
    def _move_event_tomorrow(self, instance):
        FindDialogRoot(instance).dismiss()
        tomorrow = self._event.start_datetime.date() + timedelta(days=1)
        self._event.updateEvent(due_date=str(tomorrow))
        #self._event.moveDateTime(tomorrow)
        self._screen.update()

    def _move_event_today(self, instance):
        FindDialogRoot(instance).dismiss()
        today = datetime.now().date()
        self._event.updateEvent(due_date=str(today))
        #self._event.moveDateTime(today)
        self._screen.update()

    def _mark_event_complete(self, instance):
        FindDialogRoot(instance).dismiss()
        self._event.completeEvent()
        self._screen.update()

    def _do_move_event(self, instance):
        FindDialogRoot(instance).dismiss()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            reminder = self._event.reminders
            start_time = self._event.start_datetime
            descr = self._event.description

            if self._event.is_recurring:
                recurr_text = f"{True} ({self._event.recurrence})"
            else:
                recurr_text = False

            if start_time.date() == datetime.now().date():
                this_cont = MDDialogButtonContainer(
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
                    ),
                    MDButton(
                        MDButtonText(text="Tomorrow"),
                        style="text",
                        on_release=self._move_event_tomorrow
                    ),
                    MDButton(
                        MDButtonText(text="Complete"),
                        style="text",
                        on_release=self._mark_event_complete
                    )
                )
            else:
                this_cont = MDDialogButtonContainer(
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
                    ),
                    MDButton(
                        MDButtonText(text="Today"),
                        style="text",
                        on_release=self._move_event_today
                    ),
                    MDButton(
                        MDButtonText(text="Complete"),
                        style="text",
                        on_release=self._mark_event_complete
                    )
                )

            MDDialog(
                MDDialogHeadlineText(text=self.text),
                MDDialogSupportingText(text=self._event.start_pretty),
                MDDialogContentContainer(
                    MDListItem(
                        MDListItemSupportingText(text=f"Organizer: {self._event.organizer}"),
                    ),
                    MDListItem(
                        MDListItemSupportingText(text=f"Reminder: {reminder}")
                    ),
                    MDListItem(
                        MDListItemSupportingText(text=f"Description: {descr}")
                    ),
                    MDListItem(
                        MDListItemSupportingText(text=f"Recurring: {recurr_text}")
                    ),
                    MDDivider(),
                    MDListItem(
                        MDListItemLeadingIcon(icon="calendar-lock-outline"),
                        MDListItemSupportingText(text=f"Private: {self._event.visibility == 'private'}")
                    ),
                    orientation="vertical"
                ),
                this_cont
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
        for idx, item in enumerate(item_list):
            #lbl.add_widget(MDListItem(MDListItemHeadlineText(text=item._text), MDListItemTrailingCheckbox(id=str(idx))))
            this_item = ListBoxItem(item, idx, self)
            self._items.append(item)

            lbl.add_widget(this_item)

class ListBoxItem(MDListItem):
    def __init__(self, item, idx, lb, **kwargs):
        super().__init__(**kwargs)
        if item.indented:
            ind = "    "
        else:
            ind = ""
        if item.checked:
            self.ids.item_text.text = f"[s]{ind}{item.text}[/s]"
            self.ids.item_cb.active = True
        else:
            self.ids.item_text.text = f"{ind}{item.text}"
            self.ids.item_cb.active = False
        self.ids.item_cb.id = str(idx)
        self.ids.item_cb.bind(on_touch_down=self.check_box_toggled)

        self._list_box = lb

    def check_box_toggled(self, instance, touch):
        if instance.collide_point(*touch.pos):
            this_idx = int(instance.id)
            this_item = self._list_box._items[this_idx]
            this_item.checked = not this_item.checked

            root_inst = self._list_box.parent.parent.parent.parent
            root_inst._lists.push()
            root_inst.update()
            return True
#    def __init__(self, name, layout):
#        self._name = name
#        self._state = False
#        self._layout = layout
#
#        self._label = MDLabel()
#        self._label.text = self._name
#        self._layout.add_widget(self._label)