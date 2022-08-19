#!/usr/bin/env python

import  wx

#---------------------------------------------------------------------------

class MySplitter(wx.SplitterWindow):
    def __init__(self, parent, ID, log):
        wx.SplitterWindow.__init__(self, parent, ID,
                                   style = wx.SP_LIVE_UPDATE
                                   )
        self.log = log

        self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.OnSashChanged)
        self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING, self.OnSashChanging)

    def OnSashChanged(self, evt):
        self.log.WriteText("sash changed to %s\n" % str(evt.GetSashPosition()))

    def OnSashChanging(self, evt):
        self.log.WriteText("sash changing to %s\n" % str(evt.GetSashPosition()))
        # uncomment this to not allow the change
        #evt.SetSashPosition(-1)


#---------------------------------------------------------------------------

def runTest(frame, nb, log):
    splitter = MySplitter(nb, -1, log)

    #sty = wx.BORDER_NONE
    #sty = wx.BORDER_SIMPLE
    sty = wx.BORDER_SUNKEN

    p1 = wx.Window(splitter, style=sty)
    p1.SetBackgroundColour("pink")
    wx.StaticText(p1, -1, "Panel One", (5,5))

    p2 = wx.Window(splitter, style=sty)
    p2.SetBackgroundColour("sky blue")
    wx.StaticText(p2, -1, "Panel Two", (5,5))

    splitter.SetMinimumPaneSize(20)
    splitter.SplitVertically(p1, p2, -100)

    return splitter


#---------------------------------------------------------------------------




