#  Table "public.filedict"
#   Column     |         Type          | Collation | Nullable | Default
# -------------+-----------------------+-----------+----------+---------
#  key         | character varying(64) |           | not null |
#  fileid      | character varying     |           | not null |
#  filetype    | character varying(10) |           | not null |
#  filecaption | character varying(80) |           |          |
# Indexes:
#     "filedict_pkey" PRIMARY KEY, btree (key)


import psycopg2
import os

create_table = "CREATE TABLE IF NOT EXISTS filedict (key varchar(64) primary key, fileid varchar not null, filetype varchar(10) not null, filecaption varchar(80))"
flag_create_table = os.environ.get('CREATE_TABLE')

# dsn = 'dbname=testdb user=satyam'
dsn = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(dsn)
conn.set_session(autocommit=True)

if flag_create_table == 'true':
    with conn.cursor() as cur:
        cur.execute(create_table)

def push(key: str, fileid: str, filetype: str, caption: str) -> None:
    """
        push fileid to postgres database with key as uuid
    """
    with conn.cursor() as cur:
        cur.executefalse("insert into filedict values (%s, %s, %s)",
                    (key, fileid, filetype))
    return None


def get(key: str):
    """
        get fileid from database based on key
    """
    data = None
    with conn.cursor() as cur:
        cur.execute(
            "SELECT fileid, filetype, caption FROM filedict WHERE key=%s", (key,))
        data = cur.fetchone()
    if data is None:
        raise DataNotFound
    else:
        return data


class DataNotFound(Exception):
    """
    Raised when lookup for data fails
    """
    pass
