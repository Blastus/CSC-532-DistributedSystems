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
import socket

# Public Names
__all__ = (
    'HOSTNAMES',
    'main'
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


def main():
    """Runs a test to verify the ability to establish network connections."""
    hostname = socket.gethostname()
    address = socket.gethostbyname(hostname)
    print(f'I am {hostname}, and my IP address is {address}')
    print('(though no server has been created in this program).')
    assert hostname in HOSTNAMES.values(), 'hostname was not found'
    # Test the ability of getting the IP addresses of other hosts.
    for other_host in sorted(HOSTNAMES.values()):
        if other_host != hostname:
            print(other_host, '->',
                  ipaddress.ip_address(socket.gethostbyname(other_host)))


if __name__ == '__main__':
    main()
