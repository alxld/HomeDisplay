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

from kivy.factory import Factory
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window

from agents.Calendars import Calendars
from agents.Lists import Lists
from Helpers.KivyHelpers import FindDialogRoot, FindChildByID, FindWindowFromWidget
from datetime import datetime, date
#import platform
import pytz

class CalendarScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._calendars = Calendars()
        self._lists = Lists()

        self.day_widgets = []

        self.list_widgets = {}

        self._lists = {}
        self._lists['ABC List'] = ['abc', 'def', 'ghi', 'jkl', 'mno', 'pqr', 'stu', 'vwx', 'yz' ]
        self._lists['123 List'] = ['123', '456', '789', '012', '345', '678', '901', '234' ]
        self._lists['ABC123 List'] = ['abc123', 'def456', 'ghi789', 'jkl0123', 'mno345', 'pqr678', 'stu901', 'vwx234', 'yz56']
        self._lists['Colors'] = ['Red', 'Orange', 'Yellow', 'Green', 'Blue', 'Purple']

        self._displayDays = self._calendars.displayDays

        #if platform.system() in ('Linux'):
        #    self._start_format = "%-I:%M%p"
        #else:
        #    self._start_format = "%#I:%M%p"

    def on_kv_post(self, base_widget):
        self.update()

    def update(self):
        Window.set_system_cursor('wait')
        self._calendars.update()
        self._displayDays = self._calendars.displayDays

        cdl = self.ids.calendar_day_layout
        cll = self.ids.calendar_list_layout

        cdl.clear_widgets()
        cll.clear_widgets()

        # Add day names as CalendayDayNameTemplate's from the Factory
        for day in ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']:
            cdl.add_widget(Factory.CalendarDayNameTemplate(text=day))

        self.ids.calendar_month_label.text = self._calendars.month_pretty

        for list in self._lists:
            lb = ListBox(list)
            lb.addItems(self._lists[list])
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

        if self._event.summary != name:
            self._calendars.update_event(self._event, name)

        # TODO: Update remaining fields!

        self._screen.root.ids.main_screen_manager.get_screen("CalendarScreen").update()

    def on_keyboard_closed(self):
        print("Keyboard closed")

    def edit_event(self, instance):
        FindDialogRoot(instance).dismiss()
        this_window = FindWindowFromWidget(instance)
        #self._keyboard = this_window.request_keyboard(self.on_keyboard_closed, instance, 'text')
        #self._keyboard = VKeyboard()
        #this_window.release_all_keyboards()
        #this_window.add_widget(self._keyboard)

        MDDialog(
            MDDialogHeadlineText(text=f"Editing {self.text}"),
            MDDialogContentContainer(
                MDTextField(MDTextFieldHintText(text="Name"), text=self._event.name, id="Name"),
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
            ),
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
            reminder = self._event.reminders
            is_recurr = self._event.is_recurring
            start_time = self._event.start_datetime
            descr = self._event.description

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