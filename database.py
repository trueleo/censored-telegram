#   Column     |         Type          | Collation | Nullable | Default
# -------------+-----------------------+-----------+----------+---------
#  key         | character varying(64) |           | not null |
#  fileid      | character varying     |           | not null |
#  filetype    | character varying(10) |           | not null |

import psycopg2
import os

create_table = "CREATE TABLE nokeydb (key varchar(35) not null, fileid varchar(100) not null, filetype varchar(10) not null, filecaption varchar(100));"

drop_table = "drop table nokeydb;"

flag_create_table = os.environ.get('CREATE_TABLE')
flag_drop_table = os.environ.get('DROP_TABLE')

# dsn = 'dbname=testdb user=satyam'
dsn = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(dsn)
conn.set_session(autocommit=True)

if flag_drop_table == 'true':
    with conn.cursor() as cur:
        cur.execute(drop_table)

if flag_create_table == 'true':
    with conn.cursor() as cur:
        cur.execute(create_table)

def push(key: str, file_id: str, file_type: str, file_caption: str):
    """
        push data to postgres database with key as uuid
    """
    with conn.cursor() as cur:
        cur.execute("INSERT INTO nokeydb VALUES (%s, %s, %s, %s)", (key, file_id, file_type, file_caption))


def get(key: str):
    """
        If multiple data found then a list is returned otherwise a tuple is returned for single row of data.
        In case of no data found an empty list is returned.

        returns List( ( file_id, file_type, file_caption ) )
    """
    data = None
    with conn.cursor() as cur:
        cur.execute("SELECT fileid, filetype, filecaption FROM nokeydb WHERE key=%s", (key,))
        data = cur.fetchall()
        if ( type(data) is list and ( len(data) == 1 ) ):
            return data[0]
        else:
            return data
