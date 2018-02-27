import os
from datetime import datetime

import simplejson as json

from db import get_collections

DUMP_DIR = './dump/'


def main():
    print('Started')

    users_collection, messages_collection, _ = get_collections()

    print('Uploading users.json')
    with open(os.path.join(DUMP_DIR, 'users.json'), 'rb') as f:
        users = json.load(f)
        users_collection.insert_many(users)

    print('Uploading messages...')
    for channel_name in os.listdir(DUMP_DIR):
        channel_path = os.path.join(DUMP_DIR, channel_name)

        if os.path.isfile(channel_path):
            continue

        print('{} {}'.format(channel_name, '=' * 30))

        for dumpfilename in os.listdir(channel_path):
            print(dumpfilename)

            with open(os.path.join(channel_path, dumpfilename), 'rb') as f:
                channel_messages = json.load(f)

            for message in channel_messages:
                message['channel'] = channel_name
                message['date'] = datetime.fromtimestamp(float(message.pop('ts')))

            messages_collection.insert_many(channel_messages)


if __name__ == '__main__':
    main()
