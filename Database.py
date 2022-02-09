
import sqlite3
import random
import string

class DataBase:
    def __init__(self):
        con, cur = connect_database()
        self.connection = con
        self.cursor = cur

    def store_sent_message(self, chat_name, message):
        return add_message(self.cursor, chat_name, 1, message)

    def store_received_message(self, chat_name, message):
        return add_message(self.cursor, chat_name, 0, message)

    def get_chats_list(self):
        return get_chats_list(self.cursor)

    def get_n_messages(self, chat_name, n):
        return get_messages(self.cursor, chat_name, n)

    def create_chat(self, chat_name, IP):
        return create_chat(self.cursor, chat_name, IP)

    def delete_chat(self, chat_name):
        return delete_chat(self.cursor, chat_name)
    
    def update_chatname(self, cur_chat_name, new_chat_name):
        return rename_chat(self.cursor, cur_chat_name, new_chat_name)

    def update_ip(self, cur_chat_name, new_IP):
        return change_ip_address(self.cursor, cur_chat_name, new_IP)

    def get_chat_by_ip(self, IP):
        return get_chat_by_ip(self.cursor, IP)

    def get_ip_by_chatname(self, chat_name):
        return get_ip_address(self.cursor, chat_name)

    def disconnect(self):
        self.connection.commit()
        self.connection.close()
        return None


def is_valid_chatname(chat_name):
    return chat_name.replace(' ', '').replace('.','').isalnum()

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

def connect_database():
    con = sqlite3.connect('data/MessageDB.db')
    cur = con.cursor()
    init_chats_table(cur)
    return con, cur
    
def init_chats_table(cur):
    # Check if table 'chats' already exists
    cur.execute('''SELECT count(name) FROM sqlite_master WHERE type='table'
                   AND name='chats'
                ''')

    # If table 'chats' does not exist, create it 
    if cur.fetchone()[0] == 0:
        print(f"Creating table: chats")
        command = '''CREATE TABLE chats
                        (chatNum INTEGER, receiverIP TEXT, chatName TEXT)'''
        cur.execute(command)
    else:
        print(f"Table: chats exists")

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

def get_ip_address(cur, chat_name):
    cur.execute(''' SELECT *
                    FROM chats
                    WHERE chatName=?
                ''', (chat_name,)
                )
    val = cur.fetchone()
    return val[1]

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
    print('Commands:\nd: delete chat\nc: create chat\nr: rename chat\nip: change IP address\ni: insert message\npc: print chats\npm: print messages\nexit: exit')
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
        elif command == "pm":
            chat = input("Enter chat to read from: ")
            print(get_messages(cur, chat, 100))
            pass
        else:
            break

    #print(get_messages(cur, "Hans Prieto", 10))

    con.commit() # Save changes made to database
    con.close() # Close database connection

if __name__ == "__main__":
    main()
