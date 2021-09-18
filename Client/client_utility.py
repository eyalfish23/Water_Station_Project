#!/usr/bin/python
import sys
import os
import re
import socket
import threading
from time import sleep
from pathlib import Path

# Time on which client reads from a text file
INTERVAL_TIME = 5  # In seconds

# This client is based on TCP
PORT_NUMBER = 11000
SERVER_ADDRESS = '127.0.0.1'  # localhost


def get_input_from_user(current_dir_name):
    try:
        # Get station's text file from user
        print("List of available stations:")
        files_list = os.listdir(current_dir_name)
        for file in files_list:
            if re.findall("(.txt)", file):
                print(file)

        file_as_input = input("\nType the name of station file as an input\nIncluding the prefix '.txt':")
        return file_as_input.strip()
    except:
        print("Unexpected error while reading user input:", sys.exc_info()[0])
        sys.exit()


def check_if_file_exists(file_full_path):
    # Check if file exists
    path = Path(file_full_path)
    if path.is_file():
        return True

    return False


def convert_data_from_file_to_string(file_full_path):
    # Read file's data and convert into a string
    try:
        str_file_text = []
        with open(file_full_path, "r+") as file_string_stream:
            for file in file_string_stream:
                str_file_text.append(file.strip())

        return ",".join(str_file_text)
    except:
        print("Error reading from file:", file_full_path)
        sys.exit()


def init_connection():
    try:
        cl_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cl_socket.connect((SERVER_ADDRESS, PORT_NUMBER))
        return cl_socket
    except:
        print("Error while connecting to server:", sys.exc_info()[0])
        sys.exit()


def send_station_data_thread(c_socket, f_path):
    try:
        while True:
            # Read data from file and convert it to string
            message_to_send = convert_data_from_file_to_string(f_path)
            c_socket.send(message_to_send.encode("utf-8"))
            print("Data successfully sent to server")
            # wait some time - until sending again
            sleep(INTERVAL_TIME)
    except:
        print("Error while sending data to server:", sys.exc_info()[0])
        sys.exit()


def thread_handler(cl_socket, f_path):
    try:
        th = threading.Thread(name="Connection thread", target=send_station_data_thread,
                              args=(cl_socket, f_path))
        # Start the thread
        th.start()
        th.join()
    except:
        print("Error while starting a thread:", sys.exc_info()[0])
        sys.exit()
