'''

    Sources:
            Scrollbar implementation: https://blog.teclado.com/tkinter-scrollable-frames/
'''

from tkinter import *
from tkinter import ttk
from tkinter import messagebox

from Client import *
from Database import DataBase
from cipher import AES_generate_key, Fernet_generate_key

import math

# ====================================================================================== Main Menu ======================================================================================
class MainMenu:
    def __init__(self, parent, other=None):
        self.parent = parent
        mainframe = parent.display
        headerFrame = ttk.Frame(mainframe, style='header.TFrame', width=600, height=100)
        headerFrame.grid(column=0, row=0, columnspan=3, sticky='NEWS')
        centerFrame = ttk.Frame(mainframe, style='chat.TFrame', width=600, height=600)
        centerFrame.grid(column=0, row=1, rowspan=6, columnspan=3, sticky='NEWS')

        headerFrame.rowconfigure(0, weight=1)
        headerFrame.columnconfigure(0,weight=1)
        headerFrame.columnconfigure(1,weight=1)
        headerFrame.columnconfigure(2,weight=1)

        centerFrame.columnconfigure(0,weight=1)
        centerFrame.rowconfigure(0, weight=1)
        centerFrame.rowconfigure(1, weight=1)
        centerFrame.rowconfigure(2, weight=1)
        centerFrame.rowconfigure(3, weight=1)
        centerFrame.rowconfigure(4, weight=1)
        centerFrame.rowconfigure(5, weight=1)
        centerFrame.rowconfigure(6, weight=1)
        centerFrame.rowconfigure(7, weight=1)
        centerFrame.rowconfigure(8, weight=1)
                                 

        ttk.Label(headerFrame, text='Chats', background='#434343', foreground='white').grid(row=0,column=1)
        Button(headerFrame, text='New Chat', bg='#434343', fg='white', command=self.gotoNewChatMenu).grid(row=0,column=0, sticky="W", padx="2")
        Button(headerFrame, text='Preferences', bg='#434343', fg='white', command=self.gotoPreferencesMenu).grid(row=0,column=2, sticky="E", padx="2")

        # Get list of chats from database
        db = self.parent.db
        chats = db.get_chats_list()

        # Iterate through chats list and create corresponding buttons
        for i in range(len(chats)):
            num, IP, rname, cname = chats[i]
            Button(centerFrame, text=cname, bg='grey', fg='white', command=lambda cn=cname : self.gotoChatMenu(cn), anchor='w').grid(row=i,column=0, padx="2", pady='2', sticky="NWES")

        self.headerFrame = headerFrame

    def gotoChatMenu(self, chatname):
        self.parent.switchFrame(ChatMenu, chatname)

    def gotoNewChatMenu(self):
        self.parent.switchFrame(NewChatMenu, None)

    def gotoPreferencesMenu(self):
        self.parent.switchFrame(PreferencesMenu, None)
        return None
# =======================================================================================================================================================================================

