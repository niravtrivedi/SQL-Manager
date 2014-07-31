import wx
from wxPython.wx import *
from wxPython.grid import *
import sys

class ProportionalSplitter(wx.SplitterWindow):
        def __init__(self,parent, id = -1, proportion=0.66, size = wx.DefaultSize, **kwargs):
                wx.SplitterWindow.__init__(self,parent,id,wx.Point(0, 0),size, **kwargs)
                self.SetMinimumPaneSize(50) #the minimum size of a pane.
                self.proportion = proportion
                if not 0 < self.proportion < 1:
                        raise ValueError, "proportion value for ProportionalSplitter must be between 0 and 1."
                self.ResetSash()
                self.Bind(wx.EVT_SIZE, self.OnReSize)
                self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.OnSashChanged, id=id)
                ##hack to set sizes on first paint event
                self.Bind(wx.EVT_PAINT, self.OnPaint)
                self.firstpaint = True

        def SplitHorizontally(self, win1, win2):
                if self.GetParent() is None: return False
                return wx.SplitterWindow.SplitHorizontally(self, win1, win2,
                        int(round(self.GetParent().GetSize().GetHeight() * self.proportion)))

        def SplitVertically(self, win1, win2):
                if self.GetParent() is None: return False
                return wx.SplitterWindow.SplitVertically(self, win1, win2,
                        int(round(self.GetParent().GetSize().GetWidth() * self.proportion)))

        def GetExpectedSashPosition(self):
                if self.GetSplitMode() == wx.SPLIT_HORIZONTAL:
                        tot = max(self.GetMinimumPaneSize(),self.GetParent().GetClientSize().height)
                else:
                        tot = max(self.GetMinimumPaneSize(),self.GetParent().GetClientSize().width)
                return int(round(tot * self.proportion))

        def ResetSash(self):
                self.SetSashPosition(self.GetExpectedSashPosition())

        def OnReSize(self, event):
                "Window has been resized, so we need to adjust the sash based on self.proportion."
                self.ResetSash()
                event.Skip()

        def OnSashChanged(self, event):
                "We'll change self.proportion now based on where user dragged the sash."
                pos = float(self.GetSashPosition())
                if self.GetSplitMode() == wx.SPLIT_HORIZONTAL:
                        tot = max(self.GetMinimumPaneSize(),self.GetParent().GetClientSize().height)
                else:
                        tot = max(self.GetMinimumPaneSize(),self.GetParent().GetClientSize().width)
                self.proportion = pos / tot
                event.Skip()

        def OnPaint(self,event):
                if self.firstpaint:
                        if self.GetSashPosition() != self.GetExpectedSashPosition():
                                self.ResetSash()
                        self.firstpaint = False
                event.Skip()


class TableTree(wx.TreeCtrl):
     ''' Our table tree'''
     def __init__(self, parent, id, position, size, style,cur_dict):
          if not cur_dict:
               return None
          wx.TreeCtrl.__init__(self, parent, id, position, size, style)
          if cur_dict:
               databse = cur_dict['db']
               root = self.AddRoot("Asterisk")
               cursor = cur_dict['cursor']
               cursor.execute("SHOW TABLES")
               rows = cursor.fetchall()
               for table in rows:
                    self.AppendItem(root, '%s' %table['Tables_in_asterisk'])

