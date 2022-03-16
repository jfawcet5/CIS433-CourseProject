'''
    Secure Messenger Application Message Database Module

    Authors: Hans Prieto, Joshua Fawcett

    The message database module is used to store and retrieve chat information and sent/received
    messages on a local (client-side) database file. 

    Sources:
            sqlite3: https://docs.python.org/3/library/sqlite3.html
'''

import sqlite3
import random
import string
# ================================================================================================================

# ================================================ Database Class ================================================
class DataBase:
    # This class is an interface for the UI to create chats, store and retrieve
    # messages, and access chat information (chat name, receiver IP address, etc.)
    def __init__(self):
        con, cur = connect_database() # Connect to database
        self.connection = con # Database connection object
        self.cursor = cur # Databse cursor object to execute commands

    def store_sent_message(self, chat_name, message):
        # Store a sent message in the approriate message table and return
        # status code (success/failure)
        return add_message(self.cursor, chat_name, 1, message)

    def store_received_message(self, chat_name, message):
        # Store a received message in the approriate message table and return
        # status code (success/failure)
        return add_message(self.cursor, chat_name, 0, message)

    def get_chats_list(self):
        # Get the list of chats the user has created
        return get_chats_list(self.cursor)

    def get_n_messages(self, chat_name, n):
        # Get a specified number of messages from a message table
        # with name 'chat_name'
        return get_messages(self.cursor, chat_name, n)

    def get_chat_key(self, chat_name, keyType):
        # Get a specific secret key associated with this chat
        return get_chat_key(self.cursor, chat_name, keyType)

    def create_chat(self, chat_name, receiverIP, receiverName, keys):
        # Create a new chat
        return create_chat(self.cursor, chat_name, receiverIP, receiverName, keys)

    def delete_chat(self, chat_name):
        # Delete a chat
        return delete_chat(self.cursor, chat_name)
    
    def update_chatname(self, cur_chat_name, new_chat_name):
        # Update the chat name for a chat
        return rename_chat(self.cursor, cur_chat_name, new_chat_name)

    def update_ip(self, cur_chat_name, new_IP):
        # Update the IP address of a chat
        return change_ip_address(self.cursor, cur_chat_name, new_IP)

    def get_chat_by_ip(self, IP):
        # Find a chat in the database with the specified IP address
        return get_chat_by_ip(self.cursor, IP)

    def get_ip_by_chatname(self, chat_name):
        # Return the IP address of a chat with chat name 'chat_name'
        return get_ip_address(self.cursor, chat_name)

    def disconnect(self):
        self.connection.commit() # Save changes
        self.connection.close() # Close connection
        return None
# ================================================================================================================

# =============================================== Helper Functions ===============================================
def is_valid_chatname(chat_name):
    # Make sure a chat name is valid
    return chat_name.replace(' ', '').replace('.','').isalnum()

def is_valid_ip(IP):
    # Make sure an IP address is valid
    octets = IP.split('.')
    if len(octets) != 4:
        return False

    for i in range(4):
        if not octets[i].isdecimal():
            return False
        elif int(octets[i]) > 255:
            return False
    return True

def connect_database():
    # Creates database connection and cursor objects and initializes the chats
    # table and keys table
    con = sqlite3.connect('data/MessageDB.db')
    cur = con.cursor()
    init_chats_table(cur)
    create_keys_table(cur)
    return con, cur

def get_random_ip():
    # Used for testing. Generates a random IP address
    v1 = random.randint(0, 255)
    v2 = random.randint(0, 255)
    v3 = random.randint(0, 255)
    v4 = random.randint(0, 255)
    return f'{v1}.{v2}.{v3}.{v4}'

def get_random_uname():
    # Used for testing. Generates a random string of size 3-10
    letters = string.ascii_lowercase
    n = random.randint(3, 10)
    s = ''
    for i in range(n):
        s += random.choice(letters)
    return s
# ================================================================================================================

# =========================================== Database Query functions ===========================================
def get_chat_by_ip(cur, IP):
    # Given an IP address, return the associated chat
    cur.execute(''' SELECT *
                    FROM chats
                    WHERE receiverIP=?
                ''', (IP,)
                )

    return cur.fetchone()

def get_ip_address(cur, chat_name):
    # Given a chat name, return the associated IP address
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

def get_chats_list(cur):
    # Return a list of all chats in the chats table
    cur.execute(''' SELECT *
                    FROM chats
                    ORDER BY chatNum DESC
                '''
                )
    val = cur.fetchall()
    return val

def print_chats(cur):
    # Print chats table
    val = get_chats_list(cur)
    for c in val:
        print(c)

def get_messages(cur, chat_name, numMessages):
    # Get a specific number of messages from a chat with
    # the specified chat name
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

def print_keys(cur):
    # Print the keys table
    cur.execute(''' SELECT *
                    FROM keys
                '''
                )
    val = cur.fetchall()
    for c in val:
        print(c)