# ================================================================================ Create Account Menu ==================================================================================
class CreateAccountMenu:
    def __init__(self, parent, other=None):
        self.parent = parent
        mainframe = parent.display
        headerFrame = ttk.Frame(mainframe, style='header.TFrame', width=600, height=100)
        headerFrame.grid(column=0, row=0, columnspan=3, sticky='NEWS')
        centerFrame = ttk.Frame(mainframe, style='chat.TFrame', width=600, height=600)
        centerFrame.grid(column=0, row=1, rowspan=6, columnspan=3, sticky='NEWS')

        # Configuer header frame rows and columns
        headerFrame.rowconfigure(0, weight=1)
        headerFrame.columnconfigure(0,weight=1)
        headerFrame.columnconfigure(1,weight=1)
        headerFrame.columnconfigure(2,weight=1)

        # Configure center frame rows and columns
        centerFrame.columnconfigure(0,weight=1)
        centerFrame.columnconfigure(1,weight=1)
        centerFrame.columnconfigure(2,weight=1)
        centerFrame.rowconfigure(0, weight=1)
        centerFrame.rowconfigure(1, weight=1)
        centerFrame.rowconfigure(2, weight=1)
        centerFrame.rowconfigure(3, weight=1)
        centerFrame.rowconfigure(4, weight=1)
        centerFrame.rowconfigure(5, weight=1)
                                 

        # New Account menu label
        ttk.Label(headerFrame, text='Create Account', background='#434343', foreground='white').grid(row=0,column=1)

        # Tkinter variable to store username and password entered by user
        self.userName = StringVar()
        self.password = StringVar()

        # Commands to validate text entry for username and password
        vcName = (self.parent.root.register(self.validateChatNameEntry), '%d', '%P')
        vpass = (self.parent.root.register(self.validateChatNameEntry), '%d', '%P')

        # Username entry field
        ttk.Label(centerFrame, text="Username", background='#cfe2f3').grid(row=0, column=1, sticky="s", pady=2)
        ttk.Entry(centerFrame, textvariable=self.userName, validate="key", validatecommand=vcName).grid(row=1, column=1, sticky='N', pady=2)

        # Password entry field
        ttk.Label(centerFrame, text="Password", background='#cfe2f3').grid(row=1, column=1, sticky="s", pady=2)
        self.passwordField = ttk.Entry(centerFrame, textvariable=self.password, validate="key", validatecommand=vpass, show="*")
        self.passwordField.grid(row=2, column=1, sticky='N', pady=2)

        # Show password toggle button
        self.showpass = BooleanVar(value=False)
        ttk.Checkbutton(centerFrame, text='show password', command=self.showPassword, variable=self.showpass, onvalue=True, offvalue=False, style='cBox.TCheckbutton').grid(row=2, column=1, sticky="S")

        # Login button
        Button(centerFrame, text='Create Account', bg='#434343', fg='white', command=self.createAccount).grid(row=3,column=1, sticky="N", pady=2)

    def validateChatNameEntry(self, action, newText):
        # Limits length of chat name to 20 characters
        if action == '1':
            if len(newText) > 15:
                return False
            else:
                return True
        return True

    def showPassword(self):
        if self.showpass.get():
            self.passwordField["show"] = ''
        else:
            self.passwordField["show"] = '*'
        return None

    def createAccount(self):
        # Check username and password
        un = self.userName.get()
        pw = self.password.get()
        if len(un) < 3: # Make sure username has at least 3 characters
            self.parent.createPopUp(ErrorPopUp, 'Username must be at least 3 characters')
            return None
        
        if len(pw) < 8: # Make sure password has at least 8 characters
            self.parent.createPopUp(ErrorPopUp, 'Password must have at least 8 characters')
            return None

        # Note: The following condition 'any(map(str.isdigit, pw))' comes from:
        # https://www.adamsmith.haus/python/answers/how-to-check-if-a-string-contains-a-number-in-python
        if not any(map(str.isdigit, pw)):
            self.parent.createPopUp(ErrorPopUp, 'Password must contain at least 1 number')
            return None
        
        if not any(char in "!#$%&*()+,-./:;<>=?@[]^_~|" for char in pw): # Make sure password contains a special character
            self.parent.createPopUp(ErrorPopUp, 'Password must contain at least 1 special character')
            return None
        
        if not any(char.isupper() for char in pw): # Make sure password contains an upper case
            self.parent.createPopUp(ErrorPopUp, 'Password must contain at least 1 upper case')
            return None

        # Contact server with account info
        client = self.parent.client
        success = client.createAccount(un, pw)

        if success is None:
            self.parent.createPopUp(ErrorPopUp, 'Server connection is required')
            return None
        if not success:
            self.parent.createPopUp(ErrorPopUp, 'Username is taken')
            return None
        
        # Go to main menu
        self.gotoMainMenu()
        return None

    def gotoMainMenu(self):
        self.parent.switchFrame(MainMenu, None)
        return None
# =======================================================================================================================================================================================

