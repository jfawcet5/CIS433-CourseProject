'''

    Sources:
            Scrollbar implementation: https://blog.teclado.com/tkinter-scrollable-frames/
'''

from tkinter import *
from tkinter import ttk

from Client import *
from testDB_v2 import *

# Main menu
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
        Button(headerFrame, text='Settings', bg='#434343', fg='white').grid(row=0,column=2, sticky="E", padx="2")

        # Get list of chats from database
        chats = get_chats_list(self.parent.db_cur)

        # Iterate through chats list and create corresponding buttons
        for i in range(len(chats)):
            num, IP, name = chats[i]
            Button(centerFrame, text=name, bg='grey', fg='white', command=lambda cn=name : self.gotoChatMenu(cn), anchor='w').grid(row=i,column=0, padx="2", pady='2', sticky="NWES")

        self.headerFrame = headerFrame

    def gotoChatMenu(self, chatname):
        self.parent.switchFrame(ChatMenu, chatname)

    def gotoNewChatMenu(self):
        self.parent.switchFrame(NewChatMenu, None)

# Chat menu
class ChatMenu:
    def __init__(self, parent, chatname):
        self.parent = parent
        mainframe = parent.display
        headerFrame = ttk.Frame(mainframe, style='header.TFrame', width=600, height=50)
        headerFrame.grid(column=0, row=0, columnspan=3, sticky='NEWS')
        footerFrame = ttk.Frame(mainframe, style='header.TFrame', width=600, height=50)
        footerFrame.grid(column=0, row=6, columnspan=3, sticky='NEWS')
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

        ttk.Label(headerFrame, text=chatname, background='#434343', foreground='white').grid(row=0,column=1)
        Button(headerFrame, text='Back', bg='#434343', fg='white', command=self.gotoMainMenu).grid(row=0,column=0, sticky="W", padx="2")
        Button(headerFrame, text='Settings', bg='#434343', fg='white', command=self.gotoSettingsMenu).grid(row=0,column=2, sticky="E", padx="2")

        self.text = Text(footerFrame, height=1)
        self.text.grid(row=0,column=0, columnspan=2, sticky="EW", padx=5)
        Button(footerFrame, text='Send', bg='#434343', fg='white', command=self.sendMessage).grid(row=0,column=1, sticky="E", padx="2")

        canvas = Canvas(centerFrame, width=596, height=634, background='#cfe2f3')
        canvas.grid(row=0,column=0)

        s = ttk.Scrollbar(centerFrame, orient=VERTICAL, command=canvas.yview, style='Vertical.TScrollbar')
        s.grid(row=0, column=0, sticky='NSE')

        messageFrame = ttk.Frame(canvas, style='chat.TFrame')
        messageFrame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

        canvas.create_window((0,0), window=messageFrame, anchor='nw')
        canvas.configure(yscrollcommand=s.set)

        self.messageFrame = messageFrame
        
        self.headerFrame = headerFrame
        self.centerFrame = centerFrame

        self.parent.root.bind('<Return>', self.sendMessage)

        # Store chat name in tkinter StringVar
        self.cName = StringVar()
        self.cName.set(chatname)

        # Initialize messages from database
        self.messages = get_messages(self.parent.db_cur, chatname, 40)
        self.displayMessages(chatname)

    def updateText(self, other):
        lines = self.text.get('1.0', 'end-1c').split('\n')
        n = len(lines)
        self.text.configure(height=n)
        return None

    def gotoMainMenu(self):
        self.parent.switchFrame(MainMenu, None)
        return None

    def displayMessages(self, chat_name):
        messageList = self.messages
        n = len(messageList)
                
        r = 0
        for i in range(n, 0, -1):
            j = -1 * i
            m = messageList[j]
            if r == 0 and m[1] == 1:
                ttk.Label(self.messageFrame, text=' ', width=41, wraplength=300, font=("TkFixedFont", 9), background='#cfe2f3').grid(row=0,column=0, sticky="NSW", pady=4)
                ttk.Label(self.messageFrame, text=m[2], width=40, font=("TkFixedFont", 9), wraplength=284).grid(row=r,column=m[1], sticky="NSW", pady=4)
            else:
                if m[1] == 0:
                    messageWidth = 41
                else:
                    messageWidth = 40
                ttk.Label(self.messageFrame, text=m[2], width=messageWidth, font=("TkFixedFont", 9), wraplength=284).grid(row=r,column=m[1], sticky="NSW", pady=4)
            r += 1

    def sendMessage(self, other=None):
        # Get text entered by user
        message = self.text.get('1.0', 'end-1c')
        n = len(message)
        if n < 1:
            return
        if message[-1] == '\n':
            message = message[:-1]
        #TODO: Send message to server through socket here
        ip = get_ip_address(self.parent.db_cur, self.cName.get())
        success = sendMessageTo(self.parent.cSock, message, ip)

        if not success:
            return None

        # Store the sent message in the database
        n = add_message(self.parent.db_cur, self.cName.get(), 1, message)
        # Add message to message 'buffer'
        self.messages.append((n, 1, message))
        # Display messages to screen
        self.displayMessages(self.cName.get())
        # Delete message from prompt
        self.text.delete('1.0', END)
        
    def gotoSettingsMenu(self):
        self.parent.switchFrame(SettingsMenu, self.cName.get())
        return None

