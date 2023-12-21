import wx
from TextEditor import TextEditor


class CompareDlg(wx.Dialog):
    def __init__(self, parent, lstc, rstc):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=u"Compare",
                           pos=wx.DefaultPosition, size=wx.DefaultSize,
                           style=wx.DEFAULT_DIALOG_STYLE |
                           wx.RESIZE_BORDER | wx.STAY_ON_TOP)
        self.lstc = lstc
        self.rstc = rstc
        self.SetMinSize((512, 310))

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.main_sizer)

        self.tool_bar = wx.ToolBar(self)
        self.middle_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.main_sizer.Add(self.tool_bar, 0)
        self.main_sizer.Add(self.middle_sizer, 1, wx.EXPAND)
        self.splitter = wx.Panel(self, size=wx.Size(40, -1))
        self.splitter.SetBackgroundColour(wx.Colour(54, 103, 163))

        self.middle_sizer.Add(self.lstc, 2, wx.EXPAND)
        self.middle_sizer.Add(self.splitter, 0, wx.EXPAND)
        self.middle_sizer.Add(self.rstc, 2, wx.EXPAND)

        self.Refresh()