# ====================================================================================== Chat Menu ======================================================================================
class ChatMenu:
    def __init__(self, parent, chatname):
        self.parent = parent
        mainframe = parent.display
        headerFrame = ttk.Frame(mainframe, style='header.TFrame', width=600, height=50)
        headerFrame.grid(column=0, row=0, columnspan=3, sticky='NEWS')
        footerFrame = ttk.Frame(mainframe, style='header.TFrame', width=600, height=50)
        footerFrame.grid(column=0, row=6, columnspan=2, sticky='NEWS')
        centerFrame = ttk.Frame(mainframe, width=600, height=600)
        centerFrame.grid(column=0, row=1, rowspan=5, columnspan=3, sticky='NEWS')
        centerFrame.grid_propagate(0)

        headerFrame.rowconfigure(0, weight=1)
        headerFrame.columnconfigure(0,weight=1)
        headerFrame.columnconfigure(1,weight=1)
        headerFrame.columnconfigure(2,weight=1)

        footerFrame.rowconfigure(0, weight=1)
        footerFrame.columnconfigure(0,weight=1)
        footerFrame.columnconfigure(1,weight=1)

        # Display chat header with: chat name, back button, and chat settings button
        ttk.Label(headerFrame, text=chatname, background='#434343', foreground='white').grid(row=0,column=1)
        Button(headerFrame, text='Back', bg='#434343', fg='white', command=self.gotoMainMenu).grid(row=0,column=0, sticky="W", padx="2")
        Button(headerFrame, text='Settings', bg='#434343', fg='white', command=self.gotoSettingsMenu).grid(row=0,column=2, sticky="E", padx="2")

        # Display text entry field at bottom for user to enter messages
        self.text = Text(footerFrame, height=1)
        self.text.grid(row=0,column=0, sticky="EW", padx=5)
        Button(footerFrame, text='Send', bg='#434343', fg='white', command=self.sendMessage).grid(row=0,column=2, sticky="EW", padx="2")

        # Display messages in center of screen and create scroll bar
        canvas = Canvas(centerFrame, width=596, height=616, background='#cfe2f3')
        canvas.grid(row=0,column=0)

        s = ttk.Scrollbar(centerFrame, orient=VERTICAL, command=canvas.yview, style='Vertical.TScrollbar')
        s.grid(row=0, column=0, sticky='NSE')

        messageFrame = ttk.Frame(canvas, style='chat.TFrame')
        messageFrame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

        canvas.create_window((0,0), window=messageFrame, anchor='nw')
        canvas.configure(yscrollcommand=s.set)

        self.canvas = canvas

        self.messageFrame = messageFrame
        
        self.headerFrame = headerFrame
        self.centerFrame = centerFrame

        # Bind <return> button with sendmessage function
        self.parent.root.bind('<Return>', self.sendMessage)

        # Store chat name in tkinter StringVar
        self.cName = StringVar()
        self.cName.set(chatname)

        # Initialize messages from database
        self.displayMessages()

    def gotoMainMenu(self):
        # Switch from chat menu to main menu
        self.parent.switchFrame(MainMenu, None)
        return None

    def displayMessages(self):
        # Get messages from database
        db = self.parent.db
        self.messages = db.get_n_messages(self.cName.get(), math.inf)
        n = len(self.messages)

        # Clear message frame by destroying all child label widgets
        for widget in self.messageFrame.winfo_children():
            widget.destroy()

        # Reset message frame grid
        self.messageFrame.grid_forget()
                
        r = 0 # Current row to display message on
        
        for i in range(n, 0, -1):
            # j is index into message list. Reads through messages backwards to display newest
            # messages first
            j = -1 * i
            m = self.messages[j] # Current message

            # Special Case: first message is a sent message (should be aligned on the right). Create an invisible message in column 0
            # to align the actual message in column 1. Since this only applies to row 0, this check could probably be moved out of the
            # for loop for efficiency
            if r == 0 and m[1] == 1:
                ttk.Label(self.messageFrame, text=' ', width=41, wraplength=300, font=("TkFixedFont", 9), background='#cfe2f3').grid(row=0,column=0, sticky="NSW", pady=4)
                ttk.Label(self.messageFrame, text=m[2], width=40, font=("TkFixedFont", 9), wraplength=284).grid(row=r,column=m[1], sticky="NSW", pady=4)
            else:
                # Determine width of white background of message. If both columns have width 41 then column 1 will collide
                # with the scroll bar
                if m[1] == 0:
                    messageWidth = 41
                else:
                    messageWidth = 40
                # Create label widget to display the message
                ttk.Label(self.messageFrame, text=m[2], width=messageWidth, font=("TkFixedFont", 9), wraplength=284).grid(row=r,column=m[1], sticky="NSW", pady=4)
            r += 1

        # Update canvas and scrollbar to display properly
        self.canvas.update()
        self.canvas.yview_moveto('1.0')

    def sendMessage(self, other=None):
        # Get text entered by user
        message = self.text.get('1.0', 'end-1c')
        message = message.replace('\n', '')
        n = len(message)
        # Tried to send empty message or '\n'
        if n < 1 or message == '\n':
            self.text.delete('1.0', END)
            self.text.insert('end-1c', message)
            return

        # Get chat destination IP from database
        db = self.parent.db
        ip = db.get_ip_by_chatname(self.cName.get())

        # Send message to server
        client = self.parent.client

        encryptionType = client.getPreference('eType')

        encryptionKey = db.get_chat_key(self.cName.get(), encryptionType)
        publicKey = db.get_chat_key(self.cName.get(), 4)

        #publicKey = publicKey[2:][:-1].encode('latin-1').decode('unicode-escape').encode('latin-1')
        #print(publicKey)
        print(type(publicKey))
        
        success = client.sendMessage(message, ip, encryptionType, encryptionKey, publicKey)

        # Failed to send a message. Create error pop up
        if not success:
            self.parent.createPopUp(ErrorPopUp, 'Failed to send message')
            self.text.delete('1.0', END)
            self.text.insert('end-1c', message)
            return None

        # Store the sent message in the database
        n = db.store_sent_message(self.cName.get(), message)
        # Add message to message 'buffer'
        self.messages.append((n, 1, message))
        # Display messages to screen
        self.displayMessages()
        # Delete message from prompt
        self.text.delete('1.0', END)
        
    def gotoSettingsMenu(self):
        self.parent.switchFrame(SettingsMenu, self.cName.get())
        return None
# =========================================================================================================================================================================================

