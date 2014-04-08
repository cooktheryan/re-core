# -*- coding: utf-8 -*-
# Copyright © 2014 SEE AUTHORS FILE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import json
import pika

def parse_config_file(path):
    if os.path.exists(path):
        return json.loads(open(os.path.expanduser(path)).read())
    else:
        raise IOError("Path to config file doesn't exist: %s" % path)

def connect_mq(name=None, password=None, server=None, exchange=None):
    """
    Return channel and connection objects hooked into our message bus

    `name` - Username to connect with
    `password` - Password to authenticate with
    `server` - Hostname of the actual message bus
    `exchange` - Exchange to connect to on the bus

    Returns a 2-tuple of `channel` and `connection` objects
    """
    creds = pika.credentials.PlainCredentials(name, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=str(server),
        credentials=creds))
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange,
                             durable=True,
                             exchange_type='topic')
    return (channel, connection)

def load_json_str(jstr):
    """
    Internalize the json content object (`jstr`) into a native Python
    datastructure and return it.
    """
    return json.loads(str(jstr))

def create_json_str(input_ds, **kwargs):
    """
    Load a native Python datastructure into a json formatted string
    and return it.
    """
    return json.dumps(input_ds, **kwargs)