import random
import pandas as pd
import os
import sys
from PyQt6.QtWidgets import (QApplication, QLabel, QPushButton, QFrame, QLineEdit, 
                            QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt, QTimer

# Deck configurations
deck_sequences = {
    'deck_a': [100, 100, -50, 100, -200, 100, -100, 100, -150, -250] * 3,  # -25/card
    'deck_b': [100, 100, 100, 100, 100, 100, 100, 100, 100, -1150] * 3,    # -25/card
    'deck_c': [50, 50, 50, 25, -25, 50, 0, 50, 25, -25] * 3,                # +25/card
    'deck_d': [50, 50, 50, 50, 50, 50, 50, 50, 50, -200] * 3,             # +25/card
}

# Initialize variables
net_worth = 2000
previous_net_worth = net_worth
current_position = 0  # Arrow starts at Deck A
decks = ['deck_a', 'deck_b', 'deck_c', 'deck_d']
trial_data = []  # Stores trial data for Excel output
timeout_duration = 4000  # Milliseconds to timeout
total_trials = 120
current_trial = 0
practice_trials = 10  # Number of practice trials
# Initialize deck instances for drawing (shuffled copies)
deck_instances = {deck: list(seq) for deck, seq in deck_sequences.items()}
for deck in deck_instances.values():
    random.shuffle(deck)

# Function to convert numbers to Persian numerals
def persian_number(number):
    persian_digits = {
        '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
        '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
    }
    if isinstance(number, int) or isinstance(number, float):
        number_str = str(abs(number))
        persian_num = ''.join(persian_digits[digit] for digit in number_str)
        if number < 0:
            return f"-{persian_num}"
        return persian_num
    return number

# Function to log data to Excel
def log_data(participant_id, participant_name, trial_type, trial_number, presented_deck, choice, outcome, net_worth):
    trial_data.append({
        'Participant ID': participant_id,
        'Participant Name': participant_name,
        'Trial Type': trial_type,
        'Trial Number': trial_number,
        'Presented Deck': presented_deck,
        'Choice': choice,
        'Outcome': persian_number(outcome) if outcome != 0 else "0",
        'Net Worth': persian_number(net_worth),
    })

# Function to save data to Excel
def save_data(participant_id):
    try:
        output_dir = "Iowa_Gambling_Task_pyqt/output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        df = pd.DataFrame(trial_data)
        output_file = os.path.join(output_dir, f"Participant_{participant_id}.xlsx")
        df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"Data saved to {output_file}")
    except Exception as e:
        print(f"Error saving data: {e}")

# Function to simulate deck outcome by drawing from sequences
def simulate_outcome(deck):
    if deck_instances[deck]:  # Check if deck has cards left
        return deck_instances[deck].pop(0)  # Draw and remove the first card
    return 0  # Fallback if deck is empty (shouldn't happen with 120 trials)

