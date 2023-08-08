import psycopg2
import nacl.pwhash

class DatabaseHelper:
    def __init__(self, host: str = 'localhost',
                 port: int = 5433,
                 database: str = 'smart-terrarium',
                 user: str = 'frog',
                 password: str = 'frog!123'):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = self.get_connection()

    def get_connection(self):
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password
        )

    def get_cursor(self):
        return self.connection.cursor()

    def execute_query(self, query):
        cursor = self.get_cursor()
        cursor.execute(query)
        # fetch all or commit
        if query.split(' ')[0].upper() == 'SELECT':
            result = cursor.fetchall()
            cursor.close()
            return result
        else:
            self.connection.commit()
            cursor.close()

    def add_active_user(self, email, password):
        def hash(input: str, format: str = 'UTF-8') -> str:
            hashed_password = nacl.pwhash.argon2id.str(bytes(input, format))
            return hashed_password.decode(format)
        query = 'INSERT INTO "user"' + \
            f"(email, password, is_active) VALUES ('{email}', '{hash(password)}', true);"
        self.execute_query(query)

    def __get_user_id(self, email):
        query = 'SELECT id FROM "user" ' + f"WHERE email = '{email}';"
        return self.execute_query(query)[0][0]

    def get_active_code(self, email):
        user_id = self.__get_user_id(email)
        query = f"SELECT confirmation_code FROM user_confirmation WHERE user_id = {user_id};"
        return self.execute_query(query)[0][0]