# New Chat Menu
class NewChatMenu:
    def __init__(self, parent, other=None):
        self.parent = parent
        mainframe = parent.display
        headerFrame = ttk.Frame(mainframe, style='header.TFrame', width=600, height=100)
        headerFrame.grid(column=0, row=0, columnspan=3, sticky='NEWS')
        centerFrame = ttk.Frame(mainframe, style='newchat.TFrame', width=600, height=600)
        centerFrame.grid(column=0, row=1, rowspan=6, columnspan=3, sticky='NEWS')
        footerFrame = ttk.Frame(mainframe, style='header.TFrame', width=600, height=50)
        footerFrame.grid(column=0, row=6, columnspan=1, sticky='NEWS')

        headerFrame.rowconfigure(0, weight=1)
        headerFrame.columnconfigure(0,weight=1)
        headerFrame.columnconfigure(1,weight=1)
        headerFrame.columnconfigure(2,weight=1)

        footerFrame.rowconfigure(0, weight=1)
        footerFrame.columnconfigure(0,weight=1)
        footerFrame.columnconfigure(1,weight=1)

        ttk.Label(headerFrame, text='New Chat', background='#434343', foreground='white').grid(row=0,column=1)
        Button(headerFrame, text='Back', bg='#434343', fg='white', command=self.gotoMainMenu).grid(row=0,column=0, sticky="W", padx="2")

        ttk.Label(centerFrame, text="To:", font=('Arial', 15), background='#525252', foreground='white').grid(row=1, column=1)
        self.receivertext = Text(centerFrame, height=1)
        self.receivertext.grid(row=1, column=2, columnspan=2, sticky="EW", padx=5)

        ttk.Label(centerFrame, text="IP Address:", font=('Arial', 15), background='#525252', foreground='white').grid(row=2, column=1)
        self.IPtext = Text(centerFrame, height=1)
        self.IPtext.grid(row=2, column=2, columnspan=2, sticky="EW", padx=5)

        self.text = Text(footerFrame, height=1)
        self.text.grid(row=0,column=0, columnspan=2, sticky="EW", padx=5)
        Button(footerFrame, text='Send', bg='#434343', fg='white', command=self.sendMessage).grid(row=0,column=1, sticky="E", padx="2")

    def gotoMainMenu(self):
        self.parent.switchFrame(MainMenu, None)
        return None
    
    def sendMessage(self):
        chatName = self.receivertext.get('1.0', 'end-1c')
        IP = self.IPtext.get('1.0', 'end-1c')
        success = create_chat(self.parent.db_cur, chatName, IP)
        if success == 1:
            print('Invalid Chat Name')
        elif success == 2:
            print('Invalid IP Address')
        elif success == 3:
            print('Chat Name: \'{}\' already exists'.format(chatName))
        return None