# ===================================================================================== New Chat Menu =====================================================================================
class NewChatMenu:
    def __init__(self, parent, other=None):
        self.parent = parent
        mainframe = parent.display
        headerFrame = ttk.Frame(mainframe, style='header.TFrame', width=600, height=100)
        headerFrame.grid(column=0, row=0, columnspan=3, sticky='NEWS')
        centerFrame = ttk.Frame(mainframe, style='newchat.TFrame', width=600, height=600)
        centerFrame.grid(column=0, row=1, rowspan=6, columnspan=3, sticky='NEWS')
        footerFrame = ttk.Frame(mainframe, style='header.TFrame', width=600, height=50)
        footerFrame.grid(column=0, row=6, columnspan=3, sticky='NEWS')

        headerFrame.rowconfigure(0, weight=1)
        headerFrame.columnconfigure(0,weight=1)
        headerFrame.columnconfigure(1,weight=1)
        headerFrame.columnconfigure(2,weight=1)

        centerFrame.columnconfigure(0,weight=1)
        centerFrame.columnconfigure(1,weight=0)
        centerFrame.columnconfigure(2,weight=0)
        centerFrame.columnconfigure(3,weight=1)

        footerFrame.rowconfigure(0, weight=1)
        footerFrame.columnconfigure(0,weight=1)
        footerFrame.columnconfigure(1,weight=1)
        footerFrame.columnconfigure(2,weight=1)

        ttk.Label(headerFrame, text='New Chat', background='#434343', foreground='white').grid(row=0,column=1)
        Button(headerFrame, text='Back', bg='#434343', fg='white', command=self.gotoMainMenu).grid(row=0,column=0, sticky="W", padx="2")

        ttk.Label(centerFrame, text="Chat Name: ", font=('Arial', 15), background='#525252', foreground='white').grid(row=1, column=1)
        #self.userName = StringVar()
        vcName = (self.parent.root.register(self.validateChatNameEntry), '%d', '%P')
        #name = ttk.Entry(centerFrame, textvariable=self.userName, validate="key", validatecommand=validationCommand)
        self.cName = StringVar()
        self.receivertext = ttk.Entry(centerFrame, textvariable=self.cName, validate="key", validatecommand=vcName)
        self.receivertext.grid(row=1, column=2, sticky="EW", padx=5, pady=12)

        ttk.Label(centerFrame, text="To:", font=('Arial', 15), background='#525252', foreground='white').grid(row=2, column=1)
        #self.userName = StringVar()
        vcName = (self.parent.root.register(self.validateChatNameEntry), '%d', '%P')
        #name = ttk.Entry(centerFrame, textvariable=self.userName, validate="key", validatecommand=validationCommand)
        self.uName = StringVar()
        self.receivertext = ttk.Entry(centerFrame, textvariable=self.uName, validate="key", validatecommand=vcName)
        self.receivertext.grid(row=2, column=2, sticky="EW", padx=5, pady=12)

        ttk.Label(centerFrame, text="IP Address:", font=('Arial', 15), background='#525252', foreground='white').grid(row=3, column=1)
        vIP = (self.parent.root.register(self.validateIPEntry), '%d', '%P')
        self.IP = StringVar()
        self.IPtext = ttk.Entry(centerFrame, textvariable=self.IP, validate="key", validatecommand=vIP)
        self.IPtext.grid(row=3, column=2, sticky="EW", padx=5, pady=12)

        self.text = Text(footerFrame, height=1)
        #self.text.grid(row=0,column=0, columnspan=2, sticky="EW", padx=5)
        Button(footerFrame, text='Create', bg='green', fg='white', command=self.createChat).grid(row=0,column=1, padx=2)

    def gotoMainMenu(self):
        self.parent.switchFrame(MainMenu, None)
        return None

    def validateChatNameEntry(self, action, newText):
        # Limits length of chat name to 20 characters
        if action == '1':
            if len(newText) > 20:
                return False
            else:
                return True
        return True

    def validateIPEntry(self, action, newText):
        # Limits length of chat name to 20 characters
        if action == '1':
            # longest ip have form: 255.255.255.255
            if len(newText) > 15:
                return False
            elif len(newText.split('.')) > 4:
                return False
            else:
                return True
        return True
    
    def createChat(self):
        chatName = self.cName.get()
        receiverName = self.uName.get()
        IP = self.IP.get()

        # Get other user's public key from server
        client = self.parent.client
        pubKey = client.getPublicKey(receiverName, IP)

        if pubKey is None:
            print("Did not receive public key")
            return None
        else:
            print("Received key")
            print(pubKey)
            print('\n\n')

        # Create private keys for different encryptions
        vigenereKey = b'defaultvigenerekeyfornow'
        AESKey = AES_generate_key()
        FernetKey = Fernet_generate_key()

        # Store new chat in the database
        db = self.parent.db
        success = db.create_chat(chatName, IP, receiverName, (pubKey, FernetKey, AESKey, vigenereKey))
        if success == 1:
            self.parent.createPopUp(ErrorPopUp, 'Invalid User Name')
        elif success == 2:
            self.parent.createPopUp(ErrorPopUp, 'Invalid IP Address')
        elif success == 3:
            self.parent.createPopUp(ErrorPopUp, 'Chat Name: \'{}\' already exists'.format(chatName))
        elif success == 4:
            self.parent.createPopUp(ErrorPopUp, 'IP Address: \'{}\' already exists'.format(IP))

        self.parent.switchFrame(MainMenu, None)
        return None
