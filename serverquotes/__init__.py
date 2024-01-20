import os
import sqlite3 
from io import BytesIO, StringIO
from .serverquotes import ServerQuotes
from utils.dataIO import dataIO

PATH = 'data/serverquotes/'
JSON = PATH + 'quotes.json'
SQLDB = PATH + 'quotes.sqlite'
DEFAULT_UPDATE_KEYS = (('quote_id',), ('server_id', 'server_quote_id'))

def check_folder():
    if not os.path.exists(PATH):
        print("Creating serverquotes folder...")
        os.makedirs(PATH)
        
def check_file():
    if dataIO.is_valid_json(JSON):
        print("Migrating quotes.json...")
        data = dataIO.load_json(JSON)
        db = sqlite3.connect(SQLDB)
        rows = []

        db.executescript(INIT_SQL)

        for sid, sdata in data.items():
            for entry in sdata:
                rows.append((sid, entry['added_by'], entry['author_id'], entry['author_name'], entry['text']))
        with db:
            db.executemany("INSERT INTO quotes"
                           "(server_id, added_by, author_id, author_name, quote, date_said, date_added, migrated) "
                           "VALUES (?, ?, ?, ?, ?, NULL, NULL, 1)", rows)

        os.rename(JSON, JSON.replace('.', '_migrated.'))

async def setup(bot):
    check_folder()
    check_file()
    n = ServerQuotes(bot)
    await bot.add_cog(n)