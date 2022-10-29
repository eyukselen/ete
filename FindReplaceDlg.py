import wx
from TextEditor import TextEditor


class FindReplaceDlg(wx.Dialog):
    def __init__(self, parent, notebook):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=u"Find - Replace", pos=wx.DefaultPosition,
                           size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.STAY_ON_TOP)
        self.SetMinSize((512, 310))

        # region left column in main sizer
        left_sizer = wx.BoxSizer(wx.VERTICAL)

        self.label_search_for = wx.StaticText(self, wx.ID_ANY, u"Search For:", wx.DefaultPosition, wx.DefaultSize, 0)
        left_sizer.Add(self.label_search_for, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        self.label_replace_with = wx.StaticText(self, wx.ID_ANY, u"Replace With:", wx.DefaultPosition,
                                                wx.DefaultSize, 0)
        left_sizer.Add(self.label_replace_with, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        left_sizer.Add((0, 0), 1, wx.EXPAND, 5)

        options_static_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"Options"), wx.VERTICAL)
        self.check_match_case = wx.CheckBox(options_static_sizer.GetStaticBox(), wx.ID_ANY, u"Match Case",
                                            wx.DefaultPosition, wx.DefaultSize, 0)
        options_static_sizer.Add(self.check_match_case, 0, wx.ALIGN_LEFT, 5)

        self.check_whole_word = wx.CheckBox(options_static_sizer.GetStaticBox(), wx.ID_ANY, u"Whole Word",
                                            wx.DefaultPosition, wx.DefaultSize, 0)
        options_static_sizer.Add(self.check_whole_word, 0, wx.ALIGN_LEFT, 5)

        self.check_wraparound = wx.CheckBox(options_static_sizer.GetStaticBox(), wx.ID_ANY, u"Wrap Around",
                                            wx.DefaultPosition, wx.DefaultSize, 0)
        options_static_sizer.Add(self.check_wraparound, 0, wx.ALIGN_LEFT, 5)
        self.check_wraparound.SetValue(True)

        left_sizer.Add(options_static_sizer, 1, wx.EXPAND, 5)

        # endregion

        # region middle column in main sizer

        middle_sizer = wx.BoxSizer(wx.VERTICAL)

        self.text_find_str = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        middle_sizer.Add(self.text_find_str, 0, wx.ALL | wx.EXPAND, 5)

        self.text_replace_str = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        middle_sizer.Add(self.text_replace_str, 0, wx.ALL | wx.EXPAND, 5)

        middle_sizer.Add((0, 0), 1, wx.EXPAND, 5)

        direction_static_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"Direction"), wx.HORIZONTAL)

        self.radio_up = wx.RadioButton(direction_static_sizer.GetStaticBox(), wx.ID_ANY, u"Up", wx.DefaultPosition,
                                       wx.DefaultSize, wx.RB_GROUP)
        direction_static_sizer.Add(self.radio_up, 0, wx.ALL, 5)

        self.radio_down = wx.RadioButton(direction_static_sizer.GetStaticBox(), wx.ID_ANY, u"Down", wx.DefaultPosition,
                                         wx.DefaultSize, 0)
        self.radio_down.SetValue(True)
        direction_static_sizer.Add(self.radio_down, 0, wx.ALL, 5)

        middle_sizer.Add(direction_static_sizer, 0, wx.LEFT, 5)

        # endregion

        # region right column in main sizer

        right_sizer = wx.BoxSizer(wx.VERTICAL)

        self.button_find_next = wx.Button(self, wx.ID_ANY, u"Find Next", wx.DefaultPosition, wx.DefaultSize, 0)
        right_sizer.Add(self.button_find_next, 0, wx.ALL | wx.EXPAND, 5)

        self.button_count_all = wx.Button(self, wx.ID_ANY, u"Count All", wx.DefaultPosition, wx.DefaultSize, 0)
        right_sizer.Add(self.button_count_all, 0, wx.ALL | wx.EXPAND, 5)

        self.button_replace = wx.Button(self, wx.ID_ANY, u"Replace", wx.DefaultPosition, wx.DefaultSize, 0)
        right_sizer.Add(self.button_replace, 0, wx.ALL | wx.EXPAND, 5)

        self.button_replace_all = wx.Button(self, wx.ID_ANY, u"Replace All", wx.DefaultPosition, wx.DefaultSize, 0)
        right_sizer.Add(self.button_replace_all, 0, wx.ALL | wx.EXPAND, 5)

        # endregion

        # region main sizer
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(left_sizer, 0, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(middle_sizer, 3, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(right_sizer, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(main_sizer)
        self.Layout()
        main_sizer.Fit(self)

        # endregion

        self.Centre(wx.BOTH)
        self.text_find_str.SetFocus()

        self.button_find_next.Bind(wx.EVT_BUTTON, self.on_find_next)
        self.button_count_all.Bind(wx.EVT_BUTTON, self.on_count)
        self.button_replace.Bind(wx.EVT_BUTTON, self.on_replace)
        self.button_replace_all.Bind(wx.EVT_BUTTON, self.on_replace_all)

        self.notebook = notebook

    def get_current_text_editor(self):
        cp = self.notebook.GetCurrentPage()
        for widget in cp.GetChildren():
            if isinstance(widget, TextEditor):
                return widget
        return None

    def get_flags(self):
        flags = 0
        if self.check_match_case.GetValue():
            flags |= wx.stc.STC_FIND_MATCHCASE
        if self.check_whole_word.GetValue():
            flags |= wx.stc.STC_FIND_WHOLEWORD
        return flags

    def on_find_next(self, _):
        te = self.get_current_text_editor()
        flags = self.get_flags()
        search_start = max(te.GetCurrentPos(), te.GetAnchor())
        search_end = te.GetTextLength()
        search_str = self.text_find_str.GetValue()
        if not self.radio_down.GetValue():
            search_start = min(te.GetCurrentPos(), te.GetAnchor())
            search_end = 0

        res, find_end = te.FindText(search_start, search_end, search_str, flags)
        if res == -1:
            if self.check_wraparound.GetValue():  # wrap enabled
                if search_end != 0:  # forward wrap
                    res, find_end = te.FindText(0, search_end, search_str, flags)
                    if res == -1:
                        msg = 'Nothing found!'
                        wx.MessageBox(message=msg, caption='Warning!', style=wx.OK | wx.ICON_WARNING)
                    else:
                        te.SetSelection(res, res + len(search_str))
                else:  # backward wrap
                    res, find_end = te.FindText(te.GetTextLength(), 0, search_str, flags)
                    if res == -1:
                        msg = 'Nothing found!'
                        wx.MessageBox(message=msg, caption='Warning!', style=wx.OK | wx.ICON_WARNING)
                    else:
                        te.SetCurrentPos(res)
                        te.SetAnchor(res + len(search_str))
                        te.Refresh()
            else:
                msg = 'Reached top of file!' if search_end == 0 else 'Reached end of file!'
                wx.MessageBox(message=msg, caption='Warning!', style=wx.OK | wx.ICON_WARNING)

        else:
            if search_end == 0:  # backwards search
                te.SetCurrentPos(res)
                te.SetAnchor(res + len(search_str))  # need to call refresh to make selection visible
                te.Refresh()
            else:
                te.SetSelection(res, res + len(search_str))

    def on_count(self, _):
        cnt = 0
        te = self.get_current_text_editor()
        flags = self.get_flags()
        search_start = 0
        search_end = te.GetTextLength()
        search_str = self.text_find_str.GetValue()
        fin = True
        while fin:
            res, find_end = te.FindText(search_start, search_end, search_str, flags)
            if res == -1:
                fin = False
            else:
                cnt += 1
                search_start = res + len(search_str)
        if cnt > 0:
            msg = 'Found ' + str(cnt) + ' match' + ('es!' if cnt > 1 else '!')
        else:
            msg = 'Found no match!'
        wx.MessageBox(message=msg, caption='Counted!', style=wx.OK | wx.ICON_INFORMATION)

    def on_replace(self, _):
        te = self.get_current_text_editor()
        search_str = self.text_find_str.GetValue()
        replace_str = self.text_replace_str.GetValue()
        selected_str = te.GetSelectedText()
        if search_str == selected_str:
            te.ReplaceSelection(replace_str)
            self.on_find_next(None)
        else:
            self.on_find_next(None)

    def on_replace_all(self, _):
        cnt = 0
        te = self.get_current_text_editor()
        flags = self.get_flags()
        search_start = 0
        search_end = te.GetTextLength()
        search_str = self.text_find_str.GetValue()
        replace_str = self.text_replace_str.GetValue()
        fin = True
        while fin:
            res, find_end = te.FindText(search_start, search_end, search_str, flags)
            if res == -1:
                fin = False
            else:
                cnt += 1
                te.Replace(res, res + len(search_str), replace_str)
                search_start = res + len(search_str)
        if cnt > 0:
            msg = 'Replaced ' + str(cnt) + ' occurrence' + ('s!' if cnt > 1 else '!')
        else:
            msg = 'Found no match!'
        wx.MessageBox(message=msg, caption='Replaced!', style=wx.OK | wx.ICON_INFORMATION)
