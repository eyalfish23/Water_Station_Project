#!/usr/bin/python
import os
import client_utility


if __name__ == "__main__":
    # Get dir absolute path
    absolute_path = os.path.abspath(__file__)
    current_dir_name = os.path.dirname(absolute_path)
    # Make an instance of client_utility
    c_util = client_utility
    # Get file input from the user
    file_name = c_util.get_input_from_user(current_dir_name)
    file_path = current_dir_name + "/" + file_name

    # Check if file exists
    if c_util.check_if_file_exists(file_path):
        # Create a socket object
        client_socket = c_util.init_connection()
        # Bind to thread , that handle client's sending data
        c_util.thread_handler(client_socket, file_path)

    else:
        print("Error while reading file")
