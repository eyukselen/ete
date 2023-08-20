import wx
import wx.stc as stc
from configs import EID, keywords


class TextEditor(wx.stc.StyledTextCtrl):
    def __init__(self, parent=None, filename='', status_bar=None):
        stc.StyledTextCtrl.__init__(self, parent, style=wx.SIMPLE_BORDER)
        self.ID_MARGIN_CLICK = wx.ID_ANY
        self.markers = {}
        self.FOLD_MARGIN = 2
        self.LINE_NUMBERS_MARGIN = 0
        self.MARKER_MARGIN = 1
        self.MARKER_BOOKMARK = 4
        self.MARKER_PLUS = 5
        self.MARKER_MINUS = 6
        self.MarkerDefine(self.MARKER_PLUS, self.MARKER_PLUS,
                          foreground="RED", background="BLACK")
        self.MarkerDefine(self.MARKER_MINUS, self.MARKER_MINUS,
                          foreground="RED", background="BLACK")
        self.check_for_braces = False
        self.SetMultipleSelection(False)
        self.file_name = filename
        self.lang = EID.LANG_TXT
        self.code_page = ''
        self.style_no = 0
        self.folding = False
        self.status_bar = status_bar
        self.Bind(stc.EVT_STC_UPDATEUI, self.on_update_ui)
        self.Bind(stc.EVT_STC_ZOOM, self.on_update_ui)
        self.Bind(wx.EVT_RIGHT_UP, self.on_popup)
        self.Bind(wx.stc.EVT_STC_MARGINCLICK, self.on_margin_click,
                  id=self.ID_MARGIN_CLICK)
        self.set_styles()
        self.set_margins()
        self.SetAdditionalSelectionTyping(True)
        self.SetMultipleSelection(True)
        # region styling

        self.txt_fore = 'BLACK'
        self.txt_back = 'WHITE'
        self.txt_size = '12'
        self.txt_face = 'Courier New'
        self.txt_bold = ''  # "bold" or ""
        self.txt_italic = ''  # "italic" or ""
        self.txt_underline = ''  # "underline" or ""

        style_spec = "fore:" + self.txt_fore + ",back:" + self.txt_back + \
                     ",size:" + self.txt_size + ",face:" + self.txt_face + \
                     "," + self.txt_bold + "," + self.txt_italic + \
                     "," + self.txt_underline
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT, style_spec)
        self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT,
                          "fore:RED,back:MEDIUM TURQUOISE,bold")
        self.StyleSetSpec(stc.STC_STYLE_BRACEBAD,
                          "fore:RED,back:THISTLE,bold")

        self.SetCaretWidth(2)  # caret feels better a little thicker

        # selection style and current line coloring
        selection_color = wx.Colour(red=128, green=219, blue=255,
                                    alpha=wx.ALPHA_OPAQUE)
        current_line_color = wx.Colour(red=216, green=255, blue=255,
                                       alpha=wx.ALPHA_OPAQUE)
        self.SetSelBackground(True, selection_color)
        self.SetSelEOLFilled(False)
        self.SetCaretLineBackground(current_line_color)
        self.SetCaretLineVisible(True)

        # endregion

        # region context menu
        self.menu_popup = wx.Menu()
        menu_popup_undo = wx.MenuItem(self.menu_popup, EID.EDIT_UNDO, "Undo")
        self.menu_popup.Append(menu_popup_undo)
        self.Bind(wx.EVT_MENU, self.undo, menu_popup_undo)

        menu_popup_redo = wx.MenuItem(self.menu_popup, EID.EDIT_REDO, "Redo")
        self.menu_popup.Append(menu_popup_redo)
        self.Bind(wx.EVT_MENU, self.redo, menu_popup_redo)

        self.menu_popup.AppendSeparator()

        menu_popup_cut = wx.MenuItem(self.menu_popup, EID.EDIT_CUT, "Cut")
        self.menu_popup.Append(menu_popup_cut)
        self.Bind(wx.EVT_MENU, self.oncut, menu_popup_cut)

        menu_popup_copy = wx.MenuItem(self.menu_popup, EID.EDIT_COPY, "Copy")
        self.menu_popup.Append(menu_popup_copy)
        self.Bind(wx.EVT_MENU, self.copy, menu_popup_copy)

        menu_popup_paste = wx.MenuItem(self.menu_popup, EID.EDIT_PASTE, "Paste")
        self.menu_popup.Append(menu_popup_paste)
        self.Bind(wx.EVT_MENU, self.paste, menu_popup_paste)
        self.Bind(wx.EVT_MENU, self.paste, id=5033)  # TODO what's this?

        menu_popup_delete = wx.MenuItem(self.menu_popup, EID.EDIT_DELETE, "Delete")
        self.menu_popup.Append(menu_popup_delete)
        self.Bind(wx.EVT_MENU, self.delete, menu_popup_delete)

        self.menu_popup.AppendSeparator()

        menu_popup_select_all = wx.MenuItem(self.menu_popup,
                                            EID.EDIT_SELECTALL,
                                            "Select All")
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
        # margins 0:markers, 1:line numbers, 2: folding options
        # margin 0 and 1 defined below, 2 is defined in code folding function
        # marker margin
        self.SetMarginType(self.MARKER_MARGIN, wx.stc.STC_MARGIN_SYMBOL)
        self.SetMarginMask(self.MARKER_MARGIN,  ~wx.stc.STC_MASK_FOLDERS)
        self.SetMarginSensitive(self.MARKER_MARGIN, True)
        self.SetMarginWidth(self.MARKER_MARGIN, 12)

        # diff markers
        self.MarkerDefine(self.MARKER_BOOKMARK, stc.STC_MARK_BOOKMARK,
                          'black', 'red')
        self.MarkerDefine(self.MARKER_PLUS, stc.STC_MARK_PLUS)
        self.MarkerDefine(self.MARKER_MINUS, stc.STC_MARK_MINUS)

        # Line Numbers
        self.SetMarginType(self.LINE_NUMBERS_MARGIN, wx.stc.STC_MARGIN_NUMBER)
        line_width = self.TextWidth(wx.stc.STC_STYLE_LINENUMBER, '9' + '9'
                                    * len(str(self.GetFirstVisibleLine()
                                              + self.LinesOnScreen())))
        self.SetMarginWidth(self.LINE_NUMBERS_MARGIN, line_width)
        self.StyleSetSpec(wx.stc.STC_STYLE_LINENUMBER,
                          'fore:#FFFFFF,back:#5f74A1')

    def on_receive_event(self, event):
        wx.PostEvent(self.GetEventHandler(), event)
        event.Skip()

    def on_update_ui(self, event):
        cursor, anchor = self.GetSelection()
        line_num = self.GetCurrentLine() + 1
        col_num = self.GetColumn(self.GetCurrentPos())
        sel_len = abs(cursor - anchor)
        self.status_bar.SetStatusText('line:' + str(line_num)
                                      + ' col :' + str(col_num)
                                      + ' Sel:' + str(sel_len), 1)
        self.indicate_selection()
        self.set_margins()
        self.check_braces()
        event.Skip()
        self.refresh()

    def refresh(self):
        # TODO: this needs to move out from on_update_ui
        self.update_toolbar_eol_mode()
        self.set_lang(self.lang)

    def get_eol_len(self):
        res = 1
        if self.GetEOLMode() == stc.STC_EOL_CRLF:
            res = 2
        return res

    def update_toolbar_eol_mode(self):
        eol_dict = {0: 'CRLF', 1: 'CR', 2: 'LF'}
        eol_mode = eol_dict.get(self.GetEOLMode(), 'N/A')
        self.status_bar.SetStatusText(str(eol_mode), 2)

    def check_braces(self):
        cp = self.GetCurrentPos()
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

    def set_eol(self, eol_mode):
        self.ConvertEOLs(eol_mode)
        self.SetEOLMode(eol_mode)

    def set_lang(self, lang=EID.LANG_TXT):

        langs = {EID.LANG_PYTHON: self.lang_python,
                 EID.LANG_BASH: self.lang_bash,
                 EID.LANG_HTML: self.lang_html,
                 EID.LANG_JSON: self.lang_json,
                 EID.LANG_MSSQL: self.lang_mssql,
                 EID.LANG_POWERSHELL: self.lang_ps,
                 EID.LANG_XML: self.lang_xml,
                 EID.LANG_TXT: self.lang_txt,
                 }

        f = langs[lang]
        self.lang = lang
        self.status_bar.SetStatusText(f.__name__[5:], 4)
        f()

    def set_folding(self, fold=False):
        if fold:
            self.folding = True
            self.SetProperty('fold', '1')  # this needs to be send to stc
            # TODO: below property needs to run only when lang=xml|html
            self.SetProperty("fold.html", "1")  # needed for html and xml
            self.SetMarginType(self.FOLD_MARGIN, wx.stc.STC_MARGIN_SYMBOL)
            self.SetMarginMask(self.FOLD_MARGIN, wx.stc.STC_MASK_FOLDERS)
            self.SetMarginSensitive(self.FOLD_MARGIN, True)
            self.SetMarginWidth(self.FOLD_MARGIN, 16)
            self.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL,
                              stc.STC_MARK_TCORNERCURVE,
                              "WHEAT", "#808080")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN,
                              stc.STC_MARK_BOXMINUS,
                              "WHEAT", "#808080")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDER,
                              stc.STC_MARK_BOXPLUS,
                              "WHEAT", "#808080")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB,
                              stc.STC_MARK_VLINE,
                              "WHEAT", "#808080")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL,
                              stc.STC_MARK_LCORNER,
                              "WHEAT", "#808080")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDEREND,
                              stc.STC_MARK_BOXPLUSCONNECTED,
                              "WHEAT", "#808080")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID,
                              stc.STC_MARK_BOXMINUSCONNECTED,
                              "WHEAT", "#808080")
            self.SetAutomaticFold(wx.stc.STC_AUTOMATICFOLD_SHOW)
            self.Bind(wx.stc.EVT_STC_MARGINCLICK,
                      self.on_margin_click,
                      id=self.ID_MARGIN_CLICK)
        else:
            self.folding = False
            self.SetProperty('fold', '0')  # this needs to be send to stc
            self.SetMarginWidth(self.FOLD_MARGIN, 0)
            self.SetMarginSensitive(self.FOLD_MARGIN, False)
            self.Unbind(wx.stc.EVT_STC_MARGINCLICK, id=self.ID_MARGIN_CLICK)

    def on_margin_click(self, event):
        if event.GetMargin() == self.FOLD_MARGIN:
            line_clicked = self.LineFromPosition(event.GetPosition())
            self.ToggleFold(line_clicked)
        elif event.GetMargin() == self.MARKER_MARGIN:
            line_clicked = self.LineFromPosition(event.GetPosition())
            if (line_clicked, self.MARKER_BOOKMARK) in self.markers.items():
                self.MarkerDelete(line_clicked, self.MARKER_BOOKMARK)
                self.markers.pop(line_clicked)
            else:
                self.MarkerAdd(line_clicked, self.MARKER_BOOKMARK)
                self.markers[line_clicked] = self.MARKER_BOOKMARK

    def lang_python(self):
        self.StyleClearAll()
        self.SetLexer(stc.STC_LEX_PYTHON)
        self.SetKeyWords(0, keywords['python']['keywords_0'])
        self.StyleSetSpec(stc.STC_P_DEFAULT, 'fore:#000000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_P_COMMENTLINE, 'fore:#008000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_P_NUMBER, 'fore:#FF0000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_P_STRING, 'fore:#808080,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_P_CHARACTER, 'fore:#808080,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_P_WORD, 'fore:#0000FF,back:#FFFFFF,bold')
        self.StyleSetSpec(stc.STC_P_WORD2, 'fore:#880088,back:#FFFFFF,bold')
        self.StyleSetSpec(stc.STC_P_TRIPLE, 'fore:#FF8000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_P_TRIPLEDOUBLE, 'fore:#FF8000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_P_CLASSNAME,
                          'fore:#000000,back:#FFFFFF,bold')
        self.StyleSetSpec(stc.STC_P_DEFNAME, 'fore:#FF00FF,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_P_OPERATOR, 'fore:#000080,back:#FFFFFF,bold')
        self.StyleSetSpec(stc.STC_P_IDENTIFIER, 'fore:#000000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_P_COMMENTBLOCK, 'fore:#008000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_P_DECORATOR,
                          'fore:#FF8000,back:#FFFFFF,italic')
        self.StyleSetSpec(stc.STC_P_STRINGEOL,
                          'fore:#RED,back:#FFFFFF,underline')
        self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT,
                          "fore:RED,back:MEDIUM TURQUOISE,bold")
        self.StyleSetSpec(stc.STC_STYLE_BRACEBAD, "fore:RED,back:THISTLE,bold")
        # to mark inconsistent indentation
        self.SetProperty("tab.timmy.whinge.level", "1")
        self.set_folding(True)

    def lang_ps(self):
        self.StyleClearAll()
        self.SetLexer(stc.STC_LEX_BASH)
        self.SetKeyWords(0, keywords['ps']['keywords_0'])
        self.SetKeyWords(1, keywords['ps']['keywords_1'])
        self.SetKeyWords(2, keywords['ps']['keywords_2'])
        self.SetKeyWords(3, keywords['ps']['keywords_3'])
        self.StyleSetSpec(stc.STC_POWERSHELL_ALIAS,
                          'fore:#0080FF,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_POWERSHELL_CHARACTER,
                          'fore:#808080,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_POWERSHELL_CMDLET,
                          'fore:#8000FF,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_POWERSHELL_COMMENT,
                          'fore:#008000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_POWERSHELL_COMMENTDOCKEYWORD,
                          'fore:#008080,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_POWERSHELL_COMMENTSTREAM,
                          'fore:#008080,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_POWERSHELL_DEFAULT,
                          'fore:#000000,back:#FFFFFF')
        # self.StyleSetSpec(stc.STC_POWERSHELL_FUNCTION,
        # 'fore:#880088,back:#FFFFFF,bold')
        self.StyleSetSpec(stc.STC_POWERSHELL_HERE_CHARACTER,
                          'fore:#808080,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_POWERSHELL_HERE_STRING,
                          'fore:#808080,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_POWERSHELL_IDENTIFIER,
                          'fore:#0000FF,back:#FFFFFF,bold')
        # self.StyleSetSpec(stc.STC_POWERSHELL_KEYWORD,
        # 'fore:#880088,back:#FFFFFF,bold')
        self.StyleSetSpec(stc.STC_POWERSHELL_NUMBER,
                          'fore:#FF8000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_POWERSHELL_OPERATOR,
                          'fore:#000080,back:#FFFFFF,bold')
        self.StyleSetSpec(stc.STC_POWERSHELL_STRING,
                          'fore:#808080,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_POWERSHELL_USER1,
                          'fore:#000000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_POWERSHELL_VARIABLE,
                          'fore:#000000,back:#FFFFFF,bold')

    def lang_bash(self):
        self.StyleClearAll()
        self.SetLexer(stc.STC_LEX_BASH)
        self.SetKeyWords(0, keywords['bash']['keywords_0'])
        self.StyleSetSpec(stc.STC_SH_BACKTICKS, 'fore:#FFFF00')
        self.StyleSetSpec(stc.STC_SH_NUMBER, 'fore:#FF00FF')
        self.StyleSetSpec(stc.STC_SH_CHARACTER, 'fore:#8DB0D3')
        self.StyleSetSpec(stc.STC_SH_COMMENTLINE, 'italic,fore:#00CFCB')
        self.StyleSetSpec(stc.STC_SH_DEFAULT, 'fore:#8DB0D3')
        self.StyleSetSpec(stc.STC_SH_ERROR, 'fore:#0000FF')
        self.StyleSetSpec(stc.STC_SH_HERE_DELIM, 'fore:#00FF80')
        self.StyleSetSpec(stc.STC_SH_HERE_Q, 'fore:#00FF80')
        self.StyleSetSpec(stc.STC_SH_IDENTIFIER, 'fore:#8DB0D3')
        self.StyleSetSpec(stc.STC_SH_OPERATOR, 'fore:#F0804F')
        self.StyleSetSpec(stc.STC_SH_PARAM, 'fore:#8DB0D3')
        self.StyleSetSpec(stc.STC_SH_SCALAR, 'fore:#FF00FF')
        self.StyleSetSpec(stc.STC_SH_STRING, 'fore:#00FF80')
        self.StyleSetSpec(stc.STC_SH_WORD, 'fore:#FFFF00')

    def lang_txt(self):
        self.StyleClearAll()
        self.SetLexer(stc.STC_LEX_NULL)
        self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT,
                          "fore:RED,back:MEDIUM TURQUOISE,bold")
        self.StyleSetSpec(stc.STC_STYLE_BRACEBAD,
                          "fore:RED,back:THISTLE,bold")
        self.set_folding(False)

    def lang_json(self):
        self.StyleClearAll()
        self.SetLexer(stc.STC_LEX_JSON)
        self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT,
                          "fore:RED,back:MEDIUM TURQUOISE,bold")
        self.StyleSetSpec(stc.STC_STYLE_BRACEBAD, "fore:RED,back:THISTLE,bold")
        self.set_folding(True)
        self.StyleSetSpec(stc.STC_JSON_BLOCKCOMMENT,
                          "fore:#008000,back:#FFFFFF")
        self.StyleSetSpec(stc.STC_JSON_COMPACTIRI, "fore:#0000FF,back:#FFFFFF")
        self.StyleSetSpec(stc.STC_JSON_DEFAULT, "fore:#000000,back:#FFFFFF")
        self.StyleSetSpec(stc.STC_JSON_ERROR, "fore:#FFFF80,back:#FF0000")
        self.StyleSetSpec(stc.STC_JSON_ESCAPESEQUENCE,
                          "fore:#0000FF,back:#FFFFFF")
        self.StyleSetSpec(stc.STC_JSON_KEYWORD, "fore:#18AF8A,back:#FFFFFF")
        self.StyleSetSpec(stc.STC_JSON_PROPERTYNAME,
                          "fore:#8000FF,back:#FFFFFF,bold")
        self.StyleSetSpec(stc.STC_JSON_LDKEYWORD, "fore:#FF0000,back:#FFFFFF")
        self.StyleSetSpec(stc.STC_JSON_LINECOMMENT,
                          "fore:#008000,back:#FFFFFF")
        self.StyleSetSpec(stc.STC_JSON_URI, "fore:#0000FF,back:#FFFFFF")
        self.StyleSetSpec(stc.STC_JSON_STRINGEOL, "fore=#808080,back:#FFFFFF")
        self.StyleSetSpec(stc.STC_JSON_NUMBER, "fore:#FF8000,back:#FFFFFF")
        self.StyleSetSpec(stc.STC_JSON_STRING, "fore:#800000,back:#FFFFFF")
        self.StyleSetSpec(stc.STC_JSON_OPERATOR, "fore:#000000,back:#FFFFFF")
        self.SetKeyWords(0, keywords['json']['keywords_0'])
        self.SetKeyWords(1, keywords['json']['keywords_1'])

    def lang_mssql(self):
        self.StyleClearAll()
        self.SetLexer(stc.STC_LEX_MSSQL)
        self.SetKeyWords(0, keywords['mssql']['keywords_0'])
        self.StyleSetSpec(stc.STC_MSSQL_DEFAULT, 'fore:#000000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_MSSQL_COMMENT, 'fore:#838383')
        self.StyleSetSpec(stc.STC_MSSQL_COLUMN_NAME, 'fore:#A52B2B, bold')
        self.StyleSetSpec(stc.STC_MSSQL_COLUMN_NAME_2, 'fore:#2E8B57, bold')
        self.StyleSetSpec(stc.STC_MSSQL_DATATYPE, 'fore:#2E8B57, bold')
        self.StyleSetSpec(stc.STC_MSSQL_DEFAULT_PREF_DATATYPE,
                          'fore:#2E8B57, bold')
        self.StyleSetSpec(stc.STC_MSSQL_FUNCTION, 'fore:#008B8B, bold')
        self.StyleSetSpec(stc.STC_MSSQL_GLOBAL_VARIABLE, 'fore:#007F7F')
        self.StyleSetSpec(stc.STC_MSSQL_IDENTIFIER,
                          'fore:#000000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_MSSQL_LINE_COMMENT, 'fore:#838383')
        self.StyleSetSpec(stc.STC_MSSQL_NUMBER, 'fore:#DD0101')
        self.StyleSetSpec(stc.STC_MSSQL_OPERATOR, 'Fore:#000000, bold')
        self.StyleSetSpec(stc.STC_MSSQL_STATEMENT, 'fore:#2E8B57, bold')
        self.StyleSetSpec(stc.STC_MSSQL_STORED_PROCEDURE, 'fore:#AB37F2, bold')
        self.StyleSetSpec(stc.STC_MSSQL_STRING, 'fore:#FF3AFF, bold')
        self.StyleSetSpec(stc.STC_MSSQL_SYSTABLE, 'fore:#9D2424')
        self.StyleSetSpec(stc.STC_MSSQL_VARIABLE, 'fore:#AB37F2')
        self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT,
                          "fore:RED,back:MEDIUM TURQUOISE,bold")
        self.StyleSetSpec(stc.STC_STYLE_BRACEBAD, "fore:RED,back:THISTLE,bold")

    def lang_xml(self):
        self.StyleClearAll()
        self.SetLexer(stc.STC_LEX_XML)
        # setting keywords 0 has an unexpected behaviour such as
        # tags and attributes are not styled as expected
        self.SetKeyWords(1, keywords['xml']['keywords_1'])
        self.StyleSetSpec(stc.STC_H_DEFAULT, 'fore:#000000,back:#FFFFFF,bold')
        self.StyleSetSpec(stc.STC_H_XMLSTART, 'fore:#FF0000,back:#FFFF00')
        self.StyleSetSpec(stc.STC_H_XMLEND, 'fore:#FF0000,back:#FFFF00')
        self.StyleSetSpec(stc.STC_H_COMMENT, 'fore:#008000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_H_NUMBER, 'fore:#FF0000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_H_DOUBLESTRING,
                          'fore:#8000FF,back:#FFFFFF,bold')
        self.StyleSetSpec(stc.STC_H_SINGLESTRING,
                          'fore:#8000FF,back:#FFFFFF,bold')
        self.StyleSetSpec(stc.STC_H_TAG, 'fore:#0000FF,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_H_TAGEND, 'fore:#0000FF,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_H_TAGUNKNOWN, 'fore:#0000FF,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_H_ATTRIBUTE, 'fore:#FF0000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_H_ATTRIBUTEUNKNOWN,
                          'fore:#FF0000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_H_SGML_DEFAULT, 'fore:#000000,back:#A6CAF0')
        self.StyleSetSpec(stc.STC_H_CDATA, 'fore:#FF8000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_H_ENTITY, 'fore:#000000,back:#FEFDE0,italic')
        self.StyleSetSpec(stc.STC_H_VALUE, 'fore:#000000,back:#A6CAF0')
        self.set_folding(True)

    def lang_html(self):
        self.StyleClearAll()
        self.SetLexer(stc.STC_LEX_HTML)
        self.SetKeyWords(1, keywords['html']['keywords_1'])
        self.StyleSetSpec(stc.STC_H_DEFAULT, 'fore:#000000,back:#FFFFFF,bold')
        self.StyleSetSpec(stc.STC_H_COMMENT, 'fore:#008000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_H_NUMBER, 'fore:#FF0000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_H_DOUBLESTRING,
                          'fore:#8000FF,back:#FFFFFF,bold')
        self.StyleSetSpec(stc.STC_H_SINGLESTRING,
                          'fore:#8000FF,back:#FFFFFF,bold')
        self.StyleSetSpec(stc.STC_H_TAG, 'fore:#0000FF,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_H_TAGEND, 'fore:#0000FF,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_H_TAGUNKNOWN, 'fore:#000000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_H_ATTRIBUTE, 'fore:#FF0000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_H_ATTRIBUTEUNKNOWN,
                          'fore:#000000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_H_SGML_DEFAULT, 'fore:#000000,back:#A6CAF0')
        self.StyleSetSpec(stc.STC_H_CDATA, 'fore:#FF8000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_H_VALUE, 'fore:#000000,back:#A6CAF0')
        self.StyleSetSpec(stc.STC_H_ENTITY, 'fore:#000000,back:#FEFDE0,italic')

    def set_styles(self):
        # style set 4 for compare matched line
        self.StyleSetSpec(4, 'back:TURQUOISE')
        # style set 5 for compare unmatched line
        self.StyleSetSpec(5, 'back:WHEAT')
        self.StyleSetEOLFilled(4, True)
        self.StyleSetEOLFilled(5, True)
        self.SetIndicatorCurrent(9)
        # style set 9 for matched search word indicator
        self.IndicatorSetStyle(9, stc.STC_INDIC_ROUNDBOX)
        self.IndicatorSetForeground(9, 'BLUE')

    def indicate_selection(self):
        if self.GetSelectionEmpty():
            self.IndicatorClearRange(0, self.GetTextLength())
        else:
            sel_start, sel_end = self.GetSelection()  # get selection range
            self.IndicatorClearRange(0, self.GetTextLength())
            if self.IsRangeWord(sel_start, sel_end):
                vis_start = self.XYToPosition(0, self.GetFirstVisibleLine())
                vis_end = self.GetLineEndPosition(
                    self.GetFirstVisibleLine() + self.LinesOnScreen())
                chk = True
                while chk:
                    found_start, found_end = self.FindText(
                                                vis_start,
                                                vis_end,
                                                self.GetSelectedText(),
                                                stc.STC_FIND_WHOLEWORD)
                    if found_start == -1:
                        break
                    else:
                        self.IndicatorFillRange(found_start,
                                                found_end - found_start)
                        vis_start += found_end - found_start
            else:
                self.IndicatorFillRange(sel_start, sel_end)

    def load_file(self, file):
        with open(file, 'rb') as ff:
            f = ff.read()

        if self.is_utf8(f):
            self.code_page = 'utf-8'
            self.SetTextRaw(f)
            self.status_bar.SetStatusText('utf-8', 3)
            self.SetModified(False)
        else:
            self.code_page = 'windows-1252'
            self.SetText(f.decode('windows-1252'))
            self.status_bar.SetStatusText('windows-1252', 3)
            self.SetModified(False)

    def save_file(self, file):
        f = open(file, 'w', encoding=self.code_page, newline='')
        f.write(self.GetText())
        self.SetSavePoint()
        f.close()

    def is_utf8(self, data):
        try:
            data.decode('UTF-8')
        except UnicodeDecodeError:
            return False
        else:
            return True