def get_chat_key(cur, chat_name, keyType):
    # Gets the specified key from the specified chat
    
    # Translate key type to key index
    if keyType == 2: # Vigenere
        index = 4
    elif keyType == 3: # AES
        index = 3
    elif keyType == 4: # RSA
        index = 1
    elif keyType == 5: # Fernet
        index = 2
    else:
        return None

    cur.execute(''' SELECT *
                    FROM keys 
                    WHERE chatName=?
                ''', (chat_name,)
                )

    val = cur.fetchone()
    if val is not None:
        return val[index]
    return val
# ================================================================================================================

# ======================================= Table/Row Modification Functions =======================================
def init_chats_table(cur):
    # This function ensures that the chats table exists before the execution of
    # any other database accesses
    
    # Check if table 'chats' already exists
    cur.execute('''SELECT count(name) FROM sqlite_master WHERE type='table'
                   AND name='chats'
                ''')

    # If table 'chats' does not exist, create it 
    if cur.fetchone()[0] == 0:
        print(f"Creating table: chats")
        command = '''CREATE TABLE chats
                        (chatNum INTEGER, receiverIP TEXT, receiverName TEXT, chatName TEXT)'''
        cur.execute(command)
    else:
        print(f"Table: chats exists")

def create_chat(cur, chat_name, receiverIP, receiverName, keys):
    # Add a chat to the chats table
    
    # Input validation
    if not is_valid_chatname(chat_name):
        return 1
    elif not is_valid_ip(receiverIP):
        return 2

    if get_ip_address(cur, chat_name) is not None:
        return 3
    if get_chat_by_ip(cur, receiverIP) is not None:
        return 4

    # Extract key values
    pubkey, fernetkey, aeskey, vigenerekey = keys

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
    cur.execute(''' INSERT INTO chats (chatNum, receiverIP, receiverName, chatName)
                    VALUES (?, ?, ?, ?)
                ''', (newv, receiverIP, receiverName, chat_name))
    
    create_message_table(cur, chat_name) # Create corresponding message table
    insert_keys(cur, chat_name, keys) # Create corresponding entry in keys table to store chat keys
    return 0

# deletes a chat
def delete_chat(cur, chat_name):
    # select chat name from table
    cur.execute('''SELECT count(name) FROM sqlite_master WHERE type='table'
                   AND name=?
                ''', (chat_name,))
    
    # delete table associated with chat name
    if cur.fetchone()[0] != 0:
        print(f"Deleting table {chat_name}")
        command = f'''DROP TABLE "{chat_name}"'''
        cur.execute(command)
    else:
        print(f"Table {chat_name} does not exist")  # case where table does not exist
        return 0

    # deletes the chat from the chats table
    cur.execute(''' DELETE 
                    FROM chats
                    WHERE chatName=?
                ''', (chat_name,)
                )
    return 1

# renames a chat
def rename_chat(cur, prev_chat_name, new_chat_name):
    # determine if chat name is valid or not
    if not is_valid_chatname(new_chat_name):
        return 1

    # determine if the previous chat name is in the chats table or not
    cur.execute(''' SELECT *
                    FROM chats
                    WHERE chatName=?
                ''', (prev_chat_name,)
                )
    prev_chat_name_row = cur.fetchone()
    if prev_chat_name_row == None:  # if previous chat name not in table, then error
        return 2

    # check if the new chat name is in the chats table or not
    cur.execute(''' SELECT *
                    FROM chats
                    WHERE chatName=?
                ''', (new_chat_name,)
                )
    new_chat_name_row = cur.fetchone()
    if new_chat_name_row != None:   # if new chat name already in table, then error
        return 3

    cur.execute('''SELECT count(name) FROM sqlite_master WHERE type='table'
                   AND name=?
                ''', (prev_chat_name,))
    if cur.fetchone()[0] != 0:  # renames the chat by renaming the table associated with the previous chat name
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
    return 0    # success in renaming chat

# changes the IP Address for a chat
def change_ip_address(cur, cur_chat_name, new_ip_address):
    if not is_valid_chatname(cur_chat_name):    # determine if chatname is valid or not
        return 1
    elif not is_valid_ip(new_ip_address):   # determine if IP address is valid or not
        return 2
    
    # select chatname from chats table
    cur.execute(''' SELECT *
                    FROM chats
                    WHERE chatName=?
                ''', (cur_chat_name,)
                )

    row = cur.fetchone()
    if row == None:
        return 3

    cur_chatNum = row[0]

    # update the chats table with the IP address associated with the proper chat name
    cur.execute(''' UPDATE chats
                    SET receiverIP=? 
                    WHERE chatNum=?
                ''', (new_ip_address, cur_chatNum)
                )

    return 0    # success in updating IP address

def create_message_table(cur, chat_name):
    # Create a message table to store all of the messages for the
    # specified chat with name 'chat_name'
    
    # Check if the message table already exists
    cur.execute('''SELECT count(name) FROM sqlite_master WHERE type='table'
                   AND name=?
                ''', (chat_name,))

    # If the message table does not exist, create it 
    if cur.fetchone()[0] == 0:
        print(f"Creating table: {chat_name}")
        command = f'''CREATE TABLE "{chat_name}"
                        (messageNum INTEGER, sender INTEGER, message TEXT)'''
        cur.execute(command)
    return None

