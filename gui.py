import tkinter as tk
from tkinter import messagebox, font
from tkcalendar import DateEntry
import random

import wordle

from typing import List

class WordleGUI(tk.Tk):
    COLORS = ["#787c7e", "#3cB043", "#ffff00"]
    
    def __init__(self, word=""):
        """
        Initialize the Wordle GUI class
        """
        super().__init__()
        self.title("Wordle Art Generator")
        self.resizable(False, False)

        self.grid_buttons:List[List[tk.Button]] = []
        self.grid_states:List[List[int]] = [[0]*5 for _ in range(6)]
        self.word_list = wordle.load_word_list()

        if not self.word_list:
            messagebox.showerror("Error", f"Could not load word list from '{wordle.WORD_LIST}'.\nMake sure this file exists.")
            self.destroy()
            return
        
        self.create_widgets(word)

    
    def create_widgets(self, word):
        main_frame = tk.Frame(self, padx=10, pady=10)
        main_frame.pack()

        input_frame = tk.Frame(main_frame)
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="Select Date:").pack(side=tk.LEFT, padx=(0,5))
        self.date_picker = DateEntry(input_frame, date_pattern="y-mm-dd", width=12, showweeknumbers=False, showothermonthdays=False)
        self.date_picker.pack(side=tk.LEFT, padx=5)
        fetch_btn = tk.Button(input_frame, text="Fetch", command=self.fetch_word_for_date)
        fetch_btn.pack(side=tk.LEFT, padx=5)

        tk.Label(input_frame, text="Wordle Answer:").pack(side=tk.LEFT, padx=(0,5))
        self.answer_var = tk.StringVar(value="")
        self.answer_entry = tk.Entry(input_frame, textvariable=self.answer_var, width=7, justify="center", font=font.Font(size=14))
        self.answer_entry.pack(side=tk.LEFT)

        grid_frame = tk.Frame(main_frame, bd=2, relief="groove")
        grid_frame.pack(pady=10)

        for r in range(6):
            row_buttons = []
            for c in range(5):
                btn = tk.Button(grid_frame, width=4, height=2, bg=self.COLORS[0], relief="raised")
                btn.bind("<Button-1>", lambda event, row=r, col=c: self.toggle_square(row, col))
                btn.bind("<Button-3>", lambda event, row=r, col=c: self.reset_square(row, col))
                btn.grid(row=r, column=c, padx=2, pady=2)
                row_buttons.append(btn)
            self.grid_buttons.append(row_buttons)

        control_frame = tk.Frame(main_frame)
        control_frame.pack(pady=10)

        generate_btn = tk.Button(control_frame, text="Generate Guesses", command=self.generate_guesses)
        generate_btn.pack(side=tk.LEFT, padx=5)

        reset_btn = tk.Button(control_frame, text="Reset", command=self.reset_interface)
        reset_btn.pack(side=tk.LEFT, padx=5)

        result_frame = tk.Frame(main_frame)
        result_frame.pack(pady=10)

        self.result_text = tk.Text(result_frame, height=6, width=40, state="disabled", font=("Courier", 12))
        self.result_text.pack()

    
    def toggle_square(self, row:int, col:int):
        current_state = self.grid_states[row][col]
        new_state = (current_state + 1) % 3
        self.grid_states[row][col] = new_state
        self.grid_buttons[row][col].config(bg=self.COLORS[new_state])

    
    def reset_square(self, row:int, col:int):
        self.grid_states[row][col] = 0
        self.grid_buttons[row][col].config(bg=self.COLORS[0])

    
    def reset_interface(self):
        self.grid_states = [[0]*5 for _ in range(6)]

        for r in range(6):
            for c in range(5):
                self.grid_buttons[r][c].config(bg=self.COLORS[0])
        
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state="disabled")

    
    def check_early_solve(self):
        for r_index, row in enumerate(self.grid_states):
            if all(state==1 for state in row):
                if r_index < 5:
                    for subseq_row in self.grid_states[r_index+1:]:
                        if any(state!=0 for state in subseq_row):
                            return True
        return False
    

    def generate_guesses(self):
        answer = self.answer_var.get().strip().upper()

        if len(answer)!=5:
            messagebox.showerror("Invalid Input", "Answer must be 5 letters.")
            return

        if answer not in self.word_list:
            messagebox.showwarning("Warning", "Answer not in word list.")
            return

        if self.check_early_solve():
            proceed = messagebox.askyesno("Warning",
                        "You have a row of all green squares before the final guess, but subsequent rows are not empty.\n\n"
                        "This pattern is impossible to achieve in a real Wordle game. Do you want to continue anyways?")
            if not proceed:
                return
        
        found_guesses = wordle.find_art_guesses(self.grid_states, answer, self.word_list)

        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        for i, guess in enumerate(found_guesses):
            self.result_text.insert(tk.END, f"Guess {i+1}: {guess}\n")
        
        self.result_text.config(state="disabled")
        # Shuffle internal word list between guess generations for variety
        random.shuffle(self.word_list)
    

    def fetch_word_for_date(self):
        date_str = self.date_picker.get()
        answer = wordle.get_wordle_answer(date_str)
        if answer:
            self.answer_var.set(answer.upper())
        else:
            self.answer_var.set("")
            messagebox.showwarning("Failure", f"Could not retrieve Wordle answer for date {date_str}.")