import json
import os
from config import file_name


# function to load data from the JSON file
def load_data():

    # check whether the file exists
    if not os.path.exists(file_name):
        return []  # if the file does not exist, return an empty list
    try:
        # open the file in 'r' (read) mode
        with open(file_name, 'r') as file:
            content = file.read()
            # if the file has content, convert the JSON string to a Python list
            # if the file is empty, return an empty list
            return json.loads(content) if content else []
    except (json.JSONDecoderError, IOError):
        # if the file is corrupted or reading fails, return an empty list so the program keeps running
        return []


# function to save data to the JSON file
def save_data(data):
    try:
        # open the file in 'w' (write) mode
        with open(file_name, 'w') as file:
            # convert the data from a Python list to a JSON string and write it to the file
            # indent=4 for a tidier format
            json.dump(data, file, indent=4)
    except IOError as e:
        print(f"error saving data: {e}")