def add_message(cur, chat_name, sender, message):
    # Adds a message to the correspoding message table with name 'chat_name'. The
    # sender parameter identifies whether the chat was sent or received

    # First make sure the message table exists
    cur.execute(''' SELECT *
                    FROM chats
                    WHERE chatName=?
                ''', (chat_name,)
                )

    if cur.fetchone() == None:
        print(f'chat: {chat_name} does not exist')
        return False

    # Get appropriate message number
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

    # Insert message into table
    command = f''' INSERT INTO "{chat_name}" (messageNum, sender, message)
                    VALUES ({newv}, {sender}, "{message}")
               '''
    cur.execute(command)
    return newv

def create_keys_table(cur):
    # Create the keys table to store all of the secret keys for a
    # particular chat

    # Check if keys table already exists
    cur.execute('''SELECT count(name) FROM sqlite_master WHERE type='table'
                   AND name='keys'
                ''')

    # If keys table does not exist, create it 
    if cur.fetchone()[0] == 0:
        print("Creating table: keys")
        command = f'''CREATE TABLE keys
                        (chatName TEXT, RSAPubKey BLOB, FernetKey BLOB, AESKey BLOB, VigenereKey BLOB)'''
        cur.execute(command)
    return None

def insert_keys(cur, chat_name, keys):
    # Insert a set of keys into the keys table for a specific chat

    # Make sure an entry for this chat does not already exist
    cur.execute(''' SELECT *
                    FROM keys
                    WHERE chatName=?
                ''', (chat_name,)
                )

    if cur.fetchone() is not None:
        return False

    # Extract keys from tuple
    pubkey, fernetkey, aeskey, vigenerekey = keys

    # Insert keys into keys table
    cur.execute(''' INSERT INTO keys (chatName, RSAPubKey, FernetKey, AESKey, VigenereKey)
                    VALUES (?, ?, ?, ?, ?)
               ''', (chat_name, pubkey, fernetkey, aeskey, vigenerekey))
    return True
# ================================================================================================================

# ===================================================== Main =====================================================
def main():
    # Connect to (or create) a database with name 'testDB.db'
    
    #con = sqlite3.connect('testMessageDB.db')
    con = sqlite3.connect('data/MessageDB.db')

    # Get cursor object. Used to execute SQL statements
    cur = con.cursor()
    
    init_chats_table(cur)
    
    #create_chat(cur, 'Chat 1', get_random_ip())
    #create_chat(cur, 'Joshua Fawcett', get_random_ip())
    #create_chat(cur, 'Hans Prieto', get_random_ip())
    #create_chat(cur, 'The boys', get_random_ip())
    #create_chat(cur, 'Chat 5', get_random_ip())

    #add_message(cur, 'Joshua Fawcett', 1, 'Hello World')
    #add_message(cur, 'Hans Prieto', 0, 'Hi Hans')
    
    print_chats(cur)
    print('Commands:\nd: delete chat\nc: create chat\nr: rename chat\nip: change IP address\ni: insert message\nin: insert n messages\npc: print chats\npm: print messages\npk: print keys\nexit: exit')
    while True:
        command =  input("Command: ")
        if command == "c":
            name = input("Enter chat name you would like to create: ")
            ip = input("Enter ip address: ")
            create_chat(cur, name, ip)
            print_chats(cur)
        elif command == "d":
            chat_to_delete = input("Enter chat name you would like to delete: ")
            delete_chat(cur, chat_to_delete)
            print_chats(cur)
        elif command == "r":
            chat_to_rename = input("Enter chat name you would like to rename: ")
            new_chat_name = input("What would you like to rename this chat to?: ")
            rename_chat(cur, chat_to_rename, new_chat_name)
            print_chats(cur)
        elif command == "ip":
            chat_to_change_ip = input("Enter chat name you would like to change the IP Address for: ")
            new_ip_address = input("Enter new ip address: ")
            change_ip_address(cur, chat_to_change_ip, new_ip_address)
        elif command == "pc":
            print_chats(cur)
        elif command == "i":
            chat_to_add_to = input("Insert message into which chat: ")
            sender = input("0 for received, 1 for sent: ")
            message = input("Message to be inserted: ")
            if message.isdecimal():
                num = int(message)
                message = ''
                for i in range(num):
                    message += 'a'
            add_message(cur, chat_to_add_to, int(sender), message)
        elif command == "in":
            chat_to_add_to = input("Insert message into which chat: ")
            num = input("How many messages: ")
            sender = input("0: all sent messages, 1: all received messages, 2: alternate - ")
            minput = input("Message to be inserted: ")
            for i in range(int(num)):
                message = minput
                if message.isdecimal():
                    num = int(message)
                    message = ''
                    for i in range(num):
                        message += 'a'
                add_message(cur, chat_to_add_to, i % 2, message)
        elif command == "pm":
            chat = input("Enter chat to read from: ")
            print(get_messages(cur, chat, 100))
            pass
        elif command == "pk":
            print_keys(cur)
        else:
            break

    #print(get_messages(cur, "Hans Prieto", 10))

    con.commit() # Save changes made to database
    con.close() # Close database connection

if __name__ == "__main__":
    main()
