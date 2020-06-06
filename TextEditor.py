import wx
import wx.stc as stc


class TextEditor(wx.stc.StyledTextCtrl):

    def __init__(self, parent, filename=''):
        stc.StyledTextCtrl.__init__(self, parent, style=wx.SIMPLE_BORDER)
        self.ID_MARGIN_CLICK = wx.ID_ANY
        self.FOLD_MARGIN = 2
        self.check_for_braces = False
        self.file_name = filename
        self.lang = ''
        self.folding = False
        self.status_bar = self.GetParent().GetParent().GetParent().GetParent().status_bar
        self.Bind(stc.EVT_STC_UPDATEUI, self.on_update_ui)
        self.Bind(stc.EVT_STC_ZOOM, self.on_update_ui)
        self.Bind(wx.EVT_RIGHT_UP, self.on_popup)
        self.UsePopUp(False)
        self.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
        self.set_styles()
        self.set_margins()

        # region styling

        self.txt_fore = 'BLACK'
        self.txt_back = 'WHITE'
        self.txt_size = '10'
        self.txt_face = 'Courier New'
        self.txt_bold = ''  # "bold" or ""
        self.txt_italic = ''  # "italic" or ""
        self.txt_underline = ''  # "underline" or ""

        style_spec = "fore:" + self.txt_fore + ",back:" + self.txt_back + \
                     ",size:" + self.txt_size + ",face:" + self.txt_face + "," + \
                     self.txt_bold + "," + self.txt_italic + "," + self.txt_underline
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT, style_spec)
        self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT, "fore:RED,back:MEDIUM TURQUOISE,bold")
        self.StyleSetSpec(stc.STC_STYLE_BRACEBAD, "fore:RED,back:THISTLE,bold")

        self.SetCaretWidth(2)  # caret feels better a little thicker

        # selection style and current line coloring
        selection_color = wx.Colour(red=128, green=219, blue=255, alpha=wx.ALPHA_OPAQUE)
        current_line_color = wx.Colour(red=216, green=255, blue=255, alpha=wx.ALPHA_OPAQUE)
        self.SetSelBackground(True, selection_color)
        self.SetCaretLineBackground(current_line_color)
        self.SetCaretLineVisible(True)

        # endregion

        # region context menu
        self.menu_popup = wx.Menu()
        menu_popup_undo = wx.MenuItem(self.menu_popup, wx.ID_UNDO, "Undo")
        self.menu_popup.Append(menu_popup_undo)
        self.Bind(wx.EVT_MENU, self.undo, menu_popup_undo)

        menu_popup_redo = wx.MenuItem(self.menu_popup, wx.ID_REDO, "Redo")
        self.menu_popup.Append(menu_popup_redo)
        self.Bind(wx.EVT_MENU, self.redo, menu_popup_redo)

        self.menu_popup.AppendSeparator()

        menu_popup_cut = wx.MenuItem(self.menu_popup, wx.ID_CUT, "Cut")
        self.menu_popup.Append(menu_popup_cut)
        self.Bind(wx.EVT_MENU, self.oncut, menu_popup_cut)

        menu_popup_copy = wx.MenuItem(self.menu_popup, wx.ID_COPY, "Copy")
        self.menu_popup.Append(menu_popup_copy)
        self.Bind(wx.EVT_MENU, self.copy, menu_popup_copy)

        menu_popup_paste = wx.MenuItem(self.menu_popup, wx.ID_PASTE, "Paste")
        self.menu_popup.Append(menu_popup_paste)
        self.Bind(wx.EVT_MENU, self.paste, menu_popup_paste)

        menu_popup_delete = wx.MenuItem(self.menu_popup, wx.ID_DELETE, "Delete")
        self.menu_popup.Append(menu_popup_delete)
        self.Bind(wx.EVT_MENU, self.delete, menu_popup_delete)

        self.menu_popup.AppendSeparator()

        menu_popup_select_all = wx.MenuItem(self.menu_popup, wx.ID_SELECTALL, "Select All")
        self.menu_popup.Append(menu_popup_select_all)
        self.Bind(wx.EVT_MENU, self.select_all, menu_popup_select_all)

        # endregion
        self.SetUseAntiAliasing(True)  # this is new with wxPython 4.1
        self.Refresh()

    def undo(self, _):
        self.Undo()

    def redo(self, _):
        self.Redo()

    def oncut(self, _):
        self.Cut()

    def copy(self, _):
        self.Copy()

    def paste(self, _):
        self.Paste()

    def delete(self, _):
        if self.GetSelectedText():
            self.Clear()

    def select_all(self, _):
        self.SelectAll()

    def on_popup(self, event):
        self.PopupMenu(self.menu_popup, pos=event.GetPosition())
        event.Skip()

    def set_margins(self):
        line_width = self.TextWidth(wx.stc.STC_STYLE_LINENUMBER,
                                    '9' + '9' * len(str(self.GetFirstVisibleLine() + self.LinesOnScreen())))
        self.SetMarginWidth(1, line_width)

    def on_receive_event(self, event):
        # if event.GetId() == wx.ID_FIND:
        #     print('find requested')
        #     event.StopPropagation()
        # if for an event I dont process it here or stop propagation, it will propagate up to parent class and
        # will be sent to here from parent class with on_menu_edit_event method. It will keep in a loop forever!
        wx.PostEvent(self.GetEventHandler(), event)
        # self.GetEventHandler().ProcessEvent(event)
        # wx.PostEvent is better than wx.ProcessEvent but in practise there is no difference
        # (may be process in process event is noun not verb!)
        # self.QueueEvent(event)  # this is processing event and exiting application which is not usable
        event.Skip()

    def on_update_ui(self, event):
        cursor, anchor = self.GetSelection()  # switching cursor and anchor returning cursor smaller
        line_num = self.GetCurrentLine() + 1
        col_num = self.GetColumn(self.GetCurrentPos())
        sel_len = abs(cursor - anchor)
        self.status_bar.SetStatusText('line:' + str(line_num) + ' col :' + str(col_num) + ' Sel:' + str(sel_len), 1)
        if cursor != anchor:
            if self.IsRangeWord(cursor, anchor):
                self.indicate_words(self.GetSelectedText())
        else:
            self.indicate_words('', True)

        self.set_margins()  # update line numbers margin width when UI updates
        self.check_braces()
        event.Skip()            

    def check_braces(self):
        cp = self.GetCurrentPos()
        # cc = self.GetCharAt(cp)  # for out of range GetCharAt is not giving error just returning 0
        if chr(self.GetCharAt(cp)) in "[]{}()<>":  # found after caret
            bm = self.BraceMatch(cp)
            if bm != -1:  # found matching brace
                self.BraceHighlight(cp, bm)
                self.check_for_braces = True
            else:
                self.BraceBadLight(cp)
                self.check_for_braces = True
        elif chr(self.GetCharAt(cp - 1)) in "[]{}()<>":  # found before caret
            bm = self.BraceMatch(cp - 1)
            if bm != -1:  # found matching brace
                self.BraceHighlight(cp - 1, bm)
                self.check_for_braces = True
            else:
                self.BraceBadLight(cp - 1)
                self.check_for_braces = True
        elif self.check_for_braces:
            self.BraceHighlight(-1, -1)
            self.check_for_braces = False

    def set_case(self, case):
        if case == 'upper':
            self.UpperCase()
        if case == 'lower':
            self.LowerCase()

    def set_lang(self, lang):
        if lang == 'python':
            self.lang = 'python'
            self.lang_python()
        if lang == 'mssql':
            self.lang = 'mssql'
            self.lang_mssql()
        if lang == 'text':
            self.lang_txt()

    def set_folding(self, fold=False):
        if fold:
            self.folding = True
            self.SetProperty('fold', '1')  # this needs to be send to stc
            self.SetMarginType(2, wx.stc.STC_MARGIN_SYMBOL)
            self.SetMarginMask(2, wx.stc.STC_MASK_FOLDERS)
            self.SetMarginSensitive(self.FOLD_MARGIN, True)
            self.SetMarginWidth(2, 16)
            self.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNERCURVE, "WHEAT", "#808080")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN, stc.STC_MARK_BOXMINUS, "WHEAT", "#808080")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDER, stc.STC_MARK_BOXPLUS, "WHEAT", "#808080")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB, stc.STC_MARK_VLINE, "WHEAT", "#808080")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL, stc.STC_MARK_LCORNER, "WHEAT", "#808080")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDEREND, stc.STC_MARK_BOXPLUSCONNECTED, "WHEAT", "#808080")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_BOXMINUSCONNECTED, "WHEAT", "#808080")
            self.SetAutomaticFold(wx.stc.STC_AUTOMATICFOLD_SHOW)
            self.Bind(wx.stc.EVT_STC_MARGINCLICK, self.on_margin_click, id=self.ID_MARGIN_CLICK)
        else:
            self.folding = False
            self.SetProperty('fold', '0')  # this needs to be send to stc
            self.SetMarginWidth(self.FOLD_MARGIN, 0)
            self.SetMarginSensitive(self.FOLD_MARGIN, False)
            self.Unbind(wx.stc.EVT_STC_MARGINCLICK, id=self.ID_MARGIN_CLICK)

    def on_margin_click(self, event):
        print(' margin clicked')
        print(event.GetMargin())
        if event.GetMargin() == self.FOLD_MARGIN:
            line_clicked = self.LineFromPosition(event.GetPosition())
            print(line_clicked)
            self.ToggleFold(line_clicked)

    def lang_python(self):
        self.StyleClearAll()
        self.SetLexer(stc.STC_LEX_PYTHON)
        self.SetKeyWords(0, 'False None True and as assert async await break class continue def del elif else '
                            'except finally for from global if import in is lambda nonlocal not or pass raise '
                            'return try while with yield')
        self.StyleSetSpec(stc.STC_P_DEFAULT, 'fore:#000000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_P_COMMENTLINE, 'fore:#008000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_P_NUMBER, 'fore:#FF0000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_P_STRING, 'fore:#808080,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_P_CHARACTER, 'fore:#808080,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_P_WORD, 'fore:#0000FF,back:#FFFFFF,bold')
        self.StyleSetSpec(stc.STC_P_WORD2, 'fore:#880088,back:#FFFFFF,bold')
        self.StyleSetSpec(stc.STC_P_TRIPLE, 'fore:#FF8000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_P_TRIPLEDOUBLE, 'fore:#FF8000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_P_CLASSNAME, 'fore:#000000,back:#FFFFFF,bold')
        self.StyleSetSpec(stc.STC_P_DEFNAME, 'fore:#FF00FF,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_P_OPERATOR, 'fore:#000080,back:#FFFFFF,bold')
        self.StyleSetSpec(stc.STC_P_IDENTIFIER, 'fore:#000000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_P_COMMENTBLOCK, 'fore:#008000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_P_DECORATOR, 'fore:#FF8000,back:#FFFFFF,italic')
        self.StyleSetSpec(stc.STC_P_STRINGEOL, 'fore:#RED,back:#FFFFFF,underline')
        self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT, "fore:RED,back:MEDIUM TURQUOISE,bold")
        self.StyleSetSpec(stc.STC_STYLE_BRACEBAD, "fore:RED,back:THISTLE,bold")
        self.SetProperty("tab.timmy.whinge.level", "1")  # to mark inconsistent indentation
        self.set_folding(True)

    def lang_txt(self):
        self.StyleClearAll()
        self.SetLexer(stc.STC_LEX_NULL)
        self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT, "fore:RED,back:MEDIUM TURQUOISE,bold")
        self.StyleSetSpec(stc.STC_STYLE_BRACEBAD, "fore:RED,back:THISTLE,bold")
        self.set_folding(False)

    def lang_mssql(self):
        self.StyleClearAll()
        self.SetLexer(stc.STC_LEX_MSSQL)
        self.SetKeyWords(0, "add external procedure all fetch public alter file raiserror and fillfactor read any for "
                            "readtext as foreign reconfigure asc freetext references authorization freetexttable "
                            "replication backup from restore begin full restrict between function return break goto "
                            "revert browse grant revoke bulk group right by having rollback cascade holdlock rowcount "
                            "case identity rowguidcol check identity_insert rule checkpoint identitycol save close if "
                            "schema clustered in securityaudit coalesce index select collate inner column insert "
                            "semantickeyphrasetable semanticsimilaritydetailstable commit intersect constraint join "
                            "semanticsimilaritytable compute into session_user is set contains  setuser containstable "
                            "key shutdown continue kill some convert left primary within group exists load tablesample "
                            "statistics create like system_user cross lineno table current current_date merge nocheck "
                            "textsize current_time national then current_timestamp current_user nonclustered openxml "
                            "top cursor not tran database null transaction dbcc nullif to deallocate of truncate "
                            "declare off try_convert default offsets tsequal delete on union deny open unique desc "
                            "opendatasource writetext exit proc percent when escape option"
                            "unpivot disk openquery update distinct openrowset updatetext distributed use double "
                            "user drop or values dump order varying else outer view end over waitfor errlvl "
                            "pivot where except plan while exec precision with execute print trigger")
        self.StyleSetSpec(stc.STC_MSSQL_DEFAULT, 'fore:#000000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_MSSQL_COMMENT, 'fore:#838383')
        self.StyleSetSpec(stc.STC_MSSQL_COLUMN_NAME, 'fore:#A52B2B, bold')
        self.StyleSetSpec(stc.STC_MSSQL_COLUMN_NAME_2, 'fore:#2E8B57, bold')
        self.StyleSetSpec(stc.STC_MSSQL_DATATYPE, 'fore:#2E8B57, bold')
        self.StyleSetSpec(stc.STC_MSSQL_DEFAULT_PREF_DATATYPE, 'fore:#2E8B57, bold')
        self.StyleSetSpec(stc.STC_MSSQL_FUNCTION, 'fore:#008B8B, bold')
        self.StyleSetSpec(stc.STC_MSSQL_GLOBAL_VARIABLE, 'fore:#007F7F')
        self.StyleSetSpec(stc.STC_MSSQL_IDENTIFIER, 'fore:#000000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_MSSQL_LINE_COMMENT, 'fore:#838383')
        self.StyleSetSpec(stc.STC_MSSQL_NUMBER, 'fore:#DD0101')
        self.StyleSetSpec(stc.STC_MSSQL_OPERATOR, 'Fore:#000000, bold')
        self.StyleSetSpec(stc.STC_MSSQL_STATEMENT, 'fore:#2E8B57, bold')
        self.StyleSetSpec(stc.STC_MSSQL_STORED_PROCEDURE, 'fore:#AB37F2, bold')
        self.StyleSetSpec(stc.STC_MSSQL_STRING, 'fore:#FF3AFF, bold')
        self.StyleSetSpec(stc.STC_MSSQL_SYSTABLE, 'fore:#9D2424')
        self.StyleSetSpec(stc.STC_MSSQL_VARIABLE, 'fore:#AB37F2')
        self.StyleSetSpec(stc.STC_P_STRINGEOL, 'fore:#000000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT, "fore:RED,back:MEDIUM TURQUOISE,bold")
        self.StyleSetSpec(stc.STC_STYLE_BRACEBAD, "fore:RED,back:THISTLE,bold")

    def set_styles(self):
        self.StyleSetSpec(4, 'back:TURQUOISE')  # style set 4 for compare matched line
        self.StyleSetSpec(5, 'back:WHEAT')  # style set 5 for compare unmatched line
        self.StyleSetEOLFilled(4, True)
        self.StyleSetEOLFilled(5, True)
        self.SetIndicatorCurrent(9)
        self.IndicatorSetStyle(9, stc.STC_INDIC_ROUNDBOX)  # style set 9 for matched search word indicator
        self.IndicatorSetForeground(9, 'BLUE')

    def indicate_words(self, word, clear=False):
        start = self.XYToPosition(0, self.GetFirstVisibleLine())
        length = self.GetLineEndPosition(self.GetFirstVisibleLine() + self.LinesOnScreen()) - start
        self.IndicatorClearRange(0, self.GetTextLength() - 1)
        if clear:
            return
        fin = True
        while fin:
            res, find_end = self.FindText(start, start + length, word, stc.STC_FIND_WHOLEWORD)
            if res == -1:
                fin = False
            else:
                self.IndicatorFillRange(res, len(word))
                start = res + len(word)
