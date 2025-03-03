from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard

class WorkoutScreen(MDScreen):
    def __init__(self, **kwargs):
        super(WorkoutScreen, self).__init__(**kwargs)

    def on_kv_post(self, base_widget):
        self.add_exercise('Bench Press')
        self.add_exercise('Squats')
        self.add_exercise('Lat Pulls')
        self.add_exercise('Deadlifts')
        #self.add_exercise('Tricep Extensions')

    def add_exercise(self, exercise_name):
        testing = ExerciseRow(exercise_name)
        self.ids.main_layout.add_widget(testing)

        testing.add_set("Aaron")
        testing.add_set("Aaron")
        testing.add_set("Aaron")
        testing.add_set("Aaron")
        testing.add_set("Aaron")
        testing.add_set("Weez")

class ExerciseRow(MDCard):
    def __init__(self, name, **kwargs):
        self.name = name
        super(ExerciseRow, self).__init__(**kwargs)

        self._currset = {'Aaron': 1, 'Weez': 1}

    @property
    def exercise_name(self):
        return self.name
    
    def add_set(self, user):
        es = ExerciseSet()
        es.ids.set_number.text = str(self._currset[user])
        self._currset[user] += 1

        if user == 'Aaron':
            self.ids.set_stack_aaron.add_widget(es)
        else:
            self.ids.set_stack_weez.add_widget(es)

class ExerciseSet(MDBoxLayout):
    pass