# =========================================================================================================================================================================================

# ===================================================================================== Settings Menu =====================================================================================
class SettingsMenu:
    def __init__(self, parent, chatname):
        self.parent = parent
        self.chatname = chatname
        mainframe = parent.display
        headerFrame = ttk.Frame(mainframe, style='header.TFrame', width=600, height=100)
        headerFrame.grid(column=0, row=0, columnspan=3, sticky='NEWS')
        centerFrame = ttk.Frame(mainframe, style='settings.TFrame', width=600, height=200)
        centerFrame.grid(column=0, row=1, rowspan=6, columnspan=3, sticky='NEWS')

        headerFrame.rowconfigure(0, weight=1)
        headerFrame.columnconfigure(0,weight=1)
        headerFrame.columnconfigure(1,weight=1)
        headerFrame.columnconfigure(2,weight=1)
        
        db = self.parent.db
        cur_IP = db.get_ip_by_chatname(chatname)

        ttk.Label(headerFrame, text=f"Settings for '{self.chatname}'\n(IP: {cur_IP})", background='#434343', foreground='white').grid(row=0,column=1)
        Button(headerFrame, text='Back', bg='#434343', fg='white', command=lambda cn=self.chatname : self.gobacktochat(cn)).grid(row=0,column=0, sticky="W", padx="2")

        ttk.Label(centerFrame, text="Rename to:", font=('Arial', 15), background='#cfe2f3', foreground='black').grid(row=1, column=1)
        self.renamedChat = Text(centerFrame, height=1)
        self.renamedChat.grid(row=1, column=2, columnspan=2, sticky="EW", padx=5)

        ttk.Label(centerFrame, text="Edit IP Address:", font=('Arial', 15), background='#cfe2f3', foreground='black').grid(row=2, column=1)
        self.changedIP = Text(centerFrame, height=1)
        self.changedIP.grid(row=2, column=2, columnspan=2, sticky="EW", padx=5)

        Button(centerFrame, text='Delete Chat', height=3, width=20, bg='red', fg='white', command=lambda cn=self.chatname : self.deleteCurrentChat(cn)).grid(row=3,column=1, sticky="W", padx="2")
        Button(centerFrame, text='Update Settings', height=3, width=20, bg='green', fg='white', command=self.updateSettings).grid(row=3,column=2, sticky="W", padx="2")

    def deleteCurrentChat(self, chatname):
        db = self.parent.db
        success = db.delete_chat(chatname)
        if success == 0:
            print(f"Unsuccessful deletion of chat '{chatname}'. Chat does not exist")
        else:
            print(f"Succuessful deletion of chat '{chatname}'")
            self.gotoMainMenu()
        return None

    def updateSettings(self):
        cur_chatname = self.chatname
        new_chatname = self.renamedChat.get('1.0', 'end-1c')
        new_IP = self.changedIP.get('1.0', 'end-1c')

        db = self.parent.db
        cur_IP = db.get_ip_by_chatname(cur_chatname)
        error1 = True
        error2 = True

        # Changes IP Address
        if len(new_IP) > 0:
            update_IP_success = db.update_ip(cur_chatname, new_IP)
            if update_IP_success == 1:
                self.parent.createPopUp(ErrorPopUp, f"Invalid chatname: '{cur_chatname}'")
            elif update_IP_success == 2:
                print(f"Invalid IP Address: {new_IP}")
                self.parent.createPopUp(ErrorPopUp, f"Invalid IP Address: {new_IP}")
            elif update_IP_success == 3:
                self.parent.createPopUp(ErrorPopUp, f"The chat you are trying to change the IP Address for, which is '{cur_chatname}', does not exist")
            else:
                print(f"Changed IP Address from {cur_IP} to {new_IP} successfully")
                error1 = False
        else:
            error1 = False

        # Renames Chat
        if len(new_chatname) > 0:
            rename_chat_success = db.update_chatname(cur_chatname, new_chatname)
            if rename_chat_success == 1:
                print(f"Invalid chatname: '{new_chatname}'")
                self.parent.createPopUp(ErrorPopUp, f"Invalid chatname: '{new_chatname}'")
            elif rename_chat_success == 2:
                print(f"The chat you are trying to rename, which is '{cur_chatname}', does not exist")
                self.parent.createPopUp(ErrorPopUp, f"The chat you are trying to rename, which is '{cur_chatname}', does not exist")
            elif rename_chat_success == 3:
                print(f"chat '{new_chatname}' already exists")
                self.parent.createPopUp(ErrorPopUp, f"chat '{new_chatname}' already exists")
            elif rename_chat_success == 4:
                print(f"Table '{cur_chatname}' does not exist")
            else:
                print(f"Renamed '{cur_chatname}' to '{new_chatname}' successfully")
                error2 = False
        else:
            error2 = False
        
        # Go back to the main menu after settings have been updated
        if not error1 and not error2:
            self.gotoMainMenu()
        return None

    def gobacktochat(self, chatname):
        self.parent.switchFrame(ChatMenu, chatname)
        return None

    def gotoMainMenu(self):
        self.parent.switchFrame(MainMenu, None)
        return None
