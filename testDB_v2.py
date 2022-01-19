
import sqlite3
import random
import string


def connect_database():
    con = sqlite3.connect('testMessageDB.db')
    cur = con.cursor()
    init_chats_table(cur)
    return cur, con
    
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

# Create a new chat
def create_chat(cur, chat_name, receiverIP):
    cur.execute(''' SELECT *
                    FROM chats
                    WHERE chatName=?
                ''', (chat_name,)
                )

    if cur.fetchone() != None:
        return None
    
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
    cur.execute(''' INSERT INTO chats (chatNum, receiverIP, chatName)
                    VALUES (?, ?, ?)
                ''', (newv, receiverIP, chat_name))

    create_message_table(cur, chat_name)

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
    print(f'adding to {chat_name}')
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

# Finds a row in the table with specified uid value
def get_id(uid):
    cur.execute('SELECT * FROM users WHERE uid=?', (uid,))
    print(cur.fetchone())

# Finds a row in the table with specified uip value
def get_ip(uip):
    cur.execute('SELECT * FROM users WHERE uip=?', (uip,))
    print(cur.fetchone())

def main():
    # Connect to (or create) a database with name 'testDB.db'
    con = sqlite3.connect('testMessageDB.db')

    # Get cursor object. Used to execute SQL statements
    cur = con.cursor()

    init_chats_table(cur)

    create_chat(cur, 'Chat 1', get_random_ip())
    create_chat(cur, 'Joshua Fawcett', get_random_ip())
    create_chat(cur, 'Hans Prieto', get_random_ip())
    create_chat(cur, 'The boys', get_random_ip())
    create_chat(cur, 'Chat 5', get_random_ip())

    #add_message(cur, 'Joshua Fawcett', 1, 'Hello World')
    #add_message(cur, 'Hans Prieto', 0, 'Hi Hans')

    print_chats(cur)

    #print(get_messages(cur, "Hans Prieto", 10))

    con.commit() # Save changes made to database
    con.close() # Close database connection

if __name__ == "__main__":
    main()
