import sqlite3

DB_PATH = './lolnotifier.db'
SUMMONER = 'labìsica'

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("UPDATE users SET last_match_id = NULL WHERE summoner_name = ?", (SUMMONER,))
conn.commit()
conn.close()
print(f"last_match_id for {SUMMONER} set to NULL.")
