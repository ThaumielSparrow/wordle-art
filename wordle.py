import requests
import datetime
import json
import os
from typing import List

CACHE_FILE = "answer_cache.json"
WORD_LIST = "guesses.txt"
PATTERN = [[0,0,0,0,0],
           [2,2,2,2,2],
           [2,0,2,0,2],
           [2,2,2,2,2],
           [2,0,2,0,2],
           [2,2,2,2,2]]


def read_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}
    

def write_cache(data):
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        print(f"Error writing to cache: {e}")


def load_word_list():
    """Loads the five-letter word list from the text file."""
    try:
        with open(WORD_LIST, "r") as f:
            words = [line.strip().upper() for line in f]
        return [word for word in words if len(word) == 5]
    except FileNotFoundError:
        print(f"Error: '{WORD_LIST}' not found.")
        return []


def get_todays_answer() -> str:
    """
    Fetches the current day's NYT wordle answer
    """
    today = datetime.date.today().isoformat()
    cache = read_cache()

    if today in cache:
        return cache[today]
    
    try:
        api_url = f"https://www.nytimes.com/svc/wordle/v2/{today}.json"
        response = requests.get(api_url)
        response.raise_for_status()
        
        data = response.json()
        solution = data.get("solution")

        if solution:
            cache[today] = solution
            write_cache(cache)
            return solution
        else:
            print("Failed to find 'solution' key in API response. Has the NYT changed the API response format?")
            return ""

    except requests.exceptions.RequestException as e:
        # Fail silently to allow user to manually enter
        return ""
        

def get_pattern(guess, answer):
    """
    Generates the color pattern for a given guess and answer
    0 - grey
    1 - green
    2 - yellow
    """
    pattern = [0] * 5
    answer_counts = {}
    for letter in answer:
        answer_counts[letter] = answer_counts.get(letter, 0) + 1
    
    # Pass 1 for green letters
    for i in range(5):
        if guess[i] == answer[i]:
            pattern[i] = 1
            answer_counts[guess[i]] -= 1
    
    # Pass 2 for grey/yellow
    for i in range(5):
        if pattern[i] == 0:
            if guess[i] in answer_counts and answer_counts[guess[i]] > 0:
                pattern[i] = 2
                answer_counts[guess[i]] -= 1
    
    return pattern


def find_art_guesses(grid, answer, word_list) -> List[str]:
    guesses = []
    for row_pattern in grid:
        found_word = False
        for word in word_list:
            if get_pattern(word, answer) == row_pattern:
                guesses.append(word)
                found_word = True
                break
        if not found_word:
            guesses.append(None)
    return guesses


def main():
    wordle_answer:str = get_todays_answer()
    
    try:
        with open("guesses.txt", "r") as f:
            word_list = [line.strip().upper() for line in f]
    except FileNotFoundError:
        print("Error: Guesses file not found.")
        print("Please download a valid Wordle guess list and save it as 'guesses.txt'.")
        return

    # Filter for 5-letter words just in case the list has others
    word_list = [word for word in word_list if len(word) == 5]

    if wordle_answer.upper() not in word_list:
        print(f"Warning: The answer '{wordle_answer.upper()}' is not in the provided word list.")

    print("Desired Wordle Grid:")
    for row in PATTERN:
        print(row)
    print(f"\nWordle Answer: {wordle_answer.upper()}")
    print("\nSearching for guess words...")

    result_guesses = find_art_guesses(PATTERN, wordle_answer.upper(), word_list)

    print("\nResulting Guesses:")
    for i, guess in enumerate(result_guesses):
        if guess:
            print(f"Guess {i+1}: {guess}")
        else:
            print(f"Guess {i+1}: No valid word found for this pattern.")


if __name__ == "__main__":
    main()