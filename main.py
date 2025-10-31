import gui
import wordle

if __name__ == "__main__":
    todays_word = wordle.get_todays_answer()
    app = gui.WordleGUI(todays_word)

    app.mainloop()