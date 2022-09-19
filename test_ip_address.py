#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# noinspection HttpUrlsUsage
"""Test IP Address.

This program is designed to test the network connection among several virtual
machines running on the same computer. Mapping computer names to IP addresses
should help later on when trying to have connections established between them
for a distributed VM. This is the first step to completing the project my USA
teacher approved for CSC 532, Distributed Systems. What follows is a license:

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>"""

import datetime
import ipaddress
import pickle
import socket
import threading
import time

# Public Names
__all__ = (
    'HOSTNAMES',
    'CLIENT_TO_SERVER',
    'PORT',
    'USER_WAIT',
    'TIMEOUT',
    'SPINLOCK_WAIT',
    'VALUE_LIMIT',
    'main',
    'show_other_host_ip_address',
    'test_server_and_client',
    'get_next_address',
    'AcceptClient'
)

# Module Documentation
__version__ = 1, 0, 0
__date__ = datetime.date(2022, 9, 18)
__author__ = 'Stephen Paul Chappell'
__credits__ = 'CSC-532'

# Symbolic Constants
HOSTNAMES = dict(
    A='zero-Virtual-Machine-A',
    B='zero-Virtual-Machine-B',
    C='zero-Virtual-Machine-C',
    D='zero-Virtual-Machine-D',
    E='zero-Virtual-Machine-E',
    Z='ZERO-FINALE'
)
CLIENT_TO_SERVER = {'Z': 'A', 'A': 'B', 'B': 'C', 'C': 'D', 'D': 'E', 'E': 'Z'}
CLIENT_TO_SERVER = {'Z': 'A', 'A': 'Z'}
PORT = 46656
USER_WAIT = 10
TIMEOUT = 1
SPINLOCK_WAIT = 0.1
VALUE_LIMIT = 1000


def main():
    """Runs a test to verify the ability to establish network connections."""
    hostname = socket.gethostname()
    address = socket.gethostbyname(hostname)
    print(f'I am {hostname}, and my IP address is {address}')
    print('(though no server has been created in this program).')
    assert hostname in HOSTNAMES.values(), 'hostname was not found'
    # show_other_host_ip_address(hostname)
    # test_server_and_client(hostname)
    client, server = create_round_robin_connection()
    print(f'{client = }\n{server = }')
    # Create easy-to-use communication channels.
    read_socket = client.makefile('r')
    write_socket = server.makefile('w')
    load = pickle.Unpickler(read_socket).load
    dump = pickle.Pickler(write_socket, 0).dump
    # Initialize the message passing with a number.
    if hostname == HOSTNAMES['Z']:
        value = 1
        dump(1)
        print(f'DUMP {type(value).__name__} value = {value};')
    # Create a loop for passing messages around the connections.
    while True:
        print(f'{read_socket.read(10) = }')
        value = load()
        print(f'LOAD {type(value).__name__} value = {value};')
        value += 1
        dump(value)
        print(f'DUMP {type(value).__name__} value = {value};')
        if value > VALUE_LIMIT:
            break


def show_other_host_ip_address(hostname):
    """Tests the ability of getting the IP addresses of other hosts."""
    for other_host in sorted(HOSTNAMES.values()):
        if other_host != hostname:
            print(other_host, '->',
                  ipaddress.ip_address(socket.gethostbyname(other_host)))


def test_server_and_client(hostname):
    """Tries to create a server and a client connecting to the next host."""
    server = socket.create_server(('', PORT))
    threading.Thread(target=server.accept, daemon=True).start()
    print('Server created and waiting ...')
    time.sleep(USER_WAIT)
    # noinspection PyTypeChecker
    alias = dict(map(reversed, HOSTNAMES.items()))[hostname]
    next_address = HOSTNAMES[CLIENT_TO_SERVER[alias]], PORT
    next_server = socket.create_connection(next_address, TIMEOUT)
    print('Connected to', next_server, '...')


def create_round_robin_connection():
    """Gets a connection from a client and connects to a server."""
    server = socket.create_server(('', PORT))
    future_client = AcceptClient(server)
    time.sleep(USER_WAIT)
    next_address = get_next_address()
    next_server = socket.create_connection(next_address, TIMEOUT)
    return future_client.client_socket, next_server


def get_next_address():
    """Calculates the address for the next server to connect with."""
    hostname = socket.gethostname()
    # noinspection PyTypeChecker
    alias = dict(map(reversed, HOSTNAMES.items()))[hostname]
    next_address = HOSTNAMES[CLIENT_TO_SERVER[alias]], PORT
    return next_address


class AcceptClient(threading.Thread):
    """Helps with getting a client connection in an asynchronous manner."""

    def __init__(self, server_socket):
        """Initializes the thread in preparation for a client connection."""
        super().__init__(daemon=True)
        self.__server_socket = server_socket
        self.__client_socket = None
        self.__client_address = None
        self.start()

    def run(self):
        """Executes the method for accepting a client connection."""
        server = self.__server_socket
        self.__client_socket, self.__client_address = server.accept()

    @property
    def client_socket(self):
        """Gets a socket representing a client connection."""
        while True:
            client_socket = self.__client_socket
            if client_socket is not None:
                return client_socket
            time.sleep(SPINLOCK_WAIT)

    @property
    def client_address(self):
        """Gets the address for whatever client might be connected."""
        while True:
            client_address = self.__client_address
            if client_address is not None:
                return client_address
            time.sleep(SPINLOCK_WAIT)


if __name__ == '__main__':
    main()