# =========================================================================================================================================================================================

# ==================================================================================== Preferences Menu ===================================================================================
class PreferencesMenu:
    def __init__(self, parent, other=None):
        self.parent = parent
        mainframe = parent.display
        headerFrame = ttk.Frame(mainframe, style='header.TFrame', width=600, height=100)
        headerFrame.grid(column=0, row=0, columnspan=3, sticky='NEWS')
        centerFrame = ttk.Frame(mainframe, style='chat.TFrame', height=600)
        centerFrame.grid(column=0, row=1, sticky='NEWS')

        headerFrame.rowconfigure(0, weight=1)
        headerFrame.columnconfigure(0,weight=1)
        headerFrame.columnconfigure(1,weight=1)
        headerFrame.columnconfigure(2,weight=1)

        centerFrame.columnconfigure(0,weight=1)
        centerFrame.rowconfigure(0, weight=1)
        centerFrame.rowconfigure(1, weight=1)
        centerFrame.rowconfigure(2, weight=1)
        centerFrame.rowconfigure(3, weight=1)
        centerFrame.rowconfigure(4, weight=1)
        centerFrame.rowconfigure(5, weight=1)
        centerFrame.rowconfigure(6, weight=1)
        centerFrame.rowconfigure(7, weight=1)
        centerFrame.rowconfigure(8, weight=1)

        ttk.Label(headerFrame, text='Preferences', background='#434343', foreground='white').grid(row=0,column=1)
        Button(headerFrame, text='Back', bg='#434343', fg='white', command=self.gotoMainMenu).grid(row=0,column=0, sticky="W", padx="2")

        ttk.Label(centerFrame, text='Username:', background='#434343', foreground='white').grid(row=0,column=0, sticky="W")

        ttk.Label(centerFrame, text=self.parent.client.getUserName(), background='white').grid(row=1, column=0, sticky="WE")

        ttk.Label(centerFrame, text='Encryption Type', background='#434343', foreground='white').grid(row=2,column=0, sticky="W")
        self.etypeVar = StringVar()
        # Create a combobox for user to select their encryption type
        self.etype = ttk.Combobox(centerFrame, textvariable=self.etypeVar, state='readonly')
        # Get list of encryption types and store in combobox values field
        self.etype['values'] = self.parent.client.getEncryptionTypes()
        # Retrieve saved encryption type and display as default value
        encryptionPreference = self.parent.client.getPreference('eType')
        self.etype.current(encryptionPreference)
        # Bind combobox selected event to updatecombobox function
        self.etype.bind('<<ComboboxSelected>>', self.updateComboBox)
        self.etype.grid(row=3, column=0, sticky="WE")

        # Container to hold check button. Needed to put label and checkbutton directly side by side
        checkBoxFrame = ttk.Frame(centerFrame, style='chat.TFrame')
        checkBoxFrame.grid(column=0, row=4, sticky="W")
        # Label for checkbutton
        ttk.Label(checkBoxFrame, text='New Chat Pop-ups: ', background='#434343', foreground='white').grid(row=4,column=0, sticky="W")
        # Retrieve saved popup preference
        popupsPreference = self.parent.client.getPreference('popups')
        # Create tkinter bool variable and initialize with popup preference value
        self.doPopups = BooleanVar(value=popupsPreference)
        # Create checkbutton for user to update their popup preference
        self.check = ttk.Checkbutton(checkBoxFrame, text='', command=self.updateCheckBox, variable=self.doPopups, onvalue=True, offvalue=False, style='cBox.TCheckbutton')
        self.check.grid(row=4, column=1, sticky="WE", padx=3)

        self.headerFrame = headerFrame

    def updateUserName(self, args=None):
        newName = self.userName.get()
        if len(newName) < 3 or len(newName) > 16:
            print('Invalid Username')
            self.parent.createPopUp(ErrorPopUp, 'Invalid User Name')
            return None
        self.parent.client.updateUserName(newName)
        return None

    def validateInsert(self, action, newText):
        # Limit the number of characters a user can insert to 16
        if action == '1':
            if len(newText) > 16:
                return False
            else:
                return True
        return True

    def updateComboBox(self, args):
        self.parent.client.updatePreference(eType=self.etype.current())
        return None

    def updateCheckBox(self):
        self.parent.client.updatePreference(doPopups=self.doPopups.get())
        return None

    def gotoMainMenu(self):
        self.parent.switchFrame(MainMenu, None)
# =========================================================================================================================================================================================

