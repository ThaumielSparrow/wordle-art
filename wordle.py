import requests
import datetime
import json
import os
import random
from typing import List, Dict

CACHE_FILE = "answer_cache.json"
WORD_LIST = "guesses.txt"

def read_cache() -> Dict[str, str]:
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

def load_word_list() -> List[str]:
    """Loads the five-letter word list from the text file."""
    try:
        with open(WORD_LIST, "r") as f:
            words = [line.strip().upper() for line in f]
        ret = [word for word in words if len(word) == 5]
        # Introduce variability in word list ordering for funsies
        random.shuffle(ret)
        return ret
    
    except FileNotFoundError:
        print(f"Error: '{WORD_LIST}' not found.")
        return []

def get_wordle_answer(date_str:str) -> str:
    """
    Fetches a specific day's NYT wordle answer
    """
    cache = read_cache()

    if date_str in cache:
        return cache[date_str]
    
    try:
        api_url = f"https://www.nytimes.com/svc/wordle/v2/{date_str}.json"
        response = requests.get(api_url)
        response.raise_for_status()
        
        data = response.json()
        solution = data.get("solution")

        if solution:
            cache[date_str] = solution
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
