# main.py
from kivy.config import Config
# --- НАСТРОЙКИ И КОНСТАНТЫ ---
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '700')
import datetime

from kivy.app import App

from kivy.core.clipboard import Clipboard
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import get_color_from_hex



LabelBase.register(
    name='Montserrat',
    fn_regular='Montserrat-Regular.ttf',
    fn_bold='Montserrat-Bold.ttf'
)

RU_WEEKDAYS = {
    0: "Пн", 1: "Вт", 2: "Ср", 3: "Чт", 4: "Пт", 5: "Сб", 6: "Вс"
}

PALETTE = {
    "background": "#F5F3F6",
    "primary": "#E6A4B4",
    "primary_dark": "#D68DA0",
    "secondary": "#FFE6E6",
    "text_dark": "#3D3B40",
    "text_light": "#FFFFFF",
    "hint": "#A0A0A0"
}

# --- КЛАССЫ ВИДЖЕТОВ (ЛОГИКА) ---

class ScheduleRow(BoxLayout):
    # У этого класса нет особой логики, он просто служит контейнером.
    # Вся его структура определена в .kv файле.
    pass


class MainLayout(BoxLayout):
    start_date_input = ObjectProperty(None)
    end_date_input = ObjectProperty(None)
    time_slots_layout = ObjectProperty(None)
    schedule_list_layout = ObjectProperty(None)

    def add_time_slot(self):
        # Этот Builder.load_string() остаётся здесь, так как он динамически
        # создаёт виджет по нажатию кнопки, что является частью логики.
        new_time_input = Builder.load_string("""
TextInput:
    text: '19:00'
    multiline: False
    on_text: app.root.update_time_for_selected(self)
""")
        self.time_slots_layout.add_widget(new_time_input)

    def remove_time_slot(self):
        if len(self.time_slots_layout.children) > 1:
            widget_to_remove = self.time_slots_layout.children[0]
            self.time_slots_layout.remove_widget(widget_to_remove)

    def generate_schedule(self):
        self.schedule_list_layout.clear_widgets()
        try:
            start_date_str = self.start_date_input.text
            end_date_str = self.end_date_input.text

            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            self.schedule_list_layout.clear_widgets()
            error_label = Builder.load_string("<Label>:\n    text: 'Ошибка! Введите даты правильно'")
            self.schedule_list_layout.add_widget(error_label)
            return

        times = [ri.text for ri in reversed(self.time_slots_layout.children)]
        times_str = " ".join(times)
        delta = datetime.timedelta(days=1)
        current_date = start_date

        while current_date <= end_date:
            day_of_week = RU_WEEKDAYS[current_date.weekday()]
            date_str = current_date.strftime('%d.%m')
            full_str = f"{date_str} ({day_of_week}) {times_str}"
            row_widget = ScheduleRow()
            row_widget.label.text = full_str
            self.schedule_list_layout.add_widget(row_widget)
            current_date += delta

    def update_time_for_selected(self, changed_input_widget):
        all_time_inputs = list(reversed(self.time_slots_layout.children))
        try:
            changed_index = all_time_inputs.index(changed_input_widget)
        except ValueError:
            return

        for row in self.schedule_list_layout.children:
            if row.checkbox.active:
                parts = row.label.text.split(' ')
                time_index_in_str = 2 + changed_index
                if time_index_in_str < len(parts):
                    parts[time_index_in_str] = changed_input_widget.text
                    row.label.text = " ".join(parts)

    def select_all_rows(self, is_active):
        for row in self.schedule_list_layout.children:
            row.checkbox.active = is_active

    def copy_to_clipboard(self):
        all_rows_text = []
        for row in reversed(self.schedule_list_layout.children):
            all_rows_text.append(row.label.text)
        Clipboard.copy("\n".join(all_rows_text))

# --- КЛАСС ПРИЛОЖЕНИЯ ---

class ScheduleApp(App):
    palette = ObjectProperty()

    def build(self):
        # Преобразуем HEX цвета в RGBA для Kivy
        for key, value in list(PALETTE.items()):
            PALETTE[key + '_rgba'] = get_color_from_hex(value)

        Window.clearcolor = PALETTE['background_rgba']
        self.palette = PALETTE

        # Kivy автоматически загрузит 'schedule.kv' и вернёт корневой виджет (MainLayout)
        # Нам нужно только установить начальные значения
        layout = MainLayout()
        layout.ids.start_date.text = datetime.date.today().strftime('%Y-%m-%d')
        layout.ids.end_date.text = (datetime.date.today() + datetime.timedelta(days=7)).strftime('%Y-%m-%d')
        return layout

# --- ТОЧКА ВХОДА ---

if __name__ == '__main__':
    ScheduleApp().run()