# ================================================================================== New Chat Popup Menu ==================================================================================
class ReceivedMessagePopUp:
    def __init__(self, parent, position, args=None):
        self.parent = parent
        self.args = args

        self.popUp = Toplevel(self.parent.root)
        self.popUp.geometry(position)

        self.mainframe = None
        self.popUp.transient(self.parent.root)
        self.popUp.protocol("WM_DELETE_WINDOW", self.closePopUp)

        self.gotoMainPopUp()

    def gotoMainPopUp(self):
        if self.mainframe is not None:
            self.mainframe.destroy()
        self.mainframe = ttk.Frame(self.popUp, style='BG.TFrame')
        self.mainframe.grid()

        # Display 'New Message' header
        Label(self.mainframe, text='New Message', background='#cfe2f3', foreground='black', font=('Arial', 18)).grid(row=0, column=1)

        # Display new message info (sender name, message preview)
        headerFrame = ttk.Frame(self.mainframe, style='chat.TFrame')
        headerFrame.grid(row=1, column=0, columnspan = 3, sticky="W")
        Label(headerFrame, text='From:', background='#cfe2f3', foreground='black').grid(row=0, column=0, sticky="W")
        Label(headerFrame, text='{}'.format(self.args[2]), background='#cfe2f3', foreground='black').grid(row=0, column=1, sticky="W")
        previewText = self.args[1]
        if len(previewText) > 38:
            previewText = previewText[:38] + '...'
        else:
            previewText = previewText[:38]
        Label(headerFrame, text='Preview:', background='#cfe2f3', foreground='grey').grid(row=1, column=0, sticky="W")
        Label(headerFrame, text=previewText, background='#cfe2f3', foreground='grey').grid(row=1, column=1, sticky="W")

        # Display action buttons (Create a new chat, ignore the message, block sender IP address)
        Button(self.mainframe, text='Create Chat', command=self.gotoCreateChat).grid(row=2, column=0)
        Button(self.mainframe, text='Ignore', command=self.closePopUp).grid(row=2, column=1)
        Button(self.mainframe, text='Block IP', command=self.blockIP).grid(row=2, column=2)

    def gotoCreateChat(self):
        self.mainframe.destroy()
        self.mainframe = ttk.Frame(self.popUp, style='BG.TFrame')
        self.mainframe.grid()

        Label(self.mainframe, text='Chat name: ', background='#434343', foreground='white').grid(row=1, column=0)

        self.cName = StringVar()
        name = ttk.Entry(self.mainframe, textvariable=self.cName)
        name.grid(row=1, column=1, columnspan=2)
        name.insert(0, self.args[2])

        Button(self.mainframe, text='Create', command=self.createChat).grid(row=1, column=3)
        Button(self.mainframe, text='Back', command=self.gotoMainPopUp).grid(row=0, column=0, sticky='w')

    def createChat(self):
        db = self.parent.db
        print(f'Creating Chat: {self.cName.get()}, IP: {self.args[0]}')
        db.create_chat(self.cName.get(), self.args[0])
        db.store_received_message(self.cName.get(), self.args[1])
        if type(self.parent.current_menu) == MainMenu:
            self.parent.switchFrame(MainMenu, None)
        self.closePopUp()

    def blockIP(self):
        self.closePopUp()

    def closePopUp(self):
        self.parent.closePopUp(self)
        self.popUp.destroy()
# =========================================================================================================================================================================================

# =================================================================================== Error Popup Menu ====================================================================================
class ErrorPopUp:
    def __init__(self, parent, position, args=None):
        self.parent = parent
        if args is not None:
            self.errormsg = args
        else:
            self.errormsg = ''

        self.popUp = Toplevel(self.parent.root)
        self.popUp.geometry(position)
        self.popUp.resizable(False, False)
        self.popUp.title("Error")

        self.mainframe = None
        self.popUp.transient(self.parent.root)
        self.popUp.protocol("WM_DELETE_WINDOW", self.closePopUp)

        self.gotoMainPopUp()

    def gotoMainPopUp(self):
        if self.mainframe is not None:
            self.mainframe.destroy()
        self.mainframe = ttk.Frame(self.popUp, style='error.TFrame')
        self.mainframe.grid()


        self.mainframe.rowconfigure(0, weight=1)
        self.mainframe.rowconfigure(1, weight=0)
        self.mainframe.rowconfigure(2, weight=1)
        self.mainframe.columnconfigure(0,weight=1)
        self.mainframe.columnconfigure(1,weight=0)
        self.mainframe.columnconfigure(2,weight=1)

        Label(self.mainframe, text="Error", background='red', foreground='white').grid(row=0, column=0, sticky="w")
        Label(self.mainframe, text=self.errormsg, background='red', foreground='white').grid(row=1, column=0, sticky="w")

        Button(self.mainframe, text='OK', command=self.closePopUp).grid(row=2, column=2, sticky='e')

    def closePopUp(self):
        self.parent.closePopUp(self)
        self.popUp.destroy()
