import wx
from TextEditor import TextEditor


class CompareDlg(wx.Dialog):
    def __init__(self, parent, lstc, rstc):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=u"Compare",
                           pos=wx.DefaultPosition, size=wx.DefaultSize,
                           style=wx.DEFAULT_DIALOG_STYLE |
                           wx.RESIZE_BORDER | wx.STAY_ON_TOP)
        self.te1 = TextEditor(self, None, None)
        self.te2 = TextEditor(self, None, None)
        self.te1.SetDocPointer(lstc.GetDocPointer())
        self.te2.SetDocPointer(rstc.GetDocPointer())
        self.SetMinSize((512, 310))

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.main_sizer)

        self.tool_bar = wx.ToolBar(self)
        self.middle_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.main_sizer.Add(self.tool_bar, 0)
        self.main_sizer.Add(self.middle_sizer, 1, wx.EXPAND)
        self.splitter = wx.Panel(self, size=wx.Size(40, -1))
        self.splitter.SetBackgroundColour(wx.Colour(54, 103, 163))

        self.middle_sizer.Add(self.te1, 2, wx.EXPAND)
        self.middle_sizer.Add(self.splitter, 0, wx.EXPAND)
        self.middle_sizer.Add(self.te2, 2, wx.EXPAND)

        self.Refresh()
        self.diff()

    def diff(self):
        tex1 = self.te1.GetText()
        import wx.stc
        for x in range(self.te1.GetLineCount()):
            self.te1.MarginSetStyle(x, wx.stc.STC_MARGIN_TEXT)
            self.te1.MarginSetText(x, "e")
        self.Refresh()




