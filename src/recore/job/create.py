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

"""This is where we create new jobs

FSM will get {"group": "$NAME", "playbook_id": "LONG_MONGODB_STRING"}
on the topic of job.create and a reply_to set

it sends a message with {"id": "MONGO_STATE_DOCUMENT"} back to the
reply_to.
"""

import recore.utils
import recore.mongo
import logging


def release(ch, playbook, reply_to, dynamic):
    """`ch` is an open AMQP channel

    `playbook` is the _id of a playbook to begin a release for.
    `reply_to` is a temporary channel
    `dynamic` is a dict storing dynamic input -- default is {}

Reference the playbook name against the database to retrieve a list of
release steps to execute.

We then generate a correlation_id by inserting a new document into the
'state' collection. The correlation_id is equivalent to the
automatically generated '_id' property of this document.

Once we have a state document we are ready to initialize another FSM
instance with that document ID."""
    out = logging.getLogger('recore')
    notify = logging.getLogger('recore.stdout')
    out.debug("Checking mongo for info on playbook %s" % playbook)
    notify.debug(
        "new job submitted from rest for %s. Need to look it up "
        "first in mongo" % playbook)
    mongo_db = recore.mongo.database
    playbook_exists = recore.mongo.lookup_playbook(mongo_db, playbook)

    out.debug("Mongo query to get info on %s finished" % playbook)
    notify.debug("looked up playbook: %s" % playbook)

    if playbook_exists:
        # Initialize state and include the dynamic items
        id = str(recore.mongo.initialize_state(mongo_db, playbook, dynamic))
        out.debug("State created for '%s' in mongo with id: %s" % (playbook, id))
    else:
        out.error("Playbook %s does not exists in mongo" % playbook)
        id = None
        return id

    body = recore.utils.create_json_str({'id': id})

    out.debug("Sending to routing key %s: %s" % (reply_to, body))
    ch.basic_publish(exchange='',
                     routing_key=reply_to,
                     body=body)
    out.info("Emitted message to start new release for %s. Job id: %s" % (
        playbook, str(id)))
    notify.info("Emitted message to start new release for %s. Job id: %s" % (
        playbook, str(id)))
    return id
