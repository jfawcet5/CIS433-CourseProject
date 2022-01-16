from tkinter import *
from tkinter import ttk

# Main menu
class MainMenu:
    def __init__(self, mainframe, switchFN, other=None):
        self.parent = mainframe
        self.switchFN = switchFN

        Button(mainframe, text='Chat Menu', bg='#434343', fg='white', command=self.gotoChatMenu).grid(row=0,column=0, padx="2")

    def gotoChatMenu(self):
        self.switchFN(ChatMenu, "Chat Name")

# Chat menu
class ChatMenu:
    def __init__(self, mainframe, switchFN, chatname):
        self.parent = mainframe
        self.switchFN = switchFN
        headerFrame = ttk.Frame(mainframe, style='header.TFrame', width=600, height=50)
        headerFrame.grid(column=0, row=0, columnspan=3, sticky='NEWS')
        footerFrame = ttk.Frame(mainframe, style='header.TFrame', width=600, height=50)
        footerFrame.grid(column=0, row=6, columnspan=3, sticky='NEWS')
        centerFrame = ttk.Frame(mainframe, style='chat.TFrame', width=600, height=600)
        centerFrame.grid(column=0, row=1, rowspan=5, columnspan=3, sticky='NEWS')

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
        Button(footerFrame, text='Send', bg='#434343', fg='white').grid(row=0,column=1, sticky="E", padx="2")

        self.headerFrame = headerFrame

        root.bind('<Return>', self.updateText)
        root.bind('<BackSpace>', self.updateText)

    def updateText(self, other):
        lines = self.text.get('1.0', 'end-1c').split('\n')
        n = len(lines)
        self.text.configure(height=n)
        return None

    def gotoMainMenu(self):
        self.switchFN(MainMenu, None)
        return None

# Application Interface manager
class UI:
    def __init__(self, root):
        self.root = root
        root.title("Secure Messenger")

        root.columnconfigure(0,weight=1)
        root.rowconfigure(0,weight=1)

        self.display = self.createMainFrame()

        self.current_menu = MainMenu(self.display, self.switchFrame)

    def openMainMenu(self):
        return None

    def switchFrame(self, newFrame, args):
        self.display.destroy()
        self.display = self.createMainFrame()
        self.current_menu = newFrame(self.display, self.switchFrame, args)
        return None

    def createMainFrame(self):
        mainframe = ttk.Frame(root, width=600, height=800, style='BG.TFrame')
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
        

root = Tk()

mainFrameStyle = ttk.Style()
mainFrameStyle.configure('BG.TFrame', background='#cfe2f3', borderwidth=5, relief='flat')

chatBG = ttk.Style()
chatBG.configure('chat.TFrame', background='#cfe2f3', borderwidth=1, relief='flat')

header = ttk.Style()
header.configure('header.TFrame', background='#434343', borderwidth=1, relief='flat')

st = ttk.Style()
st.configure('st.TButton', foreground='#434343', background='green', bordercolor='red', darkcolor='pink', highlightcolor='yellow', lightcolor='purple',borderwidth=1)

u = UI(root)
root.mainloop()
