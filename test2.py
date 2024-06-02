import string
import logging
import argparse
from collections import Counter

from utils import setup_logging
from telegram.client import Telegram


"""
Prints most popular words in the chat.

Usage:
    python examples/chat_stats.py api_id api_hash phone chat_id --limit 500
"""


def retreive_messages(telegram, chat_id, receive_limit):
    receive = True
    from_message_id = 0
    stats_data = {}

    while receive:
        response = telegram.get_chat_history(
            chat_id=chat_id,
            limit=1000,
            from_message_id=from_message_id,
        )
        response.wait()

        for message in response.update['messages']:
            if message['content']['@type'] == 'messageText':
                stats_data[message['id']] = message['content']['text']['text']
            from_message_id = message['id']

        total_messages = len(stats_data)
        if total_messages > receive_limit or not response.update['total_count']:
            receive = False

        print(f'[{total_messages}/{receive_limit}] received')

    return stats_data


def print_stats(stats_data, most_common_count):
    words = Counter()
    translator = str.maketrans('', '', string.punctuation)
    for _, message in stats_data.items():
        for word in message.split(' '):
            word = word.translate(translator).lower()
            if len(word) > 3:
                words[word] += 1

    for word, count in words.most_common(most_common_count):
        print(f'{word}: {count}')


if __name__ == '__main__':
    setup_logging(level=logging.INFO)

    tg = Telegram(
        api_id=26808455,
        api_hash="784b6198c9cc5c8218b5642cfa8540df",
        phone='+14708002362',
        database_encryption_key='changeme1234',
    )
    # you must call login method before others
    tg.login()

    stats_data = retreive_messages(
        telegram=tg,
        chat_id=args.chat_id,
        receive_limit=20,
    )

    print_stats(
        stats_data=stats_data,
        most_common_count=20,
    )

    tg.stop()