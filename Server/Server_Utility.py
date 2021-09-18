#!/usr/bin/python
import socket
import sys
import sqlite3
import datetime
from collections import deque
import threading

# This server is based on TCP
PORT_NUMBER = 11000
SERVER_ADDRESS = '127.0.0.1'  # localhost
DATABASE_FILE = "water-stations.sqlite"

# Connections List
connections_thread_list = []
# Buffer Size
BUFFER_SIZE = 2048
# Message queue
message_queue = deque()


def sql_database_settings():
    try:
        # Create our main table (if not exists)
        query_str = """CREATE TABLE IF NOT EXISTS station_status (
                   station_id INT,
                   last_date TEXT,
                   alarm1 INT,
                   alarm2 INT,
                   PRIMARY KEY(station_id) );"""

        # Execute query
        with sqlite3.connect(DATABASE_FILE) as conn:
            conn.execute(query_str)
    except sqlite3.OperationalError:
        print("Unexpected error while executing Database query:", sys.exc_info()[0])
        sys.exit()
    except:
        print("Unexpected error while connecting to Database:", sys.exc_info()[0])
        sys.exit()


def server_settings():
    try:
        # Create a socket object
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to local address
        server_socket.bind((SERVER_ADDRESS, PORT_NUMBER))
        # Start listening
        server_socket.listen(0)
        print("Listening to port:%s on address:%s" % (PORT_NUMBER, SERVER_ADDRESS))
        return server_socket
    except OSError:
        print("Unexpected error while bind server to address:", sys.exc_info()[0])
        sys.exit()
    except:
        print("Unexpected error while connecting to server:", sys.exc_info()[0])
        sys.exit()


def parse_message(message):
    last_date = datetime.datetime.now().strftime('%Y-%M-%d %H:%m')
    message_splitter = message.split(",")
    get_station_id = message_splitter[0]
    get_alarm1_status = message_splitter[1]
    get_alarm2_status = message_splitter[2]
    # Database update
    sql_database_update_station(get_station_id, last_date, get_alarm1_status, get_alarm2_status)

    if get_alarm1_status == "0":
        get_alarm1_status = "OFF(0)"
    else:
        get_alarm1_status = "ON(1)"
    if get_alarm2_status == "0":
        get_alarm2_status = "OFF(0)"
    else:
        get_alarm2_status = "ON(1)"
    print("""Station Id:%s\tLast date:%s\tAlarm1:%s\tAlarm2:%s""" %
          (get_station_id, last_date, get_alarm1_status, get_alarm2_status))


def sql_database_update_station(station_id, last_date, alarm1_status, alarm2_status):
    try:
        # Update our station# parameters, or insert new row to table in case station_id is not exists
        query_str = """REPLACE INTO station_status(station_id,last_date,alarm1,alarm2)
                    VALUES (?,?,?,?);"""

        # Execute query
        with sqlite3.connect(DATABASE_FILE) as conn:
            conn.execute(query_str, (station_id, last_date, alarm1_status, alarm2_status))

    except sqlite3.OperationalError:
        print("Unexpected error while executing Database query:", sys.exc_info()[0])
        sys.exit()
    except:
        print("Unexpected error while connecting to Database:", sys.exc_info()[0])
        sys.exit()


def read_messages_from_queue():
    try:
        while True:
            # Read pending messages (from queue)
            if message_queue:
                message = message_queue.popleft()
                parse_message(message)
    except:
        print("Error parsing message:", sys.exc_info()[0])
        sys.exit()


def connection_thread(client_connection, client_address):
    try:
        while True:
            message = client_connection.recv(BUFFER_SIZE).decode("utf-8")
            if message:
                # Append message to queue -> to reduce potential cloak (from multiple clients)
                message_queue.append(message)
    except:
        print(client_address + "is no longer sending data")
        try:
            client_connection.close()
            connections_thread_list.remove(client_address)
        except:
            pass


def bind_connection_to_thread(c_client, c_address):
    try:
        th = threading.Thread(name="Connection thread", target=connection_thread, args=(c_client, c_address))
        # Start the thread
        th.start()
    except:
        print("Error while binding connection to thread:", sys.exc_info()[0])
        sys.exit()


def init_message_queue_thread():
    try:
        message_q_th = threading.Thread(name="Message queue thread", target=read_messages_from_queue)
        message_q_th.start()
    except:
        print("Error while starting a thread:", sys.exc_info()[0])
        sys.exit()
