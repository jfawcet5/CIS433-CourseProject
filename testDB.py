
import sqlite3
import random
import string

# Connect to (or create) a database with name 'testDB.db'
con = sqlite3.connect('testDB.db')

# Get cursor object. Used to execute SQL statements
cur = con.cursor()

# Check if table 'users' already exists
cur.execute('''SELECT count(name) FROM sqlite_master WHERE type='table'
               AND name='users'
            ''')

# If table 'users' does not exist, create it 
if cur.fetchone()[0] == 0:
    print("Creating table: users")
    cur.execute(''' CREATE TABLE users
                    (uid INTEGER, uip TEXT, uname TEXT)
                ''')

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

# Creates a unique entry in the user database
def create_user_entry(ip, uname):
    cur.execute(''' SELECT *
                    FROM users
                    ORDER BY uid DESC
                '''
                )
    val = cur.fetchone()
    if val == None:
        newv = 0
    else:
        newv = val[0] + 1
    cur.execute(''' INSERT INTO users (uid, uip, uname)
                    VALUES (?, ?, ?)
                ''', (newv, ip, uname))

# Prints each row in the 'users' table
def print_table():
    for row in cur.execute('SELECT * FROM users'):
        print(row)

# Finds a row in the table with specified uid value
def get_id(uid):
    cur.execute('SELECT * FROM users WHERE uid=?', (uid,))
    print(cur.fetchone())

# Finds a row in the table with specified uip value
def get_ip(uip):
    cur.execute('SELECT * FROM users WHERE uip=?', (uip,))
    print(cur.fetchone())

# Test adding users to database
for i in range(10):
    create_user_entry(get_random_ip(), get_random_uname())
print_table()
#get_id(2)
#get_ip('165.15.35.108')
con.commit() # Save changes made to database
con.close() # Close database connection
