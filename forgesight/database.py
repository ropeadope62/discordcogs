import aiosqlite

class Forgesight_DB_Manager:
    def __init__(self, db_path, logger=None):
        self.db = db_path
        self.logger = logger
    async def __aenter__(self):
        self.db = await aiosqlite.connect('forgesight.db')
        return self.db

    async def __aexit__(self, exc_type, exc, tb):
        await self.db.close()

    async def initialize_db(self,):
        async with aiosqlite.connect('forgesight.db') as db:
            if self.logger:
                self.logger.info('Initialize: Connected to database.')
            
            # Corrected SQL for creating the config table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS config (
                    guild_id TEXT PRIMARY KEY,
                    min_message_requirement INTEGER DEFAULT 1,
                    min_message_length INTEGER DEFAULT 5, 
                    reward_timeout INTEGER DEFAULT 5,
                    base_gold INTEGER DEFAULT 1,
                    streak_bonus INTEGER DEFAULT 1,
                    media_bonus INTEGER DEFAULT 1,
                    subscriber_role_id INTEGER,
                    allowed_channels TEXT,
                    subscriber_bonus INTEGER DEFAULT 1,
                    omit_rewards_ids TEXT, 
                    rewards_enabled INTEGER DEFAULT 1,
                    channel_id_restriction INTEGER DEFAULT 0
                )
            ''')
            self.logger.info('Config Table: Created.')
            
            # Corrected SQL for creating the user_data table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_data (
                    user_id TEXT PRIMARY KEY,
                    gold INTEGER DEFAULT 0, 
                    last_earned REAL,
                    consecutive_days INTEGER DEFAULT 0, 
                    last_post_date TEXT, 
                    media_bonuses INTEGER DEFAULT 0,
                    streak_bonuses INTEGER DEFAULT 0,
                    msg_avg_length INTEGER DEFAULT 0,
                    total_msg_count INTEGER DEFAULT 0
                )
            ''')
            self.logger.info('User Data Table: Created.')

            # Corrected SQL for creating the transaction_log table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS transaction_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    user_id TEXT,
                    total_gold_earned INTEGER,
                    channel_id TEXT,
                    base_gold INTEGER DEFAULT 0,
                    streak_bonus INTEGER DEFAULT 0,
                    media_bonus INTEGER DEFAULT 0,
                    subscriber_bonus INTEGER DEFAULT 0,
                    message_length INTEGER DEFAULT 0
                )
            ''')
            self.logger.info('Transaction Log Table: Created.')

            # Corrected SQL for creating the gold_stats table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS gold_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    total_gold INTEGER,
                    gold_earned_per_hour INTEGER,
                    users_earned_gold INTEGER
                )
            ''')
            self.logger.info('Gold Stats Table: Created.')

            await db.commit()

    async def update_config_value(self, key, value):
        async with aiosqlite.connect('forgesight.db') as db:
            try:
                await db.execute('UPDATE config SET value = ? WHERE key = ?', (value, key))
            except Exception as e:
                self.logger.error(f'Error updating config value: {e}')
            await db.commit()

    async def load_config(self, guild_id):
        async with self as db:
            async with db.execute('SELECT * FROM config WHERE guild_id = ?', (guild_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    print(f"No config found for guild_id: {guild_id}")
                    return {}

                config_keys = [
                    'guild_id', 'min_message_requirement', 'min_message_length', 'reward_timeout', 'base_gold', 'streak_bonus', 
                    'media_bonus', 'subscriber_role_id', 'allowed_channels', 'subscriber_bonus', 'omit_rewards_ids', 
                    'rewards_enabled', 'channel_id_restriction'
                ]
                return dict(zip(config_keys, row))

    async def save_config(self, key, value):
        async with aiosqlite.connect('forgesight.db') as db:
            await db.execute('REPLACE INTO config (key, value) VALUES (?, ?)', (key, value))
            self.logger.info(f'Ran SQL Query REPLACE INTO config (key, value) VALUES (?, ?), (key, value). Updated config value: {key} = {value}')
            await db.commit()

    async def load_vault_data(self, user_id, user_name):
        print(f"Loading vault data for user_id: {user_id}")
        
        async with self as db:
            async with db.execute('SELECT * FROM user_data WHERE user_id = ?', (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None: 
                    print(f"No vault data found for user_id: {user_id}")
                    await self.create_new_user(user_id, user_name, gold=0, last_earned=0, last_post_date=None, consecutive_days=0, media_bonuses=0, streak_bonuses=0, msg_avg_length=0, total_msg_count=0, total_msg_length=0)  
                    print(f'Created new user {user_name}, {user_id} with 0 gold.')
                    return {}

                user_data_keys = ['user_id','user_name', 'gold', 'last_earned', 'last_post_date', 'consecutive_days', 'media_bonuses', 'streak_bonuses', 'msg_avg_length', 'total_msg_count','total_msg_length']
                return dict(zip(user_data_keys, row))
            
    async def load_vault_data_from_id(self, user_id):
        print(f"Loading vault data for user_id: {user_id}")
        
        async with self as db:
            async with db.execute('SELECT * FROM user_data WHERE user_id = ?', (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None: 
                    print(f"No vault data found for user_id: {user_id}")
                    return {}
                user_data_keys = ['user_id','user_name', 'gold', 'last_earned', 'last_post_date', 'consecutive_days', 'media_bonuses', 'streak_bonuses', 'msg_avg_length', 'total_msg_count','total_msg_length']
                return dict(zip(user_data_keys, row))

    async def load_all_vault_data(self):
        try:
            async with self as db: 
                async with db.execute('SELECT * FROM user_data') as cursor:
                    rows = await cursor.fetchall()

                    if not rows:
                        return []
                    user_data_keys = ['user_id', 'gold', 'last_earned', 'last_post_date', 'consecutive_days', 'media_bonuses', 'streak_bonuses', 'msg_avg_length', 'total_msg_count', 'total_msg_length']
                    return [dict(zip(user_data_keys, row)) for row in rows]

        except Exception as e:
            print(f"Error loading all vault data: {e}")
            return []

    async def save_vault_data(self, user_id, user_name, gold, last_earned, consecutive_days, last_post_date, media_bonuses, streak_bonuses, msg_avg_length, total_msg_count, total_msg_length):
        try:
            print('Connecting to database to save vault data')  # Debug Print
            async with aiosqlite.connect('forgesight.db') as db:
                print('Connected to database, executing REPLACE INTO')  # Debug Print
                await db.execute('''
                    REPLACE INTO user_data (user_id, user_name, gold, last_earned, consecutive_days, last_post_date, media_bonuses, streak_bonuses, msg_avg_length, total_msg_count, total_msg_length)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, user_name, gold, last_earned, consecutive_days, last_post_date, media_bonuses, streak_bonuses, msg_avg_length, total_msg_count, total_msg_length))
                await db.commit()
                print('Vault data saved successfully')  # Debug Print
        except Exception as e:
            print(f"Error in save_vault_data: {e}")
            raise
        

    async def log_transaction(self, timestamp, user_id, total_gold_earned, channel_id, base_gold, streak_bonus, media_bonus, subscriber_bonus, message_length):
        async with aiosqlite.connect('forgesight.db') as db:
            await db.execute('''
                INSERT INTO transaction_log (timestamp, user_id, total_gold_earned, channel_id, base_gold, streak_bonus, media_bonus, subscriber_bonus, message_length)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (timestamp, user_id, total_gold_earned, channel_id, base_gold, streak_bonus, media_bonus, subscriber_bonus, message_length))
            await db.commit()
            
    async def create_new_user(self, user_id, user_name, gold=0, last_earned=0, consecutive_days=0, last_post_date=None, media_bonuses=0, streak_bonuses=0, msg_avg_length=0, total_msg_count=0, total_msg_length=0):
        async with aiosqlite.connect('forgesight.db') as db:
            await db.execute('''
                INSERT INTO user_data (user_id, user_name, gold, last_earned, consecutive_days, last_post_date, media_bonuses, streak_bonuses, msg_avg_length, total_msg_count, total_msg_length)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, user_name, gold, last_earned, consecutive_days, last_post_date, media_bonuses, streak_bonuses, msg_avg_length, total_msg_count, total_msg_length))
            await db.commit()
            if self.logger:
                self.logger.info(f'New user {user_id} ({user_name}) created with {gold} gold.')
            else:
                self.logger.info(f'User {user_id} already exists in the database.')