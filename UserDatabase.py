import sqlite3
import random
import string

# ================================================================================================================

# ============================================= User Database Class ==============================================
class UserDataBase:
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
        self.connection.commit()
        self.connection.close()
        return None
# ================================================================================================================

# =============================================== Helper Functions ===============================================
def connect_database():
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
    cur.execute(''' SELECT uName
                    FROM users
                '''
                )
    val = cur.fetchall()
    if (username,) in val: # Username already exists
        return True
    else:
        return False

# Add user
def add_user(cur, username, userIP, pubkeyBytes, passwordBytes):
    # Input validation
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
    if not user_exists(cur, username):
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

# =============================================== Helper Functions ===============================================










def is_valid_ip(IP):
    octets = IP.split('.')
    if len(octets) != 4:
        return False

    for i in range(4):
        if not octets[i].isdecimal():
            return False
        elif int(octets[i]) > 255:
            return False
    return True

def get_chat_by_ip(cur, IP):
    cur.execute(''' SELECT *
                    FROM chats
                    WHERE receiverIP=?
                ''', (IP,)
                )

    return cur.fetchone()

def get_ip_address(cur, chat_name):
    cur.execute(''' SELECT *
                    FROM chats
                    WHERE chatName=?
                ''', (chat_name,)
                )
    val = cur.fetchone()
    if val is not None:
        return val[1]
    else:
        return None

# Create a new chat
def create_chat(cur, chat_name, receiverIP):
    # Input validation
    if not is_valid_chatname(chat_name):
        return 1
    elif not is_valid_ip(receiverIP):
        return 2

    if get_ip_address(cur, chat_name) is not None:
        return 3
    if get_chat_by_ip(cur, receiverIP) is not None:
        return 4

    # Get largest chatNum
    cur.execute(''' SELECT *
                    FROM chats
                    ORDER BY chatNum DESC
                '''
                )
    val = cur.fetchone()
    if val == None:
        newv = 0
    else:
        newv = val[0] + 1
    # Create new chat with appropriate values
    cur.execute(''' INSERT INTO chats (chatNum, receiverIP, chatName)
                    VALUES (?, ?, ?)
                ''', (newv, receiverIP, chat_name))
    # Create corresponding message table
    create_message_table(cur, chat_name)
    return 0

# deletes a chat
def delete_chat(cur, chat_name):
    cur.execute('''SELECT count(name) FROM sqlite_master WHERE type='table'
                   AND name=?
                ''', (chat_name,))
    if cur.fetchone()[0] != 0:
        print(f"Deleting table {chat_name}")
        command = f'''DROP TABLE "{chat_name}"'''
        cur.execute(command)
    else:
        print(f"Table {chat_name} does not exist")
        return 0

    cur.execute(''' DELETE 
                    FROM chats
                    WHERE chatName=?
                ''', (chat_name,)
                )
    return 1

# renames a chat
def rename_chat(cur, prev_chat_name, new_chat_name):
    if not is_valid_chatname(new_chat_name):
        return 1

    cur.execute(''' SELECT *
                    FROM chats
                    WHERE chatName=?
                ''', (prev_chat_name,)
                )
    prev_chat_name_row = cur.fetchone()
    if prev_chat_name_row == None:
        return 2

    cur.execute(''' SELECT *
                    FROM chats
                    WHERE chatName=?
                ''', (new_chat_name,)
                )
    new_chat_name_row = cur.fetchone()
    if new_chat_name_row != None:
        return 3

    cur.execute('''SELECT count(name) FROM sqlite_master WHERE type='table'
                   AND name=?
                ''', (prev_chat_name,))
    if cur.fetchone()[0] != 0:
        print(f"renaming table {prev_chat_name} to {new_chat_name}")
        command = f'''ALTER TABLE "{prev_chat_name}" RENAME TO "{new_chat_name}"'''
        cur.execute(command)
    else:
        return 4

    cur_chatNum = prev_chat_name_row[0]

    cur.execute(''' UPDATE chats
                    SET chatName=? 
                    WHERE chatNum=?
                ''', (new_chat_name, cur_chatNum)
                )
    return 0

