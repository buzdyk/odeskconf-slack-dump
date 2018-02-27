from collections import Counter

import pymongo

from db import get_collections


def main():
    print('Started')

    emojis = Counter()
    total = 0

    users_collection, messages_collection = get_collections()

    messages = messages_collection.find({
        'reactions': {'$exists': 1}
    }).sort('_id', pymongo.ASCENDING)

    for m in messages:
        for r in m['reactions']:
            emojis[r['name']] += r['count']
            total += r['count']

    print('Total reactions: {}'.format(total))
    print('Top 100:')
    for name, count in emojis.most_common(100):
        print(':{}: - {}'.format(name, count))


if __name__ == '__main__':
    main()
