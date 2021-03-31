#  Table "public.filedict"
#   Column     |         Type          | Collation | Nullable | Default
# -------------+-----------------------+-----------+----------+---------
#  key         | character varying(64) |           | not null |
#  fileid      | character varying     |           | not null |
#  filetype    | character varying(10) |           | not null |
#  filecaption | character varying(80) |           |          |
#  groupid   | character varying(30) |           |          |

import psycopg2
import os

create_table = "CREATE TABLE IF NOT EXISTS nokeydb (key varchar(35) not null, fileid varchar(100) not null, filetype varchar(10), filecaption varchar(100));"
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


def push(key: str, file_id: str, file_type: str, caption: str):
    """
        push file_id to postgres database with key as uuid
    """
    with conn.cursor() as cur:
        cur.execute("insert into nokeydb values (%s, %s, %s, %s)", (key, file_id, file_type, caption))


def get(key: str) -> list:
    """
        get fileid from database based on key

        returns List( ( file_id, file_type, caption ) )
    """
    data = None
    with conn.cursor() as cur:
        cur.execute("SELECT fileid, filetype, caption FROM nokeydb WHERE key=%s", (key,))
        data = cur.fetchall()
        if ( type(data) is list and ( len(data) == 1 ) ):
            return data[0]
        else:
            return data