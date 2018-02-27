import random
import re
from datetime import datetime

import markovify
from flask import Flask, request, render_template

from db import get_collections

app = Flask(__name__)
app.jinja_env.globals['random'] = random


@app.route('/')
def homepage():
    username = request.args.get('username')

    if not username:
        return render_template('index.html')

    user_collection, message_collection, reaction_collection = get_collections()

    user_id = user_collection.find_one({'name': username}, {'id': 1})

    if not user_id:
        return render_template('index.html', ok=False, no_user=True)

    user_id = user_id['id']

    total_messages = message_collection.find().count()
    messages_count = message_collection.find({'user': user_id}).count()
    put_emoji_count = reaction_collection.find({'from': user_id}).count()
    got_emoji_count = reaction_collection.find({'to': user_id}).count()

    messages_by_date = message_collection.aggregate([
        {'$match': {'user': user_id}},
        {'$group': {
            '_id': {
                'year': {'$year': "$date"},
                'month': {'$month': "$date"},
                'day': {'$dayOfMonth': "$date"}
            },
            'count': {'$sum': 1}
        }}
    ])
    messages_by_date = [
        {
            'Date': datetime(
                i['_id']['year'],
                i['_id']['month'],
                i['_id']['day']
            ).isoformat(),
            'Count': i['count']}
        for i in messages_by_date
    ]

    channels = message_collection.aggregate([
        {'$match': {'user': user_id}},
        {'$group': {'_id': '$channel', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ])
    channels = [
        {'Channel': i['_id'], 'Count': i['count']}
        for i in channels
    ]

    put_emoji = reaction_collection.aggregate([
        {'$match': {'from': user_id}},
        {'$group': {'_id': '$reaction', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': 50}
    ])

    got_emoji = reaction_collection.aggregate([
        {'$match': {'to': user_id}},
        {'$group': {'_id': '$reaction', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': 50}
    ])

    return render_template(
        'index.html',
        ok=True,
        total_messages=total_messages,
        messages_count=messages_count,
        put_emoji_count=put_emoji_count,
        got_emoji_count=got_emoji_count,
        messages_by_date=messages_by_date,
        channels=channels,
        put_emoji=put_emoji,
        got_emoji=got_emoji
    )


@app.route('/talklike_v1')
def talklike_v1():
    user_collection, message_collection, reaction_collection = get_collections()

    f = {
        'subtype': None,
        'channel': {'$ne': 'upwork'}
    }

    username = request.args.get('username') or '42'

    if username:
        user_id = user_collection.find_one({'name': username}, {'id': 1})

        if not user_id:
            return 'hmm'

        f['user'] = user_id['id']

        query = request.args.get('query')
        if query:
            f['text'] = re.compile(re.escape(query), re.IGNORECASE)

    messages = message_collection.find(f)

    def messages_iter():
        for i in messages:
            text = i['text']

            if 'http' in text:
                continue

            text = re.sub(r'(^[A-Za-z0-9\.\-]+:? |<[@#].*?>|\_)', '', text)

            yield '\n'.join(
                l for l in text.split('\n') if not l.startswith('&gt;')
            )

    try:
        text_model = markovify.Text(messages_iter())
    except:
        return render_template('talklike.html')

    sentences = set()

    for i in range(25):
        sentence = text_model.make_sentence()
        if sentence:
            sentences.add(sentence)

    return render_template('talklike.html', sentences=sentences)


RE_CLEAR_MESSAGE = re.compile(
    r'('
    r'^\s+|'  # spaces before text
    r'\s+$|'  # spaces after text
    r'^[a-z0-9\.\-]+:? |'  # metion like "doge: oh, hi doggie"
    r'\s*?<.+>|'  # channel/user metions like @doge
    r'^\s*?&gt;.*?$|'  # quotes
    r'[\_\~\*]|'  # markdown
    r'`.*?`|'  # code
    r'^\s*?:.+:\s*?$'  # only-emoji messages like ":doge: "
    r')',
    re.IGNORECASE | re.MULTILINE
)
RE_WORD_SPLIT = re.compile(r'\s+')


@app.route('/talklike')
def talklike():
    user_collection, message_collection, reaction_collection = get_collections()

    f = {
        'subtype': None,
        'channel': {'$ne': 'upwork'}
    }

    username = request.args.get('username') or '42'

    if username:
        user_id = user_collection.find_one({'name': username}, {'id': 1})

        if not user_id:
            return 'hmm'

        f['user'] = user_id['id']

        query = request.args.get('query')
        if query:
            f['text'] = re.compile(re.escape(query), re.IGNORECASE)

    messages = message_collection.find(f)

    def messages_iter():
        for i in messages:
            text = i['text'].lower()

            if 'http' in text:
                continue

            text = RE_CLEAR_MESSAGE.sub('', text)

            yield '\n'.join(l for l in text.split('\n') if len(l) > 2)

    messages_list = list(messages_iter())

    corpus = '\n'.join(messages_list)
    sentences = list(
        re.split(RE_WORD_SPLIT, i)
        for i in messages_list if len(i) > 2
    )

    try:
        text_model = markovify.Text(
            None, parsed_sentences=sentences
        )
    except:
        return render_template('talklike.html')

    sentences = set()

    for i in range(25):
        sentence = text_model.make_sentence()

        if sentence and sentence not in corpus:
            sentences.add(sentence)

    return render_template('talklike.html', sentences=sentences)


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run('127.0.0.1', 13023, debug=True)