class MyDialog(wx.Dialog):
    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title,wx.DefaultPosition,wx.Size(400,250),style=wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL)
        self.conn = None
        self.cur = None
        hbox  = wx.BoxSizer(wx.HORIZONTAL)
        vbox1 = wx.BoxSizer(wx.VERTICAL)
        vbox3 = wx.GridSizer(2,2,0,0)
        vbox4 = wx.BoxSizer(wx.HORIZONTAL)
        pnl1 = wx.Panel(self, -1, style=wx.SIMPLE_BORDER)
        pnl2 = wx.Panel(self, -1)
        vbox1.Add(pnl1, 1, wx.EXPAND | wx.ALL, 3)
        vbox1.Add(pnl2, 1, wx.EXPAND | wx.ALL, 3)
        self.tc1 = wx.TextCtrl(pnl1, -1,size=(150,-1))
        self.tc2 = wx.TextCtrl(pnl1, -1,size=(150,-1))
        self.tc3 = wx.TextCtrl(pnl1, -1,size=(150,-1))
        self.tc4 = wx.TextCtrl(pnl1, -1,size=(150,-1))
        vbox3.AddMany([ (wx.StaticText(pnl1, -1, 'Server IP'),0, wx.ALIGN_CENTER),
                        (self.tc1, 0,wx.ALIGN_LEFT |wx.ALIGN_CENTER_VERTICAL|wx.TAB_TRAVERSAL),
                        (wx.StaticText(pnl1, -1, 'DB Username'),0, wx.ALIGN_CENTER_HORIZONTAL),
                        (self.tc2,0,wx.ALIGN_LEFT),
                        (wx.StaticText(pnl1, -1, 'DB Password'),0, wx.ALIGN_CENTER_HORIZONTAL),
                        (self.tc3,0,wx.ALIGN_LEFT),
                        (wx.StaticText(pnl1, -1, 'DB Name'),0, wx.ALIGN_CENTER_HORIZONTAL),
                        (self.tc4,0,wx.ALIGN_LEFT),
                        ])
        pnl1.SetSizer(vbox3)
        hbox.Add(vbox1, 1, wx.EXPAND)
        self.SetSizer(hbox)
        vbox4.Add(wx.Button(pnl2, 10, 'Test Connection'),  -1, wx.TOP| wx.TOP, 10)
        vbox4.Add(wx.Button(pnl2, 11, 'Cancel'),-1, wx.TOP|wx.TOP, 10)
        vbox4.Add(wx.Button(pnl2, 12, 'Connect'),-1, wx.TOP| wx.TOP, 10)
        pnl2.SetSizer(vbox4)
        self.Bind (wx.EVT_BUTTON, self.TestConnect, id=10)
        self.Bind (wx.EVT_BUTTON, self.Cancel, id=11)
        self.Bind (wx.EVT_BUTTON, self.Connectdb, id=12)
    def TestConnect(self,event):
        try:
            import MySQLdb
        except:
            self.msgbox("Please intall MySQLdb")
        try:
          server = self.tc1.GetValue()
          user = self.tc2.GetValue()
          paswd = self.tc3.GetValue()
          dsb = self.tc4.GetValue()
          self.conn = MySQLdb.connect(host=server, user=user, passwd=paswd, db=dsb)
          if conn:
           self.msgbox("Connected successfully with database")
           conn.close()
           del MySQLdb
        except:
            Unexpetd = "Unexpected error: %s" %sys.exc_info()[0]
            self.msgbox("%s" %Unexpetd)
    def Cancel(self,event):
        self.Close()
    def Connectdb(self,event):
          try:
            import MySQLdb
          except:
            self.msgbox("Please intall MySQLdb")
          try:
               server = self.tc1.GetValue()
               user = self.tc2.GetValue()
               paswd = self.tc3.GetValue()
               self.dsb = self.tc4.GetValue()
               self.conn = MySQLdb.connect(host=server, user=user, passwd=paswd, db=self.dsb)
               self.cur = self.conn.cursor(MySQLdb.cursors.DictCursor)
               self.Close()
          except:
               print sys.exc_info()
               Unexpetd = "Unexpected error: %s" %sys.exc_info()[0]
               self.msgbox("%s" %sys.exc_info()[0])
               
  
    def msgbox(self,msg,title="Information"):
        dlg = wx.MessageDialog(self, msg, title, wx.OK|wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
    def OnAdd(self, event):
        if not self.tc1.GetValue() or not self.tc2.GetValue():
            return
        num_items = self.lc.GetItemCount()
        self.lc.InsertStringItem(num_items, self.tc1.GetValue())
        self.lc.SetStringItem(num_items, 1, self.tc2.GetValue())
        self.tc1.Clear()
        self.tc2.Clear()

    def OnRemove(self, event):
        index = self.lc.GetFocusedItem()
        self.lc.DeleteItem(index)

    def OnClear(self, event):
        self.lc.DeleteAllItems()

    def OnYes(self, event):
        self.Close()


class MainWindow(wx.Frame,MyDialog):
     def __init__(self,parent,id,title,position,size):
          self.cur = None
          self.dbs = None
          wx.Frame.__init__(self, parent, id, title, position, size)
          self.CreateStatusBar()
          menuBar = wx.MenuBar()
          menu = wx.Menu()
          menu.Append(106, "&New Connect", "New Connection")
          menu.Append(107, "&Quit", "Quit")
          menuBar.Append(menu, "&Manager")
          self.SetMenuBar(menuBar)
          self.Bind(wx.EVT_MENU, self.OnShowCustomDialog, id=106)
          self.Bind(wx.EVT_MENU, self.OnQuit, id=107)

          self.split1 = ProportionalSplitter(self,-1, 0.20)
          self.split2 = ProportionalSplitter(self.split1,-1, 0.50)

          self.rightpanel = wx.Panel (self.split1,style=wx.TAB_TRAVERSAL)
          self.control = TableTree(self.rightpanel, -1,(-1, -1) , (500,500),wx.TR_HIDE_ROOT|wx.TR_HAS_BUTTONS,self.dbs)
          self.topleftpanel = wx.Panel (self.split2,style=wx.TAB_TRAVERSAL)
          data =  self.topleftpanel.GetSize()
          box = wx.BoxSizer(wx.VERTICAL)
          hbox = wx.BoxSizer(wx.HORIZONTAL)          
          Connect = wx.Button(self.topleftpanel, wx.ID_CLOSE, "Connect")
          Connect.Bind(wx.EVT_BUTTON, self.OnShowCustomDialog)
          Execute = wx.Button(self.topleftpanel, 107, "Execute")
          Execute.Bind(wx.EVT_BUTTON, self.ExecuteMe)
          self.QryBox = wx.TextCtrl(self.topleftpanel,size = (1000,300),style = wx.TE_MULTILINE|wx.TE_AUTO_URL)
          box.Add(self.QryBox, 0, wx.ALL, 0)
          box.Add(Connect, 0, wx.ALL, 1)
          box.Add(Execute, -1, wx.ALL, 2)
          self.topleftpanel.SetSizer(box)
          self.topleftpanel.SetAutoLayout(True)
          self.topleftpanel.Layout()
          
          self.topleftpanel.SetBackgroundColour('#ccc')
          self.bottomleftpanel = wx.Panel (self.split2)
          self.bottomleftpanel.SetBackgroundColour('#ccc')

          self.split1.SplitVertically(self.rightpanel,self.split2)
          self.split2.SplitHorizontally(self.topleftpanel, self.bottomleftpanel)
          self.Center()
          self.Maximize()
          self.Show(True)

     def OnShowCustomDialog(self, event):
          dia = MyDialog(self, -1, 'Connection Manager')
          val = dia.ShowModal()
          self.cur = dia.cur;
          self.dbs={'cursor':self.cur,'db':dia.dsb}
          self.control = TableTree(self.rightpanel, -1,(10,10) , (500,500),wx.TR_HIDE_ROOT|wx.TR_HAS_BUTTONS,self.dbs)
          dia.Destroy()
     def OnQuit(self,event):
          self.Destroy()
     def ExecuteMe(self,event):
          selection = self.QryBox.GetStringSelection().strip()
          if len(selection)>0:
               SQL = "%s;" %selection
               print SQL
          else:
               SQL = self.QryBox.GetValue().strip()
          #print len(selection);
          #query = self.control1.GetString(selection[0],selection[1])
          if SQL.strip():
               print self.cur
               if self.cur:
                    self.exeq(SQL)
               else:
                    self.msgbox("No any database connected...")
          else:
               self.msgbox("Please type query")
     def exeq(self,qry):
          import re
          if re.match("^insert(.*)",qry,re.I):
               try:
                    self.cur.execute(qry)
               except:
                    
                    self.msgbox("An error occure INSERT MATCH")
          if re.match("^update(.*)",qry,re.I):
               try:
                    self.cur.execute(qry)
               except:
                    self.msgbox("An error occure UPDATE MATCH")
          if re.match("^select(.*)",qry,re.I):
                    try:
                         self.msgbox("Slected")
                    except:
                         self.msgbox("An error occure select MATCH")
                    
          
        
app = wx.App(0)
win = MainWindow(None, -1, "SQL Manager", (50, 50), (600, 400))
win.Show()
app.MainLoop()
