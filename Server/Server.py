#!/usr/bin/python
import sys
import Server_Utility


# Server Utility that handles all our functions
server_util = Server_Utility

if __name__ == "__main__":
    # Create main DB table (if not exists)
    server_util.sql_database_settings()
    # Binding server to socket
    server_socket = server_util.server_settings()
    # Start message queue thread
    server_util.init_message_queue_thread()

    # Infinite loop = accept connections
    while True:
        a_client, a_address = server_socket.accept()
        print("Got connection from address:%s and port:%s" % (a_address[0], a_address[1]))
        # Bind to thread , that handle client's receive data
        server_util.bind_connection_to_thread(a_client, a_address)
        # Add active thread to the list
        server_util.connections_thread_list.append(a_address[1])
        # Will wait for another connection , on next iteration
