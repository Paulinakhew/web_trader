#!/usr/bin/env python3

import sqlite3

connection = sqlite3.connect('trade_information.db',check_same_thread=False)
cursor = connection.cursor()

cursor.execute(
    """INSERT INTO current_user(
        username
    ) VALUES(
        '{}'
    );""".format(
        'paulina',
        'opensesame'
    )
)

connection.commit()
cursor.close()
connection.close()
