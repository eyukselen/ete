import wx
import wx.stc as stc


class TextEditor(wx.stc.StyledTextCtrl):
    def __init__(self, parent=None, filename='', status_bar=None):
        stc.StyledTextCtrl.__init__(self, parent, style=wx.SIMPLE_BORDER)
        self.ID_MARGIN_CLICK = wx.ID_ANY
        self.markers = {}
        self.MARGIN_1 = 0
        self.MARGIN_2 = 1
        self.MARGIN_3 = 2


class MainWindow(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title='ete - ete text editor')
        self.te = TextEditor(self)

        self.te.SetMarginType(1,stc.STC_MARGIN_TEXT)
        self.te.SetMarginWidth(1, 30)
        self.te.StyleSetSpec(1, 'fore:#000000,back:#ADD8E6')
        self.te.StyleSetSpec(stc.STC_STYLE_LINENUMBER, 'fore:#000000,back:#ADD8E6')
        self.te.MarginSetStyle(0, 1)

        self.te.SetText("This is a sample text to demonstrate custom margin text.")
        self.te.MarginSetText(0, "1")

        self.te.SetMarginType(2, stc.STC_MARGIN_NUMBER)
        self.te.SetMarginWidth(2, 30)
        self.te.StyleSetSpec(1, 'fore:#000000,back:#ADD8E6')
        self.te.StyleSetSpec(stc.STC_STYLE_LINENUMBER, 'fore:#000000,back:#ADD8E6')
        self.te.MarginSetStyle(0, 1)

        self.te.Refresh()

        self.Show()

app = wx.App()
MainWindow(None)
app.MainLoop()

mylist = [stc.STC_P_DEFAULT,
            stc.STC_P_COMMENTLINE,
            stc.STC_P_NUMBER,
            stc.STC_P_STRING,
            stc.STC_P_CHARACTER,
            stc.STC_P_WORD,
            stc.STC_P_WORD2,
            stc.STC_P_TRIPLE,
            stc.STC_P_TRIPLEDOUBLE,
            stc.STC_P_CLASSNAME,
            stc.STC_P_DEFNAME,
            stc.STC_P_OPERATOR,
            stc.STC_P_IDENTIFIER,
            stc.STC_P_COMMENTBLOCK,
            stc.STC_P_DECORATOR,
            stc.STC_P_STRINGEOL,
            stc.STC_STYLE_BRACELIGHT,
            stc.STC_STYLE_BRACEBAD,
          stc.STC_STYLE_LINENUMBER]

for x in mylist:
    print("{x}", x)