# changes the IP Address for a chat
def change_ip_address(cur, cur_chat_name, new_ip_address):
    if not is_valid_chatname(cur_chat_name):
        return 1
    elif not is_valid_ip(new_ip_address):
        return 2
    
    cur.execute(''' SELECT *
                    FROM chats
                    WHERE chatName=?
                ''', (cur_chat_name,)
                )

    row = cur.fetchone()
    if row == None:
        return 3

    cur_chatNum = row[0]

    cur.execute(''' UPDATE chats
                    SET receiverIP=? 
                    WHERE chatNum=?
                ''', (new_ip_address, cur_chatNum)
                )

    return 0

# Print out the chats table
def print_chats(cur):
    cur.execute(''' SELECT *
                    FROM chats
                    ORDER BY chatNum DESC
                '''
                )
    val = cur.fetchall()
    for c in val:
        print(c)

def get_chats_list(cur):
    cur.execute(''' SELECT *
                    FROM chats
                    ORDER BY chatNum DESC
                '''
                )
    val = cur.fetchall()
    return val

def create_message_table(cur, chat_name):
    #name = f'chat{chat_num}'
    # Check if table 'users' already exists
    cur.execute('''SELECT count(name) FROM sqlite_master WHERE type='table'
                   AND name=?
                ''', (chat_name,))

    # If table 'table_name' does not exist, create it 
    if cur.fetchone()[0] == 0:
        print(f"Creating table: {chat_name}")
        command = f'''CREATE TABLE "{chat_name}"
                        (messageNum INTEGER, sender INTEGER, message TEXT)'''
        cur.execute(command)
    else:
        print(f"Table: {chat_name} exists")

def get_messages(cur, chat_name, numMessages):
    command = f''' SELECT *
                    FROM "{chat_name}"
                    ORDER BY messageNum ASC
                '''
                
    cur.execute(command)
    val = cur.fetchall()
    if len(val) > numMessages:
        index = -1 * numMessages
        return val[index:]
    else:
        return val

def add_message(cur, chat_name, sender, message):
    print(f'Adding message to table: {chat_name}')
    cur.execute(''' SELECT *
                    FROM chats
                    WHERE chatName=?
                ''', (chat_name,)
                )

    if cur.fetchone() == None:
        print(f'chat: {chat_name} does not exist')
        return False
    command = f''' SELECT *
                    FROM "{chat_name}"
                    ORDER BY messageNum DESC
                '''
                
    cur.execute(command)
    val = cur.fetchone()
    if val == None:
        newv = 0
    else:
        newv = val[0] + 1
    command = f''' INSERT INTO "{chat_name}" (messageNum, sender, message)
                    VALUES ({newv}, {sender}, "{message}")
               '''
    cur.execute(command)
    return newv

# Used for testing. Generates a random IP address
def get_random_ip():
    v1 = random.randint(0, 255)
    v2 = random.randint(0, 255)
    v3 = random.randint(0, 255)
    v4 = random.randint(0, 255)
    return f'{v1}.{v2}.{v3}.{v4}'

# Used for testing. Generates a random string of size 3-10
def get_random_uname():
    letters = string.ascii_lowercase
    n = random.randint(3, 10)
    s = ''
    for i in range(n):
        s += random.choice(letters)
    return s

def main():
    # Connect to (or create) a database with name 'testDB.db'
    
    #con = sqlite3.connect('testMessageDB.db')
    con = sqlite3.connect('data/UserDB.db')

    # Get cursor object. Used to execute SQL statements
    cur = con.cursor()
    
    init_users_table(cur)

    add_user(cur, 'josh', get_random_ip(), b'heloo world', b'password1')
    add_user(cur, 'hans', get_random_ip(), b'pubk3ylqk', b'password2')
    add_user(cur, 'jillian', get_random_ip(), b'iamawesome', b'password3')

    print('Commands:\npu: print users\nqu: Query user\nexit: exit')
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

    #print(get_messages(cur, "Hans Prieto", 10))

    con.commit() # Save changes made to database
    con.close() # Close database connection

if __name__ == "__main__":
    main()
