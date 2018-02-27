from db import get_db
import csv
from collections import defaultdict

from db import get_db


def main():
    print('Started')

    db = get_db()

    emoji_collection = db['reactions']
    emoji_by_dates = defaultdict(int)

    for emoji in emoji_collection.find():
        emoji_by_dates[(emoji['ts'].date(),)] += 1

    with open('emoji_by_date.csv', 'w') as f:
        csv_writer = csv.writer(f)

        for key, value in emoji_by_dates.items():
            csv_writer.writerow(list(key) + [value])


if __name__ == '__main__':
    main()
