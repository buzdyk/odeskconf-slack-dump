import pymongo

from db import get_collections


def main():
    print('Started')

    users_collection, messages_collection, reaction_collection = (
        get_collections()
    )

    messages = messages_collection.find({
        'reactions': {'$exists': 1}
    }).sort('_id', pymongo.ASCENDING)

    emoji_documents = []

    for m in messages:
        for r in m['reactions']:
            for u in r['users']:
                emoji_documents.append({
                    'from': u,
                    'to': m['user'] if 'user' in m else None,
                    'channel': m['channel'],
                    'reaction': ':{}:'.format(r['name']),
                    'ts': m['date']
                })

    print(len(emoji_documents))
    reaction_collection.insert_many(emoji_documents)


if __name__ == '__main__':
    main()
