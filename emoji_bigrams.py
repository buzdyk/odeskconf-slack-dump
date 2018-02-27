from collections import Counter

import pymongo

from db import get_collections


def main():
    print('Started')

    emojis = Counter()

    users_collection, messages_collection = get_collections()

    messages = messages_collection.find({
        'reactions': {'$exists': 1}
    }).sort('_id', pymongo.ASCENDING)

    for m in messages:
        for r1 in m['reactions']:
            for r2 in m['reactions']:
                if r1['name'] == r2['name']:
                    continue

                emojis[tuple(sorted([r1['name'], r2['name']]))] += r1['count'] + r2['count']

    for names, count in emojis.most_common(256):
        print('{} {} - {}'.format(*[':{}:'.format(i) for i in names], count))


if __name__ == '__main__':
    main()
