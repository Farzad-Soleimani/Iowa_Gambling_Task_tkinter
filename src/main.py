import random
import pandas as pd
import os
from tkinter import Tk, Label, Button, Frame, Entry, messagebox, PhotoImage, font
from PIL import Image, ImageTk
import arabic_reshaper
from bidi.algorithm import get_display

# Deck configurations
conditions = {
    'deck_a': {'Reward': 100, 'Penalty': -250},
    'deck_b': {'Reward': 100, 'Penalty': -1150},
    'deck_c': {'Reward': 50, 'Penalty': -25},
    'deck_d': {'Reward': 50, 'Penalty': -200},
}

# Initialize variables
net_worth = 2000
previous_net_worth = net_worth
current_position = 0  # Arrow starts at Deck A
decks = ['deck_a', 'deck_b', 'deck_c', 'deck_d']
trial_data = []  # Stores trial data for Excel output
timeout_duration = 4  # Seconds to timeout
total_trials = 20
current_trial = 0
practice_trials = 10  # Number of practice trials

# Function to convert numbers to Persian numerals
def persian_number(number):
    persian_digits = {
        '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
        '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
    }
    # Handle negative numbers
    if isinstance(number, int) or isinstance(number, float):
        number_str = str(abs(number))  # Convert to absolute value first
        persian_num = ''.join(persian_digits[digit] for digit in number_str)
        if number < 0:
            return f"-{persian_num}"  # Add negative sign if necessary
        return persian_num
    return number  # Return as-is if not a number

# Function to log data to Excel
def log_data(participant_id, participant_name, trial_type, choice, outcome, net_worth):
    trial_data.append({
        'Participant ID': participant_id,
        'Participant Name': participant_name,
        'Trial Type': trial_type,
        'Choice': choice,
        'Outcome': persian_number(outcome) if outcome != 0 else "0",  # Record $0 payoff as "0"
        'Net Worth': persian_number(net_worth),
    })

# Function to save data to Excel
def save_data(participant_id):
    try:
        # Create an output directory if it doesn't exist
        output_dir = "Iowa_Gambling_Task_tkinter/output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Save the Excel file in the output directory
        df = pd.DataFrame(trial_data)
        output_file = os.path.join(output_dir, f"Participant_{participant_id}.xlsx")
        df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"Data saved to {output_file}")  # Debug statement
    except Exception as e:
        print(f"Error saving data: {e}")  # Debug statement

# Function to simulate deck outcome based on probabilities
def simulate_outcome(deck):
    if deck == 'deck_a':
        # Deck A: 50% gain, 50% loss, 0% $0 payoff
        if random.random() < 0.50:
            return 100  # Gain
        else:
            return -250  # Loss
    elif deck == 'deck_b':
        # Deck B: 90% gain, 10% loss, 0% $0 payoff
        if random.random() < 0.90:
            return 100  # Gain
        else:
            return -1150  # Loss
    elif deck == 'deck_c':
        # Deck C: 50% gain, 25% loss, 25% $0 payoff
        rand = random.random()
        if rand < 0.50:
            return 50  # Gain
        elif rand < 0.75:
            return -25  # Loss
        else:
            return 0  # $0 payoff
    elif deck == 'deck_d':
        # Deck D: 90% gain, 10% loss, 0% $0 payoff
        if random.random() < 0.90:
            return 50  # Gain
        else:
            return -200  # Loss
    else:
        return 0  # Default case (should not occur)

# Function to reshape and display Persian text
def persian_text(text):
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)

