'''
    Secure Messenger Application User Database

    Authors: Hans Prieto, Joshua Fawcett

    The user database is used to store and retrieve user account information on a local
    (server side) database file. 
'''

import sqlite3

# ================================================================================================================

# ============================================= User Database Class ==============================================
class UserDataBase:
    # This class is an interface for the server to use to add users and retrieve
    # their information
    def __init__(self):
        con, cur = connect_database()
        self.connection = con
        self.cursor = cur

    def addUser(self, username, userIP, pubkeyBytes, passwordBytes):
        return add_user(self.cursor, username, userIP, pubkeyBytes, passwordBytes)

    def getUserPublicKey(self, username):
        return query_user(self.cursor, username, 0)

    def getUserPassword(self, username):
        return query_user(self.cursor, username, 1)

    def getUserIP(self, username):
        return query_user(self.cursor, username, 2)

    def printUsers(self):
        print_users(self.cursor)
        return None
    
    def disconnect(self):
        self.connection.commit() # Save changes made to database
        self.connection.close() # Close connection
        return None
# ================================================================================================================

# =============================================== Helper Functions ===============================================
def connect_database():
    # Create and return database connection and cursor objects
    con = sqlite3.connect('data/UserDB.db')
    cur = con.cursor()
    init_users_table(cur)
    return con, cur
    
def init_users_table(cur):
    # Check if table 'chats' already exists
    cur.execute('''SELECT count(name) FROM sqlite_master WHERE type='table'
                   AND name='users'
                ''')

    # If table 'users' does not exist, create it 
    if cur.fetchone()[0] == 0:
        print(f"Creating table: users")
        command = '''CREATE TABLE users
                        (uID INTEGER, uIP TEXT, pubkey BLOB, uName TEXT, password BLOB)'''
        cur.execute(command)
    else:
        print(f"Table: users exists")

def user_exists(cur, username):
    # Check if a username exists in the users table
    cur.execute(''' SELECT uName
                    FROM users
                '''
                )
    val = cur.fetchall()
    if (username,) in val: # Username already exists
        return True
    else:
        return False

def add_user(cur, username, userIP, pubkeyBytes, passwordBytes):
    # Add a user
    if user_exists(cur, username): # Username already exists
        return False

    cur.execute(''' SELECT uID
                    FROM users
                    ORDER BY uID DESC
                '''
                )
    val = cur.fetchone()
    
    if val == None:
        newv = 0
    else:
        newv = val[0] + 1
    # Create new chat with appropriate values
    cur.execute(''' INSERT INTO users (uID, uIP, pubkey, uName, password)
                    VALUES (?, ?, ?, ?, ?)
                ''', (newv, userIP, pubkeyBytes, username, passwordBytes))
    return True

def print_users(cur):
    # Print a list of users
    cur.execute(''' SELECT *
                    FROM users
                    ORDER BY uID DESC
                '''
                )
    val = cur.fetchall()
    for user in val:
        print(user)
    return val

def query_user(cur, username, queryvalue):
    # Query a specific column for a user
    if not user_exists(cur, username): # Username does not exist
        return None

    cur.execute(''' SELECT *
                    FROM users
                    WHERE uName=?
                ''', (username,)
                )
    val = cur.fetchone()

    if queryvalue == 0: # Query user public key
        return val[2]
    elif queryvalue == 1: # Query user password
        return val[4]
    elif queryvalue == 2: # Query user IP
        return val[1]
    elif queryvalue == 3: # Query all values
        return val
    return None
# ================================================================================================================

# ===================================================== Main =====================================================
def main():
    # Connect to (or create) a database with name 'data/UserDB.db'
    
    con = sqlite3.connect('data/UserDB.db')

    # Get cursor object. Used to execute SQL statements
    cur = con.cursor()

    # Initialize users table
    init_users_table(cur)

    print('Commands:\npu: print users\nqu: Query user values\nexit: exit')
    while True:
        command =  input("Command: ")
        if command == "pu":
            print_users(cur)
        elif command == "qu":
            username = input("Enter user to query: ")
            queryvalue = int(input("Enter value to query (1: public key, 2: IP, 3: password, 4: all): "))
            print(query_user(cur, username, queryvalue))
        else:
            break

    con.commit() # Save changes made to database
    con.close() # Close database connection

if __name__ == "__main__":
    main()
