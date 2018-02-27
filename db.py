import os

import pymongo


def get_db():
    client = pymongo.MongoClient(
        os.getenv('MONGO_HOST', '127.0.0.1'),
        int(os.getenv('MONGO_PORT', 27017))
    )
    db = client['slack-dump']
    return db


def get_collections():
    db = get_db()

    user_collection = db['users']
    user_collection.create_index(
        [('id', pymongo.HASHED)], background=True
    )
    user_collection.create_index(
        [('name', pymongo.HASHED)], background=True
    )

    message_collection = db['messages']
    message_collection.create_index(
        [('user', pymongo.HASHED)], background=True
    )
    message_collection.create_index(
        [('channel', pymongo.HASHED)], background=True
    )
    # message_collection.create_index(
    #     [('text', pymongo.TEXT)], default_language='russian', background=True
    # )

    reaction_collection = db['reactions']
    reaction_collection.create_index(
        [('from', pymongo.HASHED)], background=True
    )
    reaction_collection.create_index(
        [('to', pymongo.HASHED)], background=True
    )

    return user_collection, message_collection, reaction_collection