# =========================================================================================================================================================================================

# =================================================================================== Interface Manager ===================================================================================
class UI:
    def __init__(self, root):
        self.root = root
        root.title("Secure Messenger")
        root.geometry('600x700')
        root.resizable(False, False)
        root.option_add( "*font", "Arial 14" )

        root.columnconfigure(0,weight=1)
        root.rowconfigure(0,weight=1)

        self.display = self.createMainFrame()

        self.popUps = []

        # Connect to database 
        self.db = DataBase()

        # Connect to server
        self.client = Client(self.onReceiveMessage)

        if self.client.getUserName() == '':
            self.current_menu = CreateAccountMenu(self)
        else:
            self.current_menu = MainMenu(self)

        if not self.client.connected:
            self.createPopUp(ErrorPopUp, 'Failed to connect to server')
        #self.current_menu = MainMenu(self) # Create and display main menu

        #self.client = Client(self.onReceiveMessage)

        root.protocol("WM_DELETE_WINDOW", self.closeApp)

        self.buffer = []

        self.update_UI()

    def openMainMenu(self):
        return None

    def closeApp(self):
        self.client.disconnect()
        self.db.disconnect()
        self.root.destroy() 

    def switchFrame(self, newFrame, args):
        self.display.destroy()
        self.display = self.createMainFrame()
        self.update_UI()
        self.current_menu = newFrame(self, args)
        return None

    def createMainFrame(self):
        mainframe = ttk.Frame(self.root, width=600, height=700, style='BG.TFrame')
        mainframe.grid(column=0, row=0, sticky='nwes')
        mainframe.columnconfigure(0, weight=1)
        mainframe.columnconfigure(1, weight=1)
        mainframe.columnconfigure(2, weight=1)
        mainframe.rowconfigure(0, weight=2)
        mainframe.rowconfigure(1, weight=3)
        mainframe.rowconfigure(2, weight=3)
        mainframe.rowconfigure(3, weight=3)
        mainframe.rowconfigure(4, weight=3)
        mainframe.rowconfigure(5, weight=3)
        mainframe.rowconfigure(6, weight=2)
        return mainframe

    def onReceiveMessage(self, message):
        ''' Determines how the UI responds to received messages

            This method is invoked by the receiving thread (self.receivingThread), defined
            in Client.py
        '''
        print('received message: {}'.format(message))
        self.buffer.append(message)

    def handleMessage(self, message):
        ''' Determines how the UI responds to received messages

            This method is invoked by the receiving thread (self.receivingThread), defined
            in Client.py
        '''
        messageFields = self.client.readMessage(message)
        IP = messageFields[0]
        chat = self.db.get_chat_by_ip(IP)
        print(chat)
        if chat is not None:
            # Add message to chat
            print("chat exists")
            self.db.store_received_message(chat[3], messageFields[1])
            if type(self.current_menu) == ChatMenu:
                self.current_menu.displayMessages()
        else:
            print("chat does not exist")
            # Create popup
            doPopup = self.client.getPreference('popups')
            if doPopup == 'True':
                self.createPopUp(ReceivedMessagePopUp, messageFields)

    def update_UI(self):
        count = 0
        for p in self.popUps:
            if type(p) == ReceivedMessagePopUp:
                count += 1
        
        if len(self.buffer) != 0 and count == 0:
            message = self.buffer.pop()
            self.handleMessage(message)
        self.display.after(1000, self.update_UI)
        return None

    def createPopUp(self, popUpClass, message):
        print('create popup')
        position = self.root.geometry()[7:]
        self.popUps.append(popUpClass(self, position, message))
        return None

    def closePopUp(self, popUp):
        try:
            self.popUps.remove(popUp)
        except Exception:
            pass
        return None
# =========================================================================================================================================================================================

# ===================================================================================== Start Program =====================================================================================
root = Tk()
    
mainFrameStyle = ttk.Style()
mainFrameStyle.configure('BG.TFrame', background='#cfe2f3', borderwidth=5, relief='flat')

errorStyle = ttk.Style()
errorStyle.configure('error.TFrame', background='red', borderwidth=5, relief='flat')

chatBG = ttk.Style()
chatBG.configure('chat.TFrame', background='#cfe2f3', borderwidth=1, relief='flat')

settingsBG = ttk.Style()
settingsBG.configure('settings.TFrame', background='#cfe2f3', borderwidth=5, relief='flat')

newchatBG = ttk.Style()
newchatBG.configure('newchat.TFrame', background='#525252', borderwidth=5, relief='flat')

header = ttk.Style()
header.configure('header.TFrame', background='#434343', borderwidth=1, relief='flat')

checkBox = ttk.Style()
checkBox.configure('cBox.TCheckbutton', background='#cfe2f3')

test = ttk.Style()
#test.theme_use('classic')
test.configure('Vertical.TScrollbar', troughcolor='red', background='green')

u = UI(root)
root.mainloop()
