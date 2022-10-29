import wx
import wx.stc as stc


class TextEditor(wx.stc.StyledTextCtrl):
    def __init__(self, parent, filename=''):
        stc.StyledTextCtrl.__init__(self, parent, style=wx.SIMPLE_BORDER)
        self.ID_MARGIN_CLICK = wx.ID_ANY
        self.markers = {}
        self.FOLD_MARGIN = 2
        self.LINE_NUMBERS_MARGIN = 0
        self.MARKER_MARGIN = 1
        self.MARKER_BOOKMARK = 4
        self.MARKER_PLUS = 5
        self.MARKER_MINUS = 6
        self.check_for_braces = False
        self.SetMultipleSelection(False)
        self.file_name = filename
        self.lang = ''
        self.code_page = ''
        self.style_no = 0
        self.folding = False
        self.status_bar = self.GetParent().GetParent().GetParent().GetParent().GetParent().status_bar
        self.Bind(stc.EVT_STC_UPDATEUI, self.on_update_ui)
        self.Bind(stc.EVT_STC_ZOOM, self.on_update_ui)
        self.Bind(wx.EVT_RIGHT_UP, self.on_popup)
        self.Bind(wx.stc.EVT_STC_MARGINCLICK, self.on_margin_click, id=self.ID_MARGIN_CLICK)
        self.set_styles()
        self.set_margins()
        self.SetAdditionalSelectionTyping(True)
        self.SetMultipleSelection(True)
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
        self.SetSelEOLFilled(False)
        self.SetCaretLineBackground(current_line_color)
        self.SetCaretLineVisible(True)

        # endregion

        # region context menu
        self.menu_popup = wx.Menu()
        menu_popup_undo = wx.MenuItem(self.menu_popup, 2001, "Undo")
        self.menu_popup.Append(menu_popup_undo)
        self.Bind(wx.EVT_MENU, self.undo, menu_popup_undo)

        menu_popup_redo = wx.MenuItem(self.menu_popup, 2002, "Redo")
        self.menu_popup.Append(menu_popup_redo)
        self.Bind(wx.EVT_MENU, self.redo, menu_popup_redo)

        self.menu_popup.AppendSeparator()

        menu_popup_cut = wx.MenuItem(self.menu_popup, 2003, "Cut")
        self.menu_popup.Append(menu_popup_cut)
        self.Bind(wx.EVT_MENU, self.oncut, menu_popup_cut)

        menu_popup_copy = wx.MenuItem(self.menu_popup, 2004, "Copy")
        self.menu_popup.Append(menu_popup_copy)
        self.Bind(wx.EVT_MENU, self.copy, menu_popup_copy)

        menu_popup_paste = wx.MenuItem(self.menu_popup, 2005, "Paste")
        self.menu_popup.Append(menu_popup_paste)
        self.Bind(wx.EVT_MENU, self.paste, menu_popup_paste)
        self.Bind(wx.EVT_MENU, self.paste, id=5033)

        menu_popup_delete = wx.MenuItem(self.menu_popup, 2009, "Delete")
        self.menu_popup.Append(menu_popup_delete)
        self.Bind(wx.EVT_MENU, self.delete, menu_popup_delete)

        self.menu_popup.AppendSeparator()

        menu_popup_select_all = wx.MenuItem(self.menu_popup, 2010, "Select All")
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
        # self.MarkerDefine(4, stc.STC_MARK_CHARACTER + ord('+'), "WHEAT", "#808080")
        # self.MarkerDefine(5, stc.STC_MARK_CHARACTER + ord('-'), "WHEAT", "#808080")
        # self.MarkerDefine(6, stc.STC_MARK_CHARACTER + ord('='), "WHEAT", "#808080")
        self.MarkerDefine(self.MARKER_BOOKMARK, stc.STC_MARK_BOOKMARK, 'black', 'red')
        self.MarkerDefine(self.MARKER_PLUS, stc.STC_MARK_PLUS)
        self.MarkerDefine(self.MARKER_MINUS, stc.STC_MARK_MINUS)

        # Line Numbers
        self.SetMarginType(self.LINE_NUMBERS_MARGIN, wx.stc.STC_MARGIN_NUMBER)
        line_width = self.TextWidth(wx.stc.STC_STYLE_LINENUMBER, '9' + '9' * len(str(self.GetFirstVisibleLine()
                                                                                     + self.LinesOnScreen())))
        self.SetMarginWidth(self.LINE_NUMBERS_MARGIN, line_width)
        self.StyleSetSpec(wx.stc.STC_STYLE_LINENUMBER, 'fore:#FFFFFF,back:#5f74A1')

    def on_receive_event(self, event):
        wx.PostEvent(self.GetEventHandler(), event)
        event.Skip()

    def on_update_ui(self, event):
        cursor, anchor = self.GetSelection()
        line_num = self.GetCurrentLine() + 1
        col_num = self.GetColumn(self.GetCurrentPos())
        sel_len = abs(cursor - anchor)
        self.status_bar.SetStatusText('line:' + str(line_num) + ' col :' + str(col_num) + ' Sel:' + str(sel_len), 1)
        self.indicate_selection()
        self.set_margins()
        self.update_toolbar_eol_mode()
        self.check_braces()
        event.Skip()

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

    def set_lang(self, lang):
        if lang == 'python':
            self.lang = 'python'
            self.lang_python()
        if lang == 'mssql':
            self.lang = 'mssql'
            self.lang_mssql()
        if lang == 'bash':
            self.lang = 'bash'
            self.lang_bash()
        if lang == 'ps':
            self.lang = 'ps'
            self.lang_ps()
        if lang == 'xml':
            self.lang = 'xml'
            self.lang_xml()
        if lang == 'html':
            self.lang = 'html'
            self.lang_html()
        if lang == 'json':
            self.lang = 'json'
            self.lang_json()
        if lang == 'txt':
            self.lang = 'txt'
            self.lang_txt()
        self.status_bar.SetStatusText(self.lang, 4)

    def set_folding(self, fold=False):
        if fold:
            self.folding = True
            self.SetProperty('fold', '1')  # this needs to be send to stc
            self.SetMarginType(self.FOLD_MARGIN, wx.stc.STC_MARGIN_SYMBOL)
            self.SetMarginMask(self.FOLD_MARGIN, wx.stc.STC_MASK_FOLDERS)
            self.SetMarginSensitive(self.FOLD_MARGIN, True)
            self.SetMarginWidth(self.FOLD_MARGIN, 16)
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
        self.SetKeyWords(0, 'False None True and as assert async await break class continue def del elif else '
                            'except finally for from global if import in is lambda nonlocal not or pass raise '
                            'return try while with yield self')
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

    def lang_ps(self):
        self.StyleClearAll()
        self.SetLexer(stc.STC_LEX_BASH)
        self.SetKeyWords(0, 'break continue do else elseif filter for foreach function if in return switch until '
                            'where while')
        self.SetKeyWords(1, 'add-content add-history add-member add-pssnapin clear-content clear-item '
                            'clear-itemproperty clear-variable compare-object convertfrom-securestring convert-path '
                            'convertto-html convertto-securestring copy-item copy-itemproperty export-alias '
                            'export-clixml export-console export-csv foreach-object format-custom format-list '
                            'format-table format-wide get-acl get-alias get-authenticodesignature get-childitem '
                            'get-command get-content get-credential get-culture get-date get-eventlog '
                            'get-executionpolicy get-help get-history get-host get-item get-itemproperty get-location '
                            'get-member get-pfxcertificate get-process get-psdrive get-psprovider get-pssnapin '
                            'get-service get-tracesource get-uiculture get-unique get-variable get-wmiobject '
                            'group-object import-alias import-clixml import-csv invoke-expression invoke-history '
                            'invoke-item join-path measure-command measure-object move-item move-itemproperty '
                            'new-alias new-item new-itemproperty new-object new-psdrive new-service new-timespan '
                            'new-variable out-default out-file out-host out-null out-printer out-string pop-location '
                            'push-location read-host remove-item remove-itemproperty remove-psdrive remove-pssnapin '
                            'remove-variable rename-item rename-itemproperty resolve-path restart-service '
                            'resume-service select-object select-string set-acl set-alias set-authenticodesignature '
                            'set-content set-date set-executionpolicy set-item set-itemproperty set-location '
                            'set-psdebug set-service set-tracesource set-variable sort-object split-path '
                            'start-service start-sleep start-transcript stop-process stop-service stop-transcript '
                            'suspend-service tee-object test-path trace-command update-formatdata update-typedata '
                            'where-object write-debug write-error write-host write-output write-progress '
                            'write-verbose write-warning')
        self.SetKeyWords(2, 'ac asnp clc cli clp clv cpi cpp cvpa diff epal epcsv fc fl foreach ft fw gal gc gci gcm '
                            'gdr ghy gi gl gm gp gps group gsv gsnp gu gv gwmi iex ihy ii ipal ipcsv mi mp nal ndr ni '
                            'nv oh rdr ri rni rnp rp rsnp rv rvpa sal sasv sc select si sl sleep sort sp spps spsv sv '
                            'tee where write cat cd clear cp h history kill lp ls mount mv popd ps pushd pwd r rm '
                            'rmdir echo cls chdir copy del dir erase move rd ren set type')
        self.SetKeyWords(3, 'component description example externalhelp forwardhelpcategory forwardhelptargetname '
                            'functionality inputs link notes outputs parameter remotehelprunspace role synopsis')
        self.StyleSetSpec(stc.STC_POWERSHELL_ALIAS, 'fore:#0080FF,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_POWERSHELL_CHARACTER, 'fore:#808080,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_POWERSHELL_CMDLET, 'fore:#8000FF,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_POWERSHELL_COMMENT, 'fore:#008000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_POWERSHELL_COMMENTDOCKEYWORD, 'fore:#008080,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_POWERSHELL_COMMENTSTREAM, 'fore:#008080,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_POWERSHELL_DEFAULT, 'fore:#000000,back:#FFFFFF')
        # self.StyleSetSpec(stc.STC_POWERSHELL_FUNCTION, 'fore:#880088,back:#FFFFFF,bold')
        self.StyleSetSpec(stc.STC_POWERSHELL_HERE_CHARACTER, 'fore:#808080,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_POWERSHELL_HERE_STRING, 'fore:#808080,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_POWERSHELL_IDENTIFIER, 'fore:#0000FF,back:#FFFFFF,bold')
        # self.StyleSetSpec(stc.STC_POWERSHELL_KEYWORD, 'fore:#880088,back:#FFFFFF,bold')
        self.StyleSetSpec(stc.STC_POWERSHELL_NUMBER, 'fore:#FF8000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_POWERSHELL_OPERATOR, 'fore:#000080,back:#FFFFFF,bold')
        self.StyleSetSpec(stc.STC_POWERSHELL_STRING, 'fore:#808080,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_POWERSHELL_USER1, 'fore:#000000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_POWERSHELL_VARIABLE, 'fore:#000000,back:#FFFFFF,bold')

    def lang_bash(self):
        self.StyleClearAll()
        self.SetLexer(stc.STC_LEX_BASH)
        self.SetKeyWords(0, '7z adduser alias apt-get ar as asa autoconf automake awk banner base64 basename bash '
                            'bc bdiff blkid break bsdcpio bsdtar bunzip2 bzcmp bzdiff bzegrep bzfgrep bzgrep bzip2 '
                            'bzip2recover bzless bzmore c++ cal calendar case cat cc cd cfdisk chattr chgrp chmod '
                            'chown chroot chvt cksum clang clang++ clear cmp col column comm compgen compress '
                            'continue convert cp cpio crontab crypt csplit ctags curl cut date dc dd deallocvt '
                            'declare deluser depmod deroff df dialog diff diff3 dig dircmp dirname disown dmesg '
                            'do done dpkg dpkg-deb du echo ed egrep elif else env esac eval ex exec exit expand '
                            'export expr fakeroot false fc fdisk ffmpeg fgrep fi file find flex flock fmt fold for '
                            'fsck function functions fuser fusermount g++ gas gawk gcc gdb genisoimage getconf '
                            'getopt getopts git gpg gpgsplit gpgv grep gres groff groups gunzip gzexe hash hd head '
                            'help hexdump hg history httpd iconv id if ifconfig ifdown ifquery ifup in insmod '
                            'integer inxi ip ip6tables ip6tables-save ip6tables-restore iptables iptables-save '
                            'iptables-restore ip jobs join kill killall killall5 lc ld ldd let lex line ln local '
                            'logname look ls lsattr lsb_release lsblk lscpu lshw lslocks lsmod lsusb lzcmp lzegrep '
                            'lzfgrep lzgrep lzless lzma lzmainfo lzmore m4 mail mailx make man mkdir mkfifo mkswap '
                            'mktemp modinfo modprobe mogrify more mount msgfmt mt mv nameif nasm nc ndisasm netcat '
                            'newgrp nl nm nohup ntps objdump od openssl p7zip pacman passwd paste patch pathchk '
                            'pax pcat pcregrep pcretest perl pg ping ping6 pivot_root poweroff pr print printf ps '
                            'pwd python python2 python3 ranlib read readlink readonly reboot reset return rev rm '
                            'rmdir rmmod rpm rsync sed select service set sh sha1sum sha224sum sha256sum sha3sum '
                            'sha512sum shift shred shuf shutdown size sleep sort spell split start stop strings '
                            'strip stty su sudo sum suspend switch_root sync systemctl tac tail tar tee test then '
                            'time times touch tr trap troff true tsort tty type typeset ulimit umask umount '
                            'unalias uname uncompress unexpand uniq unlink unlzma unset until unzip unzipsfx '
                            'useradd userdel uudecode uuencode vi vim wait wc wget whence which while who wpaste '
                            'wstart xargs xdotool xxd xz xzcat xzcmp xzdiff xzfgrep xzgrep xzless xzmore yes yum '
                            'zcat zcmp zdiff zegrep zfgrep zforce zgrep zless zmore znew zsh')
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
        self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT, "fore:RED,back:MEDIUM TURQUOISE,bold")
        self.StyleSetSpec(stc.STC_STYLE_BRACEBAD, "fore:RED,back:THISTLE,bold")
        self.set_folding(False)

    def lang_json(self):
        self.StyleClearAll()
        self.SetLexer(stc.STC_LEX_JSON)
        self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT, "fore:RED,back:MEDIUM TURQUOISE,bold")
        self.StyleSetSpec(stc.STC_STYLE_BRACEBAD, "fore:RED,back:THISTLE,bold")
        self.set_folding(True)
        self.StyleSetSpec(stc.STC_JSON_BLOCKCOMMENT, "fore:#008000,back:#FFFFFF")
        self.StyleSetSpec(stc.STC_JSON_COMPACTIRI, "fore:#0000FF,back:#FFFFFF")
        self.StyleSetSpec(stc.STC_JSON_DEFAULT, "fore:#000000,back:#FFFFFF")
        self.StyleSetSpec(stc.STC_JSON_ERROR, "fore:#FFFF80,back:#FF0000")
        self.StyleSetSpec(stc.STC_JSON_ESCAPESEQUENCE, "fore:#0000FF,back:#FFFFFF")
        self.StyleSetSpec(stc.STC_JSON_KEYWORD, "fore:#18AF8A,back:#FFFFFF")
        self.StyleSetSpec(stc.STC_JSON_PROPERTYNAME, "fore:#8000FF,back:#FFFFFF,bold")
        self.StyleSetSpec(stc.STC_JSON_LDKEYWORD, "fore:#FF0000,back:#FFFFFF")
        self.StyleSetSpec(stc.STC_JSON_LINECOMMENT, "fore:#008000,back:#FFFFFF")
        self.StyleSetSpec(stc.STC_JSON_URI, "fore:#0000FF,back:#FFFFFF")
        self.StyleSetSpec(stc.STC_JSON_STRINGEOL, "fore=#808080,back:#FFFFFF")
        self.StyleSetSpec(stc.STC_JSON_NUMBER, "fore:#FF8000,back:#FFFFFF")
        self.StyleSetSpec(stc.STC_JSON_STRING, "fore:#800000,back:#FFFFFF")
        self.StyleSetSpec(stc.STC_JSON_OPERATOR, "fore:#000000,back:#FFFFFF")
        self.SetKeyWords(0, "null false true")
        self.SetKeyWords(1, "@id @context @type @value @language @container @list "
                            "@set @reverse @index @base @vocab @graph")

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
        self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT, "fore:RED,back:MEDIUM TURQUOISE,bold")
        self.StyleSetSpec(stc.STC_STYLE_BRACEBAD, "fore:RED,back:THISTLE,bold")

    def lang_xml(self):
        self.StyleClearAll()
        self.SetLexer(stc.STC_LEX_XML)
        # setting keywords 0 has an unexpected behaviour such as tags and attributes are not styled as expected
        self.SetKeyWords(1, "xml xaml xsl xslt xsd xul kml svg mxml xsml wsdl xlf xliff xbl sxbl "
                            "sitemap gml gpx plist ")
        self.StyleSetSpec(stc.STC_H_DEFAULT, 'fore:#000000,back:#FFFFFF,bold')
        self.StyleSetSpec(stc.STC_H_XMLSTART, 'fore:#FF0000,back:#FFFF00')
        self.StyleSetSpec(stc.STC_H_XMLEND, 'fore:#FF0000,back:#FFFF00')
        self.StyleSetSpec(stc.STC_H_COMMENT, 'fore:#008000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_H_NUMBER, 'fore:#FF0000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_H_DOUBLESTRING, 'fore:#8000FF,back:#FFFFFF,bold')
        self.StyleSetSpec(stc.STC_H_SINGLESTRING, 'fore:#8000FF,back:#FFFFFF,bold')
        self.StyleSetSpec(stc.STC_H_TAG, 'fore:#0000FF,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_H_TAGEND, 'fore:#0000FF,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_H_TAGUNKNOWN, 'fore:#0000FF,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_H_ATTRIBUTE, 'fore:#FF0000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_H_ATTRIBUTEUNKNOWN, 'fore:#FF0000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_H_SGML_DEFAULT, 'fore:#000000,back:#A6CAF0')
        self.StyleSetSpec(stc.STC_H_CDATA, 'fore:#FF8000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_H_ENTITY, 'fore:#000000,back:#FEFDE0,italic')
        self.StyleSetSpec(stc.STC_H_VALUE, 'fore:#000000,back:#A6CAF0')
        # self.source.SetProperty("fold.html", "1") # not sure xml version of this
        self.set_folding(True)

    def lang_html(self):
        self.StyleClearAll()
        self.SetLexer(stc.STC_LEX_HTML)
        self.SetKeyWords(1, '!doctype ^data- a abbr accept accept-charset accesskey acronym action address align '
                            'alink alt applet archive area article aside async audio autocomplete autofocus axis '
                            'b background base basefont bdi bdo bgcolor bgsound big blink blockquote body border '
                            'br button canvas caption cellpadding cellspacing center char charoff charset checkbox '
                            'checked cite class classid clear code codebase codetype col colgroup color cols colspan '
                            'command compact content contenteditable contextmenu coords data datafld dataformatas '
                            'datalist datapagesize datasrc datetime dd declare defer del details dfn dialog dir '
                            'disabled div dl draggable dropzone dt element em embed enctype event face fieldset '
                            'figcaption figure file font footer for form formaction formenctype formmethod '
                            'formnovalidate formtarget frame frameborder frameset h1 h2 h3 h4 h5 h6 head header '
                            'headers height hgroup hidden hr href hreflang hspace html http-equiv i id iframe image '
                            'img input ins isindex ismap kbd keygen label lang language leftmargin legend li link list '
                            'listing longdesc main manifest map marginheight marginwidth mark marquee max maxlength '
                            'media menu menuitem meta meter method min multicol multiple name nav nobr noembed '
                            'noframes nohref noresize noscript noshade novalidate nowrap object ol onabort '
                            'onafterprint onautocomplete onautocompleteerror onbeforeonload onbeforeprint onblur '
                            'oncancel oncanplay oncanplaythrough onchange onclick onclose oncontextmenu oncuechange '
                            'ondblclick ondrag ondragend ondragenter ondragleave ondragover ondragstart ondrop '
                            'ondurationchange onemptied onended onerror onfocus onhashchange oninput oninvalid '
                            'onkeydown onkeypress onkeyup onload onloadeddata onloadedmetadata onloadstart onmessage '
                            'onmousedown onmouseenter onmouseleave onmousemove onmouseout onmouseover onmouseup '
                            'onmousewheel onoffline ononline onpagehide onpageshow onpause onplay onplaying '
                            'onpointercancel onpointerdown onpointerenter onpointerleave onpointerlockchange '
                            'onpointerlockerror onpointermove onpointerout onpointerover onpointerup onpopstate '
                            'onprogress onratechange onreadystatechange onredo onreset onresize onscroll '
                            'onseeked onseeking onselect onshow onsort onstalled onstorage onsubmit onsuspend '
                            'ontimeupdate ontoggle onundo onunload onvolumechange onwaiting optgroup option output p '
                            'param password pattern picture placeholder plaintext pre profile progress prompt public q '
                            'radio readonly rel required reset rev reversed role rows rowspan rp rt rtc ruby rules s '
                            'samp sandbox scheme scope scoped script seamless section select selected shadow shape '
                            'size sizes small source spacer span spellcheck src srcdoc standby start step strike '
                            'strong style sub submit summary sup svg svg:svg tabindex table target tbody td template '
                            'text textarea tfoot th thead time title topmargin tr track tt type u ul usemap valign '
                            'value valuetype var version video vlink vspace wbr width xml xmlns xmp')
        self.StyleSetSpec(stc.STC_H_DEFAULT, 'fore:#000000,back:#FFFFFF,bold')
        self.StyleSetSpec(stc.STC_H_COMMENT, 'fore:#008000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_H_NUMBER, 'fore:#FF0000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_H_DOUBLESTRING, 'fore:#8000FF,back:#FFFFFF,bold')
        self.StyleSetSpec(stc.STC_H_SINGLESTRING, 'fore:#8000FF,back:#FFFFFF,bold')
        self.StyleSetSpec(stc.STC_H_TAG, 'fore:#0000FF,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_H_TAGEND, 'fore:#0000FF,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_H_TAGUNKNOWN, 'fore:#000000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_H_ATTRIBUTE, 'fore:#FF0000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_H_ATTRIBUTEUNKNOWN, 'fore:#000000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_H_SGML_DEFAULT, 'fore:#000000,back:#A6CAF0')
        self.StyleSetSpec(stc.STC_H_CDATA, 'fore:#FF8000,back:#FFFFFF')
        self.StyleSetSpec(stc.STC_H_VALUE, 'fore:#000000,back:#A6CAF0')
        self.StyleSetSpec(stc.STC_H_ENTITY, 'fore:#000000,back:#FEFDE0,italic')

    def set_styles(self):
        self.StyleSetSpec(4, 'back:TURQUOISE')  # style set 4 for compare matched line
        self.StyleSetSpec(5, 'back:WHEAT')  # style set 5 for compare unmatched line
        self.StyleSetEOLFilled(4, True)
        self.StyleSetEOLFilled(5, True)
        self.SetIndicatorCurrent(9)
        self.IndicatorSetStyle(9, stc.STC_INDIC_ROUNDBOX)  # style set 9 for matched search word indicator
        self.IndicatorSetForeground(9, 'BLUE')

    def indicate_selection(self):
        if self.GetSelectionEmpty():
            self.IndicatorClearRange(0, self.GetTextLength())
        else:
            sel_start, sel_end = self.GetSelection()  # get selection range
            self.IndicatorClearRange(0, self.GetTextLength())
            if self.IsRangeWord(sel_start, sel_end):
                vis_start = self.XYToPosition(0, self.GetFirstVisibleLine())
                vis_end = self.GetLineEndPosition(self.GetFirstVisibleLine() + self.LinesOnScreen())
                chk = True
                while chk:
                    found_start, found_end = self.FindText(vis_start, vis_end, self.GetSelectedText(),
                                                           stc.STC_FIND_WHOLEWORD)
                    if found_start == -1:
                        break
                    else:
                        self.IndicatorFillRange(found_start, found_end - found_start)
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
