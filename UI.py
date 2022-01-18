'''

    Sources:
            Scrollbar implementation: https://blog.teclado.com/tkinter-scrollable-frames/
'''

from tkinter import *
from tkinter import ttk

from Client import *

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

        Button(centerFrame, text='Chat 1', bg='grey', fg='white', command=lambda cn='Chat 1' : self.gotoChatMenu(cn), anchor='w').grid(row=0,column=0, padx="2", pady='2', sticky="NWES")
        Button(centerFrame, text='Chat 2', bg='grey', fg='white', command=lambda cn='Chat 2' : self.gotoChatMenu(cn), anchor='w').grid(row=1,column=0, padx="2", pady='2', sticky="NWES")
        Button(centerFrame, text='Chat 3', bg='grey', fg='white', command=lambda cn='Chat 3' : self.gotoChatMenu(cn), anchor='w').grid(row=2,column=0, padx="2", pady='2', sticky="NWES")
        Button(centerFrame, text='Chat 4', bg='grey', fg='white', command=lambda cn='Chat 4' : self.gotoChatMenu(cn), anchor='w').grid(row=3,column=0, padx="2", pady='2', sticky="NWES")
        Button(centerFrame, text='Chat 5', bg='grey', fg='white', command=lambda cn='Chat 5' : self.gotoChatMenu(cn), anchor='w').grid(row=3,column=0, padx="2", pady='2', sticky="NWES")

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
        Button(headerFrame, text='Settings', bg='#434343', fg='white').grid(row=0,column=2, sticky="E", padx="2")

        self.text = Text(footerFrame, height=1)
        self.text.grid(row=0,column=0, columnspan=2, sticky="EW", padx=5)
        Button(footerFrame, text='Send', bg='#434343', fg='white', command=self.sendMessage).grid(row=0,column=1, sticky="E", padx="2")

        canvas = Canvas(centerFrame, width=596, height=634, background='#cfe2f3')
        canvas.grid(row=0,column=0)

        s = ttk.Scrollbar(centerFrame, orient=VERTICAL, command=canvas.yview)
        s.grid(row=0, column=0, sticky='NSE')

        messageFrame = ttk.Frame(canvas, style='chat.TFrame')
        messageFrame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

        canvas.create_window((0,0), window=messageFrame, anchor='nw')
        canvas.configure(yscrollcommand=s.set)

        self.messageFrame = messageFrame
        
        self.headerFrame = headerFrame
        self.centerFrame = centerFrame

        root.bind('<Return>', self.sendMessage)

        self.messages = []

    def updateText(self, other):
        lines = self.text.get('1.0', 'end-1c').split('\n')
        n = len(lines)
        self.text.configure(height=n)
        return None

    def gotoMainMenu(self):
        self.parent.switchFrame(MainMenu, None)
        return None

    def displayMessages(self):
        n = len(self.messages)
        r = 0
        for i in range(n, 0, -1):
            j = -1 * i
            m = self.messages[j]
            h = (len(m[1]) // 40) + 1
            t = ttk.Label(self.messageFrame, text=m[1], width=50, wraplength=300)
            t.grid(row=r,column=m[0], sticky="NSW", pady=4)
            r += 1

    def sendMessage(self, other=None):
        message = self.text.get('1.0', 'end-1c')
        n = len(message)
        if n < 1:
            return
        if message[-1] == '\n':
            message = message[:-1]
        self.messages.append((len(self.messages)%2, message))
        self.displayMessages()
        self.text.delete('1.0', END)
        
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
        Button(footerFrame, text='Send', bg='#434343', fg='white', command=sendMessage).grid(row=0,column=1, sticky="E", padx="2")

    def gotoMainMenu(self):
        self.parent.switchFrame(MainMenu, None)
        return None
    
    def sendMessage(self):
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

        self.current_menu = MainMenu(self)

        self.cSock = None
        #self.__connectToServer()

        root.protocol("WM_DELETE_WINDOW", self.closeApp)

    def openMainMenu(self):
        return None

    def closeApp(self):
        if self.cSock is not None:
            disconnectServer(self.cSock)
        self.root.destroy() 

    def switchFrame(self, newFrame, args):
        self.display.destroy()
        self.display = self.createMainFrame()
        self.current_menu = newFrame(self, args)
        return None

    def createMainFrame(self):
        mainframe = ttk.Frame(root, width=600, height=700, style='BG.TFrame')
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

    def __connectToServer(self):
        self.cSock = connectToServer()        

root = Tk()

mainFrameStyle = ttk.Style()
mainFrameStyle.configure('BG.TFrame', background='#cfe2f3', borderwidth=5, relief='flat')

chatBG = ttk.Style()
chatBG.configure('chat.TFrame', background='#cfe2f3', borderwidth=1, relief='flat')

newchatBG = ttk.Style()
newchatBG.configure('newchat.TFrame', background='#525252', borderwidth=5, relief='flat')

header = ttk.Style()
header.configure('header.TFrame', background='#434343', borderwidth=1, relief='flat')

u = UI(root)
root.mainloop()