# GUI Application
class IGTApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Iowa Gambling Task")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: #f0f0f0;")

        self.custom_font = QFont("B Koodak", 20)
        self.net_worth = net_worth
        self.previous_net_worth = previous_net_worth
        self.current_position = current_position
        self.decks = decks
        self.trial_data = trial_data
        self.current_trial = current_trial
        self.presented_deck = None
        self.participant_id = ""
        self.participant_name = ""
        self.timer_running = False
        self.space_enabled = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.timeout)
        self.is_practice = True
        self.game_ended = False

        # Load deck images
        self.deck_images = []
        for deck in self.decks:
            img_path = f"/home/parinaz/igt/Iowa_Gambling_Task_tkinter/images/{deck}.png"
            pixmap = QPixmap(img_path)
            pixmap = pixmap.scaled(200, 300, Qt.AspectRatioMode.KeepAspectRatio)
            self.deck_images.append(pixmap)

        # Load arrow image
        self.arrow_img = QPixmap("/home/parinaz/igt/Iowa_Gambling_Task_tkinter/images/arrow.png")
        self.arrow_img = self.arrow_img.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio)

        # Load F and J key images
        self.f_key_img = QPixmap("/home/parinaz/igt/Iowa_Gambling_Task_tkinter/images/f_key.png")
        self.f_key_img = self.f_key_img.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio)

        self.j_key_img = QPixmap("/home/parinaz/igt/Iowa_Gambling_Task_tkinter/images/j_key.png")
        self.j_key_img = self.j_key_img.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio)

        # Main layout
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Start with the registration page
        self.register_page()

    def keyPressEvent(self, event):
        if self.game_ended:
            return        
        if event.key() == Qt.Key.Key_F and self.timer_running:
            self.play()
        elif event.key() == Qt.Key.Key_J and self.timer_running:
            self.pass_turn()
        elif event.key() == Qt.Key.Key_Space and self.space_enabled and not self.timer_running:
            self.continue_trial()
        elif event.key() == Qt.Key.Key_Space and hasattr(self, 'go_to_next_page') and not self.timer_running:
            self.go_to_next_page()

    def clear_layout(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self.clear_layout_recursive(item.layout())

    def clear_layout_recursive(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout_recursive(item.layout())

    def register_page(self):
        self.clear_layout()
        
        registration_layout = QVBoxLayout()
        
        title_label = QLabel("ثبت اطلاعات")
        title_label.setFont(self.custom_font)
        title_label.setStyleSheet("color: blue;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        registration_layout.addWidget(title_label)
        
        instruction_label = QLabel("نام و شناسه خود را وارد کنید:")
        instruction_label.setFont(self.custom_font)
        instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        registration_layout.addWidget(instruction_label)
        
        self.name_entry = QLineEdit()
        self.name_entry.setFont(self.custom_font)
        self.name_entry.setAlignment(Qt.AlignmentFlag.AlignRight)
        registration_layout.addWidget(self.name_entry)
        
        self.id_entry = QLineEdit()
        self.id_entry.setFont(self.custom_font)
        self.id_entry.setAlignment(Qt.AlignmentFlag.AlignRight)
        registration_layout.addWidget(self.id_entry)
        
        start_button = QPushButton("شروع")
        start_button.setFont(self.custom_font)
        start_button.setStyleSheet("background-color: green; color: white;")
        start_button.clicked.connect(self.start_task)
        registration_layout.addWidget(start_button)
        
        self.main_layout.addLayout(registration_layout)
        
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

    def start_task(self):
        self.participant_name = self.name_entry.text()
        self.participant_id = self.id_entry.text()
        if not self.participant_name or not self.participant_id:
            QMessageBox.warning(self, "خطای ورودی", "لطفاً نام و شناسه خود را وارد کنید.")
            return
        self.show_welcome_page()

    def show_welcome_page(self):
        self.clear_layout()
        welcome_layout = QVBoxLayout()
        
        welcome_label = QLabel("در این بازی هدف شما این است که تا حد ممکن پول برنده شوید!")
        welcome_label.setFont(self.custom_font)
        welcome_label.setStyleSheet("color: blue;")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(welcome_label)
        
        instruction1 = QLabel("برای هر دور یک فلش زرد رنگ بالای یکی از چهار دسته کارت نشان داده خواهد شد")
        instruction1.setFont(self.custom_font)
        instruction1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(instruction1)
        
        instruction2 = QLabel("به واسطه آن، میتوانید بین بازی کردن یا رد کردن آن کارت تصمیم بگیرید.")
        instruction2.setFont(self.custom_font)
        instruction2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(instruction2)
        
        instruction3 = QLabel("اگر بازی کنید؛ ممکن است سکه برنده شوید و یا از دست بدهید")
        instruction3.setFont(self.custom_font)
        instruction3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(instruction3)
        
        instruction4 = QLabel("(و یا نه سکه ببرید و نه از دست بدهید)")
        instruction4.setFont(self.custom_font)
        instruction4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(instruction4)
        
        instruction5 = QLabel("اگر رد شوید؛ نه سکه می‌برید و نه چیزی از دست خواهید داد.")
        instruction5.setFont(self.custom_font)
        instruction5.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(instruction5)

        instruction5 = QLabel("برخی از دسته کارت ها سودآور تر از بقیه خواهند بود.")
        instruction5.setFont(self.custom_font)
        instruction5.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(instruction5)
        
        instruction6 = QLabel("توجه کنید که در هر نوبت فقط 4 ثانیه زمان دارید تا تصمیم بگیرید")
        instruction6.setFont(self.custom_font)
        instruction6.setStyleSheet("color: red;")
        instruction6.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(instruction6)
        
        instruction7 = QLabel("با 2000 سکه شروع خواهید کرد.")
        instruction7.setFont(self.custom_font)
        instruction7.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(instruction7)
        
        space_label = QLabel("برای ادامه کلید space را فشار دهید.")
        space_label.setFont(self.custom_font)
        space_label.setStyleSheet("color: green;")
        space_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(space_label)
        
        self.main_layout.addLayout(welcome_layout)
        
        self.go_to_next_page = self.show_practice_instructions

    def show_practice_instructions(self):
        self.clear_layout()
        practice_layout = QVBoxLayout()
        
        title_label = QLabel("پیش از آغاز بازی اصلی، به بازی تمرینی خواهید پرداخت")
        title_label.setFont(self.custom_font)
        title_label.setStyleSheet("color: blue;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        practice_layout.addWidget(title_label)
        
        instruction1 = QLabel("این مرحله در چند تکرار انجام خواهد شد و فقط جهت آشنایی شما")
        instruction1.setFont(self.custom_font)
        instruction1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        practice_layout.addWidget(instruction1)
        
        instruction2 = QLabel("با ساختار و نحوه انجام بازی است.")
        instruction2.setFont(self.custom_font)
        instruction2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        practice_layout.addWidget(instruction2)
        
        instruction3 = QLabel("لذا نتایج این مرحله ثبت نخواهد شد")
        instruction3.setFont(self.custom_font)
        instruction3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        practice_layout.addWidget(instruction3)
        
        space_label = QLabel("برای ادامه کلید space را فشار دهید.")
        space_label.setFont(self.custom_font)
        space_label.setStyleSheet("color: green;")
        space_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        practice_layout.addWidget(space_label)
        
        self.main_layout.addLayout(practice_layout)
        
        self.go_to_next_page = self.practice_game

    def practice_game(self):
        self.is_practice = True
        self.current_trial = 0
        self.main_task()

    def show_transition_to_main_game(self):
        self.clear_layout()
        transition_layout = QVBoxLayout()
        
        title_label = QLabel("پایان مرحله تمرینی")
        title_label.setFont(self.custom_font)
        title_label.setStyleSheet("color: blue;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        transition_layout.addWidget(title_label)
        
        instruction1 = QLabel("اکنون به بازی اصلی میپردازید.")
        instruction1.setFont(self.custom_font)
        instruction1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        transition_layout.addWidget(instruction1)
        
        instruction2 = QLabel("در این مرحله پاسخ های شما ثبت خواهد شد و در پایان")
        instruction2.setFont(self.custom_font)
        instruction2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        transition_layout.addWidget(instruction2)
        
        instruction3 = QLabel("نتیجه نهایی خود را مشاهده خواهید کرد.")
        instruction3.setFont(self.custom_font)
        instruction3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        transition_layout.addWidget(instruction3)
        
        instruction4 = QLabel("موفق باشید.")
        instruction4.setFont(self.custom_font)
        instruction4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        transition_layout.addWidget(instruction4)
        
        space_label = QLabel("برای ادامه کلید space را فشار دهید.")
        space_label.setFont(self.custom_font)
        space_label.setStyleSheet("color: green;")
        space_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        transition_layout.addWidget(space_label)
        
        self.main_layout.addLayout(transition_layout)
        
        self.go_to_next_page = self.start_main_game

    def start_main_game(self):
        self.is_practice = False
        self.current_trial = 0
        self.net_worth = 2000
        self.previous_net_worth = 2000
        # Reset deck instances for main game
        global deck_instances
        deck_instances = {deck: list(seq) for deck, seq in deck_sequences.items()}
        for deck in deck_instances.values():
            random.shuffle(deck)
        self.main_task()

    def main_task(self):
        self.clear_layout()
        
        main_layout = QVBoxLayout()

        self.net_worth_label = QLabel(f"موجودی فعلی: {persian_number(self.net_worth)} سکه")
        self.net_worth_label.setFont(self.custom_font)
        self.net_worth_label.setStyleSheet("color: purple;")
        self.net_worth_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.net_worth_label)
        
        self.previous_net_worth_label = QLabel(f"موجودی قبلی: {persian_number(self.previous_net_worth)} سکه")
        self.previous_net_worth_label.setFont(self.custom_font)
        self.previous_net_worth_label.setStyleSheet("color: orange;")
        self.previous_net_worth_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.previous_net_worth_label)
        
        deck_grid = QGridLayout()
        
        self.arrow_labels = []
        for i in range(4):
            label = QLabel()
            if i == self.current_position:
                label.setPixmap(self.arrow_img)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            deck_grid.addWidget(label, 0, 3-i)
            self.arrow_labels.append(label)
        
        self.deck_labels = []
        for i, deck_img in enumerate(self.deck_images):
            label = QLabel()
            label.setPixmap(deck_img)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            deck_grid.addWidget(label, 1, 3-i)
            self.deck_labels.append(label)
        
        self.feedback_labels = []
        for i in range(4):
            label = QLabel("")
            label.setFont(self.custom_font)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            deck_grid.addWidget(label, 2, 3-i)
            self.feedback_labels.append(label)
        
        f_key_layout = QVBoxLayout()
        f_key_label = QLabel()
        f_key_label.setPixmap(self.f_key_img)
        f_key_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f_key_text = QLabel("برای بازی کردن")
        f_key_text.setFont(self.custom_font)
        f_key_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f_key_layout.addWidget(f_key_label)
        f_key_layout.addWidget(f_key_text)
        deck_grid.addLayout(f_key_layout, 3, 3)
        
        j_key_layout = QVBoxLayout()
        j_key_label = QLabel()
        j_key_label.setPixmap(self.j_key_img)
        j_key_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        j_key_text = QLabel("برای گذر کردن")
        j_key_text.setFont(self.custom_font)
        j_key_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        j_key_layout.addWidget(j_key_label)
        j_key_layout.addWidget(j_key_text)
        deck_grid.addLayout(j_key_layout, 3, 0)
        
        main_layout.addLayout(deck_grid)
        
        self.space_label_container = QVBoxLayout()
        main_layout.addLayout(self.space_label_container)
        
        self.main_layout.addLayout(main_layout)
        
        self.start_trial()

    def start_trial(self):
        if self.is_practice and self.current_trial >= practice_trials:
            self.show_transition_to_main_game()
            return
        elif not self.is_practice and self.current_trial >= total_trials:
            self.quit()
            return
        self.current_trial += 1
        self.presented_deck = self.decks[self.current_position]
        self.timer_running = True
        self.space_enabled = False
        self.timer.start(timeout_duration)

    def timeout(self):
        if self.timer_running:
            print("Timeout triggered")
            self.timer_running = False
            self.timer.stop()
            self.previous_net_worth = self.net_worth
            self.feedback_labels[self.current_position].setText("گذر")
            self.feedback_labels[self.current_position].setStyleSheet("color: black;")
            if not self.is_practice:
                log_data(self.participant_id, self.participant_name, 'main', self.current_trial, self.presented_deck, 'pass', 0, self.net_worth)
            self.update_ui()
            self.wait_for_space()

    def wait_for_space(self):
        self.space_enabled = True
        while self.space_label_container.count():
            item = self.space_label_container.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        
        space_label = QLabel("برای ادامه فاصله (Space) را بزنید")
        space_label.setFont(self.custom_font)
        space_label.setStyleSheet("color: blue;")
        space_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.space_label_container.addWidget(space_label)

    def continue_trial(self):
        if not self.space_enabled:
            return
        print("Continuing to next trial")
        self.space_enabled = False
        
        while self.space_label_container.count():
            item = self.space_label_container.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        
        self.clear_feedback()
        
        self.current_position = random.randint(0, len(self.decks) - 1)
        for i, label in enumerate(self.arrow_labels):
            if i == self.current_position:
                label.setPixmap(self.arrow_img)
            else:
                label.clear()
        
        self.start_trial()

    def clear_feedback(self):
        for label in self.feedback_labels:
            label.setText("")

    def update_ui(self):
        self.net_worth_label.setText(f"موجودی فعلی: {persian_number(self.net_worth)} سکه")
        self.previous_net_worth_label.setText(f"موجودی قبلی: {persian_number(self.previous_net_worth)} سکه")

    def play(self):
        if not self.timer_running:
            return
        self.timer.stop()
        self.timer_running = False
        selected_deck = self.decks[self.current_position]
        outcome = simulate_outcome(selected_deck)
        self.previous_net_worth = self.net_worth
        self.net_worth += outcome
        
        feedback_text = f"{persian_number(abs(outcome))} {'سود' if outcome > 0 else 'ضرر'}"
        self.feedback_labels[self.current_position].setText(feedback_text)
        self.feedback_labels[self.current_position].setStyleSheet("color: green;" if outcome > 0 else "color: red;")
        
        if not self.is_practice:
            log_data(self.participant_id, self.participant_name, 'main', self.current_trial, self.presented_deck, 'play', outcome, self.net_worth)
        self.update_ui()
        self.wait_for_space()

    def pass_turn(self):
        if not self.timer_running:
            return
        self.timer.stop()
        self.timer_running = False
        self.previous_net_worth = self.net_worth
        self.feedback_labels[self.current_position].setText("گذر")
        self.feedback_labels[self.current_position].setStyleSheet("color: black;")
        if not self.is_practice:
            log_data(self.participant_id, self.participant_name, 'main', self.current_trial, self.presented_deck, 'pass', 0, self.net_worth)
        self.update_ui()
        self.wait_for_space()

    def quit(self):
        if not self.is_practice:
            log_data(self.participant_id, self.participant_name, 'final', 'end', 'none', 'end', 0, self.net_worth)
            try:
                save_data(self.participant_id)
            except Exception as e:
                print(f"Error saving data: {e}")
        
        self.game_ended = True
        self.timer.stop()
        self.clear_layout()
        quit_layout = QVBoxLayout()
        
        final_message = QLabel(f"پایان بازی\n\nپژوهشگران:\n\n Parinaz Khosravani\nparinaz.khosravaani@gmail.com \n\n Farzad Soleimani\nfarzadsoleimani7593@gmail.com")
        final_message.setFont(self.custom_font)
        final_message.setStyleSheet("color: blue;")
        final_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        quit_layout.addWidget(final_message)
        
        net_worth_label = QLabel(f"موجودی نهایی شما: {persian_number(self.net_worth)} سکه")
        net_worth_label.setFont(self.custom_font)
        net_worth_label.setStyleSheet("color: purple;")
        net_worth_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        quit_layout.addWidget(net_worth_label)

        instruction_label = QLabel("برای خروج، لطفاً پنجره را با ماوس ببندید")
        instruction_label.setFont(self.custom_font)
        instruction_label.setStyleSheet("color: red;")
        instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        quit_layout.addWidget(instruction_label)

        self.main_layout.addLayout(quit_layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IGTApp()
    window.show()
    sys.exit(app.exec())  