# Settings Menu
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

        ttk.Label(headerFrame, text=f"Settings for '{self.chatname}'", background='#434343', foreground='white').grid(row=0,column=1)
        Button(headerFrame, text='Back', bg='#434343', fg='white', command=lambda cn=self.chatname : self.gobacktochat(cn)).grid(row=0,column=0, sticky="W", padx="2")

        ttk.Label(centerFrame, text="Rename to:", font=('Arial', 15), background='#cfe2f3', foreground='black').grid(row=1, column=1)
        self.renamedChat = Text(centerFrame, height=1)
        self.renamedChat.grid(row=1, column=2, columnspan=2, sticky="EW", padx=5)

        ttk.Label(centerFrame, text="Edit IP Address:", font=('Arial', 15), background='#cfe2f3', foreground='black').grid(row=2, column=1)
        self.changedIP = Text(centerFrame, height=1)
        self.changedIP.grid(row=2, column=2, columnspan=2, sticky="EW", padx=5)

        Button(centerFrame, text='Delete Chat', height=3, width=20, bg='red', fg='white', command=None).grid(row=3,column=1, sticky="W", padx="2")

    def gobacktochat(self, chatname):
        self.parent.switchFrame(ChatMenu, chatname)
        return None

# Application Interface manager
class UI:
    def __init__(self, root):
        self.root = root
        root.title("Secure Messenger")
        root.geometry('600x700')
        root.resizable(False, False)

        root.columnconfigure(0,weight=1)
        root.rowconfigure(0,weight=1)

        self.display = self.createMainFrame()

        # Connect to database (store connection object in db_con)
        # Get database cursor object (stored in db_cur)
        self.db_cur, self.db_con = connect_database()

        self.current_menu = MainMenu(self)

        self.cSock = None
        self.receivingThread = None
        print('Connecting to server ... ', end="")
        self.__connectToServer()
        if self.cSock is None:
            print('Connection Failed')
        else:
            print('Success')
            self.receivingThread = create_receiving_thread(self.cSock, self.onReceiveMessage)

        root.protocol("WM_DELETE_WINDOW", self.closeApp)

    def openMainMenu(self):
        return None

    def closeApp(self):
        if self.receivingThread is not None:
            self.receivingThread.close()
        if self.cSock is not None:
            disconnectServer(self.cSock)
        self.db_con.commit() # Save changes to database
        self.db_con.close() # Close database connection
        self.root.destroy() 

    def switchFrame(self, newFrame, args):
        self.display.destroy()
        self.display = self.createMainFrame()
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
        print('Received message: {}'.format(message))

    def __connectToServer(self):
        self.cSock = connectToServer()

root = Tk()
    
mainFrameStyle = ttk.Style()
mainFrameStyle.configure('BG.TFrame', background='#cfe2f3', borderwidth=5, relief='flat')

chatBG = ttk.Style()
chatBG.configure('chat.TFrame', background='#cfe2f3', borderwidth=1, relief='flat')

settingsBG = ttk.Style()
settingsBG.configure('settings.TFrame', background='#cfe2f3', borderwidth=5, relief='flat')

newchatBG = ttk.Style()
newchatBG.configure('newchat.TFrame', background='#525252', borderwidth=5, relief='flat')

header = ttk.Style()
header.configure('header.TFrame', background='#434343', borderwidth=1, relief='flat')

test = ttk.Style()
#test.theme_use('classic')
test.configure('Vertical.TScrollbar', troughcolor='red', background='green')

u = UI(root)
root.mainloop()
