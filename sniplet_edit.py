import wx


class Sniplet_Editor(wx.Dialog):
    def __init__(self, parent, snip_name, snip_body):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=u"Edit Sniplet", pos=wx.DefaultPosition,
                           size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.STAY_ON_TOP)
        self.SetMinSize((512, 310))
        self.snip_name = snip_name
        self.snip_body = snip_body

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        label_sniplet_name = wx.StaticText(self, id=wx.ID_ANY, 
                                           label="Sniplet Name:")
        main_sizer.Add(label_sniplet_name, 0, wx.ALIGN_LEFT | wx.ALL, 1)

        self.textctrl_name = wx.TextCtrl(self, wx.ID_ANY, self.snip_name)
        main_sizer.Add(self.textctrl_name, 0, wx.ALL | wx.EXPAND, 1)

        label_sniplet_body = wx.StaticText(self, id=wx.ID_ANY, 
                                           label=u"Sniplet Body")
        main_sizer.Add(label_sniplet_body, 0, wx.ALIGN_LEFT | wx.ALL, 1)

        self.textctrl_body = wx.TextCtrl(self, wx.ID_ANY, self.snip_body, 
                                         style=wx.TE_MULTILINE)
        main_sizer.Add(self.textctrl_body, 1, wx.ALL | wx.EXPAND, 1)

        button_cancel = wx.Button(self, wx.ID_CANCEL, "Cancel")
        main_sizer.Add(button_cancel, 0, wx.ALIGN_RIGHT, 1)
        button_ok = wx.Button(self, wx.ID_OK, "OK")
        main_sizer.Add(button_ok, 0, wx.ALIGN_RIGHT, 1)

        button_cancel.Bind(wx.EVT_BUTTON, self.on_cancel)
        button_ok.Bind(wx.EVT_BUTTON, self.on_ok)

        self.SetSizer(main_sizer)
        self.Layout()
        main_sizer.Fit(self)
        self.Refresh()

    def on_cancel(self, _):
        self.EndModal(wx.ID_CANCEL)

    def on_ok(self, _):
        self.snip_name = self.textctrl_name.GetValue()
        self.snip_body = self.textctrl_body.GetValue()
        self.EndModal(wx.ID_OK)


# app = wx.App()
# dlg = Sniplet_Editor(None, 'new 1', 'this is \n the note\nthanks\nemre')
# res = dlg.ShowModal()
# if res == wx.ID_OK:
#     snip_name = dlg.snip_name
#     snip_body = dlg.snip_body
#     print(snip_name)
#     print(snip_body)
# if res == wx.ID_CANCEL:
#     print('cancelled')
# dlg.Destroy()


