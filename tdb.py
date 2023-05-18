import sqlite3

from uuid import uuid4

def connect():
    return sqlite3.connect("pygatsby.db")

def add_history(session_id, user_query, bot_response):
    session_id = str(session_id)
    conn = connect()
    ensure_table_exists(conn)
    c = conn.cursor()
    user_history_id = str(uuid4())
    bot_history_id = str(uuid4())
    c.execute("""INSERT INTO history (history_id, session_id, user, text, created_at)
                 VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)""",
              (user_history_id, session_id, "user", user_query))
    c.execute("""INSERT INTO history (history_id, session_id, user, text, created_at)
                 VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
              """,
              (bot_history_id, session_id, "bot", bot_response))
    conn.commit()

def ensure_table_exists(conn):
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS sentences (
                   uuid TEXT PRIMARY KEY,
                   text TEXT NOT NULL
                 )
              """)
    c.execute("""CREATE TABLE IF NOT EXISTS history (
                   history_id TEXT PRIMARY KEY,
                   session_id TEXT NOT NULL,
                   user TEXT NOT NULL,
                   text TEXT NOT NULL,
                   created_at TIMESTAMP NOT NULL
                 )
              """)
    conn.commit()

def fetch_history(session_id):
    session_id = str(session_id)
    print(f"fetching history for session_id: {session_id}")
    conn = connect()
    ensure_table_exists(conn)
    c = conn.cursor()
    # NB. everything is backwards in this query since we're trying to load the most recent
    results = c.execute(
        """SELECT user
                , text
           FROM history
           WHERE session_id = ?
           ORDER BY created_at DESC,
             CASE user WHEN 'user' THEN 1 ELSE 0 END
           LIMIT 20
        """, (session_id,))
    result = list(results)
    conn.close()
    return result

def insert(uuid, text):
    conn = connect()
    ensure_table_exists(conn)
    c = conn.cursor()
    c.execute("INSERT INTO sentences (uuid, text) VALUES (?, ?)", (str(uuid), text))
    conn.commit()

def retrieve(uuid):
    conn = connect()
    rows = c.execute("SELECT text FROM sentences WHERE uuid = ?", uuid)
    conn.commit()
    if len(rows) == 0:
        return None
    return rows[0][0]

def retrieve_all(uuids):
    conn = connect()
    c = conn.cursor()
    def wrap(s):
        return f"'{str(s)}'"
    uuid_text = ", ".join(map(wrap, uuids))
    print(f"uuid_text: {uuid_text}")
    query_text = f"""SELECT uuid
                          , text
                     FROM sentences
                     WHERE uuid IN ({uuid_text})"""
    results = c.execute(query_text)
    #print(f"retrieve_all results: {results}")
    result = dict(results)
    #print(f"retrieve_all result: {result}")
    conn.close()
    return result