# GUI Application
class IGTApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Iowa Gambling Task")
        self.root.geometry("1920x1200")
        self.root.configure(bg="#f0f0f0")

        self.custom_font = font.Font(family="B Koodak", size=40)
        self.net_worth = net_worth
        self.previous_net_worth = previous_net_worth
        self.current_position = current_position
        self.decks = decks
        self.trial_data = trial_data
        self.current_trial = current_trial
        self.participant_id = ""
        self.participant_name = ""
        self.timer_running = False
        self.space_enabled = False
        self.timer_id = None  # Store the timer ID to cancel it if needed
        self.is_practice = True  # Flag to indicate if it's a practice trial

        # Load deck images
        self.deck_images = []
        for deck in self.decks:
            img = Image.open(f"Iowa_Gambling_Task_tkinter/images/{deck}.png")
            img = img.resize((200, 300), Image.Resampling.LANCZOS)
            self.deck_images.append(ImageTk.PhotoImage(img))

        # Load arrow image
        self.arrow_img = Image.open("Iowa_Gambling_Task_tkinter/images/arrow.png")
        self.arrow_img = self.arrow_img.resize((100, 100), Image.Resampling.LANCZOS)
        self.arrow_img = ImageTk.PhotoImage(self.arrow_img)

        # Load F and J key images
        self.f_key_img = Image.open("Iowa_Gambling_Task_tkinter/images/f_key.png")
        self.f_key_img = self.f_key_img.resize((100, 100), Image.Resampling.LANCZOS)
        self.f_key_img = ImageTk.PhotoImage(self.f_key_img)

        self.j_key_img = Image.open("Iowa_Gambling_Task_tkinter/images/j_key.png")
        self.j_key_img = self.j_key_img.resize((100, 100), Image.Resampling.LANCZOS)
        self.j_key_img = ImageTk.PhotoImage(self.j_key_img)

        # Start with the registration page
        self.register_page()

    def register_page(self):
        self.clear_frame()
        Label(self.root, text=persian_text("ثبت اطلاعات"), font=self.custom_font, fg="blue", bg="#f0f0f0").pack(pady=100)
        Label(self.root, text=persian_text("نام و شناسه خود را وارد کنید:"), font=self.custom_font, bg="#f0f0f0").pack(pady=20)

        self.name_entry = Entry(self.root, font=self.custom_font, justify="right")
        self.name_entry.pack(pady=10)

        self.id_entry = Entry(self.root, font=self.custom_font, justify="right")
        self.id_entry.pack(pady=10)

        Button(self.root, text=persian_text("شروع"), command=self.start_task, font=self.custom_font, bg="green", fg="white").pack(pady=20)

    def start_task(self):
        self.participant_name = self.name_entry.get()
        self.participant_id = self.id_entry.get()
        if not self.participant_name or not self.participant_id:
            messagebox.showwarning(persian_text("خطای ورودی"), persian_text("لطفاً نام و شناسه خود را وارد کنید."))
            return
        self.show_welcome_page()

    def show_welcome_page(self):
        self.clear_frame()
        Label(self.root, text=persian_text("در این بازی هدف شما این است که تا حد ممکن پول برنده شوید!"), font=self.custom_font, fg="blue", bg="#f0f0f0").pack(pady=50)
        Label(self.root, text=persian_text("برای هر دور یک فلش زرد رنگ بالای یکی از چهار دسته کارت نشان داده خواهد شد"), font=self.custom_font, bg="#f0f0f0").pack(pady=10)
        Label(self.root, text=persian_text("به واسطه آن، میتوانید بین بازی کردن یا رد کردن آن کارت تصمیم بگیرید."), font=self.custom_font, bg="#f0f0f0").pack(pady=10)
        Label(self.root, text=persian_text("اگر بازی کنید؛ ممکن است سکه برنده شوید و یا از دست بدهید"), font=self.custom_font, bg="#f0f0f0").pack(pady=20)
        Label(self.root, text=persian_text("(و یا نه سکه ببرید و نه از دست بدهید)"), font=self.custom_font, bg="#f0f0f0").pack(pady=20)
        Label(self.root, text=persian_text("اگر رد شوید؛ نه سکه می‌برید و نه چیزی از دست خواهید داد."), font=self.custom_font, bg="#f0f0f0").pack(pady=20)
        Label(self.root, text=persian_text("توجه کنید که در هر نوبت فقط 4 ثانیه زمان دارید تا تصمیم بگیرید"), font=self.custom_font, fg='red', bg="#f0f0f0").pack(pady=20)
        Label(self.root, text=persian_text("با 2000 سکه شروع خواهید کرد."), font=self.custom_font,fg='black', bg="#f0f0f0").pack(pady=20)
        Label(self.root, text=persian_text("برای ادامه کلید space را فشار دهید."), font=self.custom_font, fg="green", bg="#f0f0f0").pack(pady=50)
        self.root.bind('<space>', lambda event: self.show_practice_instructions())

    def show_practice_instructions(self):
        self.clear_frame()
        Label(self.root, text=persian_text("پیش از آغاز بازی اصلی، به بازی تمرینی خواهید پرداخت"), font=self.custom_font, fg="blue", bg="#f0f0f0").pack(pady=50)
        Label(self.root, text=persian_text("این مرحله در چند تکرار انجام خواهد شد و فقط جهت آشنایی شما"), font=self.custom_font, bg="#f0f0f0").pack(pady=10)
        Label(self.root, text=persian_text("با ساختار و نحوه انجام بازی است."), font=self.custom_font, bg="#f0f0f0").pack(pady=10)
        Label(self.root, text=persian_text("لذا نتایج این مرحله ثبت نخواهد شد"), font=self.custom_font, bg="#f0f0f0").pack(pady=20)
        Label(self.root, text=persian_text("برای ادامه کلید space را فشار دهید."), font=self.custom_font, fg="green", bg="#f0f0f0").pack(pady=50)
        self.root.bind('<space>', lambda event: self.practice_game())

    def practice_game(self):
        self.is_practice = True
        self.current_trial = 0
        self.main_task()

    def show_transition_to_main_game(self):
        self.clear_frame()
        Label(self.root, text=persian_text("پایان مرحله تمرینی"), font=self.custom_font, fg="blue", bg="#f0f0f0").pack(pady=50)
        Label(self.root, text=persian_text("اکنون به بازی اصلی میپردازید."), font=self.custom_font, bg="#f0f0f0").pack(pady=20)
        Label(self.root, text=persian_text("در این مرحله پاسخ های شما ثبت خواهد شد و در پایان"), font=self.custom_font, bg="#f0f0f0").pack(pady=10)
        Label(self.root, text=persian_text("نتیجه نهایی خود را مشاهده خواهید کرد."), font=self.custom_font, bg="#f0f0f0").pack(pady=10)
        Label(self.root, text=persian_text("موفق باشید."), font=self.custom_font, bg="#f0f0f0").pack(pady=20)
        Label(self.root, text=persian_text("برای ادامه کلید space را فشار دهید."), font=self.custom_font, fg="green", bg="#f0f0f0").pack(pady=50)
        self.root.bind('<space>', lambda event: self.start_main_game())

    def start_main_game(self):
        self.is_practice = False
        self.current_trial = 0
        self.net_worth = 2000  # Reset net_worth to 2000 for the main task
        self.previous_net_worth = 2000  # Reset previous_net_worth as well
        self.main_task()

    def main_task(self):
        self.clear_frame()
        self.net_worth_label = Label(self.root, text=persian_text(f"موجودی فعلی: {persian_number(self.net_worth)} سکه"), font=self.custom_font, fg="purple", bg="#f0f0f0")
        self.net_worth_label.pack(pady=20)

        self.previous_net_worth_label = Label(self.root, text=persian_text(f"موجودی قبلی: {persian_number(self.previous_net_worth)} سکه"), font=self.custom_font, fg="orange", bg="#f0f0f0")
        self.previous_net_worth_label.pack(pady=20)

        self.deck_frame = Frame(self.root, bg="#f0f0f0")
        self.deck_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.deck_labels = []
        self.feedback_labels = []
        for i, deck in enumerate(self.decks):
            label = Label(self.deck_frame, image=self.deck_images[i], bg="#f0f0f0")
            label.grid(row=1, column=i, padx=30)  # Equal horizontal spacing between decks
            self.deck_labels.append(label)

            feedback_label = Label(self.deck_frame, text="", font=self.custom_font, bg="#f0f0f0", justify="right")
            feedback_label.grid(row=2, column=i, padx=30)
            self.feedback_labels.append(feedback_label)

        self.arrow_label = Label(self.deck_frame, image=self.arrow_img, bg="#f0f0f0")
        self.arrow_label.grid(row=0, column=self.current_position, padx=30, pady=30)

        # Add F and J key images with text, closer together and positioned lower
        self.f_key_label = Label(self.deck_frame, image=self.f_key_img, bg="#f0f0f0")
        self.f_key_label.grid(row=3, column=0, padx=10, pady=20)  # Reduced padding and moved lower
        Label(self.deck_frame, text=persian_text("برای بازی کردن"), font=self.custom_font, bg="#f0f0f0").grid(row=4, column=0, padx=10, pady=5)  # Reduced padding

        self.j_key_label = Label(self.deck_frame, image=self.j_key_img, bg="#f0f0f0")
        self.j_key_label.grid(row=3, column=3, padx=10, pady=20)  # Reduced padding and moved lower
        Label(self.deck_frame, text=persian_text("برای گذر کردن"), font=self.custom_font, bg="#f0f0f0").grid(row=4, column=3, padx=10, pady=5)  # Reduced padding

        # Bind keys for play, pass, and quit
        self.root.bind('<f>', lambda event: self.play())
        self.root.bind('<j>', lambda event: self.pass_turn())
        self.root.bind('<q>', lambda event: self.quit())

        # Start the first trial
        self.start_trial()

    def start_trial(self):
        if self.is_practice and self.current_trial >= practice_trials:
            self.show_transition_to_main_game()
            return
        elif not self.is_practice and self.current_trial >= total_trials:
            self.quit()
            return
        self.current_trial += 1
        self.timer_running = True
        self.space_enabled = False
        # Start the timer and store its ID
        self.timer_id = self.root.after(timeout_duration * 1000, self.timeout)  # Fixed: No parentheses!

    def timeout(self):
        if self.timer_running:  # Only proceed if the timer is still running
            print("Timeout triggered")  # Debug statement
            self.timer_running = False
            self.previous_net_worth = self.net_worth
            self.feedback_labels[self.current_position].config(text=persian_text("گذر"), fg="black")
            if not self.is_practice:
                log_data(self.participant_id, self.participant_name, 'main', 'pass', 0, self.net_worth)
            self.update_ui()
            self.wait_for_space()

    def wait_for_space(self):
        self.space_enabled = True
        self.space_label = Label(self.root, text=persian_text("برای ادامه فاصله (Space) را بزنید"), font=self.custom_font, fg="blue", bg="#f0f0f0")
        self.space_label.pack(pady=20)
        self.root.bind('<space>', lambda event: self.continue_trial())

    def continue_trial(self):
        if not self.space_enabled:
            return
        print("Continuing to next trial")  # Debug statement
        self.space_enabled = False
        self.space_label.destroy()
        self.clear_feedback()
        self.current_position = random.randint(0, len(self.decks) - 1)
        self.arrow_label.grid(row=0, column=self.current_position, padx=30, pady=30)
        self.start_trial()

    def clear_feedback(self):
        for feedback_label in self.feedback_labels:
            feedback_label.config(text="")

    def update_ui(self):
        self.net_worth_label.config(text=persian_text(f"موجودی فعلی: {persian_number(self.net_worth)} سکه"))
        self.previous_net_worth_label.config(text=persian_text(f"موجودی قبلی: {persian_number(self.previous_net_worth)} سکه"))

    def play(self):
        if not self.timer_running:
            return
        # Cancel the timer if the participant responds before the timeout
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.timer_running = False
        selected_deck = self.decks[self.current_position]
        outcome = simulate_outcome(selected_deck)
        self.previous_net_worth = self.net_worth
        self.net_worth += outcome
        feedback = persian_text(f"{persian_number(abs(outcome))} {'سود' if outcome > 0 else 'ضرر'}")
        self.feedback_labels[self.current_position].config(text=feedback, fg="green" if outcome > 0 else "red")
        # Log data for every trial, including $0 payoff
        if not self.is_practice:
            log_data(self.participant_id, self.participant_name, 'main', selected_deck, outcome, self.net_worth)
        self.update_ui()
        self.wait_for_space()

    def pass_turn(self):
        if not self.timer_running:
            return
        # Cancel the timer if the participant responds before the timeout
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.timer_running = False
        self.previous_net_worth = self.net_worth
        self.feedback_labels[self.current_position].config(text=persian_text("گذر"), fg="black")
        if not self.is_practice:
            log_data(self.participant_id, self.participant_name, 'main', 'pass', 0, self.net_worth)
        self.update_ui()
        self.wait_for_space()

    def quit(self):
        # Save the final result to the data
        if not self.is_practice:
            log_data(self.participant_id, self.participant_name, 'final', 'end', 0, self.net_worth)
            save_data(self.participant_id)  # Save data to Excel
        self.clear_frame()
        Label(self.root, text=persian_text(f"پایان بازی\n\nپژوهشگران:\n\n Parinaz Khosravani\nparinaz.khosravaani@gmail.com \n\n Farzad Soleimani\nfarzadsoleimani7593@gmail.com"), font=self.custom_font, fg="blue", bg="#f0f0f0").pack(pady=100)
        Label(self.root, text=persian_text(f"موجودی نهایی شما: {persian_number(self.net_worth)} سکه"), font=self.custom_font, fg="purple", bg="#f0f0f0").pack(pady=20)
        Button(self.root, text=persian_text("خروج"), command=self.root.destroy, font=self.custom_font, bg="gray", fg="white").pack(pady=20)

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

# Run the application
if __name__ == "__main__":
    root = Tk()
    app = IGTApp(root)
    root.mainloop()