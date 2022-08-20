import os
import sys  # from sys import platform can be cleaner
import wx
import wx.adv
import wx.aui as aui
import wx.stc as stc
import wx.svg
import io
import wx.lib.inspection  # for debugging
import zlib
import base64
from configs import *
import FindReplaceDlg as Frd
from TextEditor import TextEditor
from sniplets import Sniplet_Control
# region high dpi settings for windows
if sys.platform == 'win32':
    # import ctypes
    from ctypes import OleDLL
    try:
        # ctypes.windll.shcore.SetProcessDpiAwareness(True)
        # ctypes.OleDLL('shcore').SetProcessDpiAwareness(1)
        OleDLL('shcore').SetProcessDpiAwareness(1)
        pass
    except (AttributeError, OSError):
        pass
# endregion


class MainWindow(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title='ete - ete text editor')
        self.SetSize((800, 600))
        self.compare_tabs = []
        self.transparency = 255
        self.ID_SYNC_SCROLL_R = wx.ID_ANY
        self.ID_SYNC_SCROLL_L = wx.ID_ANY
        self.ID_SYNC_ZOOM_L = wx.ID_ANY
        self.ID_SYNC_ZOOM_R = wx.ID_ANY
        app_ico = wx.Icon()
        app_ico.LoadFile('ete.png', wx.BITMAP_TYPE_PNG, 32, 32)
        self.SetIcon(app_ico)

        def get_icon(name):
            with io.BytesIO(zlib.decompress(base64.b64decode(icons[name]))) as stream:
                icon = wx.Bitmap(wx.Image(stream))
            return icon

        # region menubar

        menux = {
            '&File': [
                        [EID_FILE_NEW, '&New\tCTRL+N', get_icon('new_ico'), ],
                        [EID_FILE_OPEN, '&Open\tCTRL+O', get_icon('open_ico'), ],
                        [EID_FILE_SAVE, '&Save\tCTRL+S', get_icon('save_ico'), ],
                        [EID_FILE_SAVEAS, 'Save &As\tCTRL+SHIFT+S', get_icon('save_as_ico'), ],
                        [EID_SEP, ],
                        [EID_CLOSE_TAB, 'Close', ],
                        [EID_FILE_EXIT, 'E&xit', get_icon('exit_ico'), ],
                     ],
            '&Edit': [
                        [EID_EDIT_UNDO, '&Undo\tCTRL+Z', get_icon('undo_ico'), ],
                        [EID_EDIT_REDO, '&Redo\tCTRL+Y', get_icon('redo_ico'), ],
                        [EID_SEP, ],
                        [EID_EDIT_CUT, 'Cu&t\tCTRL+X', get_icon('cut_ico'), ],
                        [EID_EDIT_COPY, '&Copy\tCTRL+C', get_icon('copy_ico'), ],
                        [EID_EDIT_PASTE, '&Paste\tCTRL+V', get_icon('paste_ico'), ],
                        [EID_SEP, ],
                        [EID_EDIT_FIND, '&Find\tCTRL+F', get_icon('find_ico'), ],
                        [EID_EDIT_REPLACE, '&Replace\tCTRL+R', get_icon('replace_ico'), ],
                        [EID_EDIT_JUMPTO, 'Jump To\tCTRL+J', get_icon('select_ico'), ],
                        [EID_SEP, ],
                        [EID_EDIT_DELETE, 'Delete', get_icon('delete_ico'), ],
                        [EID_EDIT_SELECTALL, 'Select All', get_icon('select_ico'), ],
                        [EID_SEP, ],
                        [EID_EDIT_UPPER, 'Upper Case', ],
                        [EID_EDIT_LOWER, 'Lower Case', ],
                        [EID_SEP, ],
                        [EID_EDIT_CRLF, 'Change Eol to CRLF', ],
                        [EID_EDIT_LF, 'Change Eol to LF', ],
                        [EID_EDIT_CR, 'Change Eol to CR', ],
                        [EID_SEP, ],
                        [EID_EDIT_MULTISELECT, 'Multiple Selection', ],
                      ],
            '&View':  [
                        [EID_VIEW_SPACE, 'Show White Space', ],
                        [EID_VIEW_EOL, 'Show End Of Line', ],
                        [EID_VIEW_INDENT, 'Show Indentation Guides', ],
                        [EID_SEP, ],
                        [EID_VIEW_WRAP, 'Wrap', ],
                        [EID_VIEW_TRANSPARENT, 'Transparent', ],

                      ],
            '&Lang':  [
                        [EID_LANG_TXT, 'Text', ],
                        [EID_LANG_PYTHON, 'Python', ],
                        [EID_LANG_MSSQL, 'MSSQL', ],
                        [EID_LANG_BASH, 'Bash', ],
                        [EID_LANG_POWERSHELL, 'PowerShell', ],
                        [EID_LANG_XML, 'XML', ],
                        [EID_LANG_HTML, 'HTML', ],
                      ],
            'E&ncoding': [
                            [EID_ENCODE_UTF8, 'UTF-8', ],
                            [EID_ENCODE_WIN1252, 'Windows-1252', ],
                            [EID_ENCODE_WIN1254, 'Windows-1254', ],
                         ],
            '&Tools': [
                         [EID_TOOLS_COMPARE, '&Compare', get_icon('compare_ico'), ],
                         [EID_TOOLS_CLEARCOMP, 'Clea&r Compare', get_icon('clear_compare_ico'), ],
                      ],
            '&About': [
                         [EID_ABOUT_INFO, 'About', get_icon('about_ico'), ],
                      ],
            }

        self.menu_bar = wx.MenuBar()

        for item in menux:
            m = wx.Menu()
            for i in menux[item]:
                if i[0] == EID_SEP:
                    m.AppendSeparator()
                else:
                    try:
                        mi = wx.MenuItem(parentMenu=m, id=i[0], text=i[1], kind=wx.ITEM_NORMAL)
                        if len(i) > 2:
                            bmp = i[2]
                            img = bmp.ConvertToImage()
                            mi.SetBitmap(wx.Bitmap(img.Scale(24, 24, wx.IMAGE_QUALITY_HIGH)))
                            # TODO: this call is only for mac os - windows handles this fine
                            # mac os scaled same bitmap differently for toolbar and menu
                            # entire if block should be only mi.SetBitmap(i[2]) for windows
                        m.Append(mi)
                    finally:
                        pass
            self.menu_bar.Append(m, item)

        self.SetMenuBar(self.menu_bar)
        # endregion

        # region toolbar definition
        # cascaded toolbar on macos does not show icons so text added
        # on windows adding text makes icons too big
        self.tool_bar = wx.ToolBar(self)
        if sys.platform == 'win32':
            self.tool_bar.SetWindowStyle(wx.TB_HORIZONTAL | wx.TB_FLAT | wx.NO_BORDER)
        elif sys.platform == 'darwin':
            self.tool_bar.SetWindowStyle(wx.TB_HORIZONTAL | wx.TB_FLAT | wx.TB_TEXT | wx.NO_BORDER)

        self.tool_bar.AddTool(toolId=EID_FILE_NEW, label='New', bitmap=get_icon('new_ico'),
                              bmpDisabled=get_icon('new_ico'), kind=wx.ITEM_NORMAL, shortHelp='New File',
                              longHelp='', clientData=None)
        self.tool_bar.AddTool(toolId=EID_FILE_OPEN, label='Open', bitmap=get_icon('open_ico'),
                              bmpDisabled=get_icon('open_ico'), kind=wx.ITEM_NORMAL, shortHelp='Open File',
                              longHelp='', clientData=None)
        self.tool_bar.AddTool(toolId=EID_FILE_SAVE, label='Save', bitmap=get_icon('save_ico'),
                              bmpDisabled=get_icon('save_ico'), kind=wx.ITEM_NORMAL, shortHelp='Save File',
                              longHelp='', clientData=None)
        self.tool_bar.AddTool(toolId=EID_FILE_SAVEAS, label='Save As', bitmap=get_icon('save_as_ico'),
                              bmpDisabled=get_icon('save_as_ico'), kind=wx.ITEM_NORMAL, shortHelp='Save File As',
                              longHelp='', clientData=None)
        self.tool_bar.AddSeparator()
        self.tool_bar.AddTool(toolId=EID_EDIT_CUT, label='Cut', bitmap=get_icon('cut_ico'),
                              bmpDisabled=get_icon('cut_ico'), kind=wx.ITEM_NORMAL, shortHelp='Cut',
                              longHelp='Cut Text', clientData=None)
        self.tool_bar.AddTool(toolId=EID_EDIT_COPY, label='Copy', bitmap=get_icon('copy_ico'),
                              bmpDisabled=get_icon('copy_ico'), kind=wx.ITEM_NORMAL, shortHelp='Copy',
                              longHelp='Copy Text', clientData=None)
        self.tool_bar.AddTool(toolId=EID_EDIT_PASTE, label='Paste', bitmap=get_icon('paste_ico'),
                              bmpDisabled=get_icon('paste_ico'), kind=wx.ITEM_NORMAL, shortHelp='Paste',
                              longHelp='Paste Text', clientData=None)
        self.tool_bar.AddSeparator()
        self.tool_bar.AddTool(toolId=EID_EDIT_FIND, label='Find', bitmap=get_icon('find_ico'),
                              bmpDisabled=get_icon('find_ico'), kind=wx.ITEM_NORMAL, shortHelp='Find',
                              longHelp='Find Text', clientData=None)
        self.tool_bar.AddTool(toolId=EID_EDIT_REPLACE, label='Replace Text', bitmap=get_icon('replace_ico'),
                              bmpDisabled=get_icon('replace_ico'), kind=wx.ITEM_NORMAL, shortHelp='Replace',
                              longHelp='Replace Text', clientData=None)
        self.tool_bar.AddSeparator()
        self.tool_bar.AddTool(toolId=EID_ABOUT_INFO, label='Info', bitmap=get_icon('info_ico'),
                              bmpDisabled=get_icon('info_ico'), kind=wx.ITEM_NORMAL, shortHelp='Information',
                              longHelp='', clientData=None)
        self.tool_bar.AddTool(toolId=EID_FILE_EXIT, label='Exit', bitmap=get_icon('exit_ico'),
                              bmpDisabled=get_icon('exit_ico'), kind=wx.ITEM_NORMAL, shortHelp='Exit Application',
                              longHelp='', clientData=None)
        self.tool_bar.AddSeparator()
        self.tool_bar.AddTool(toolId=EID_TOOLS_COMPARE, label='Compare', bitmap=get_icon('compare_ico'),
                              bmpDisabled=get_icon('compare_ico'), kind=wx.ITEM_NORMAL, shortHelp='Compare',
                              longHelp='', clientData=None)
        self.tool_bar.AddTool(toolId=EID_TOOLS_CLEARCOMP, label='Clear Compare', bitmap=get_icon('clear_compare_ico'),
                              bmpDisabled=get_icon('clear_compare_ico'), kind=wx.ITEM_NORMAL, shortHelp='Clear Compare',
                              longHelp='', clientData=None)

        self.SetToolBar(self.tool_bar)
        self.tool_bar.Realize()
        # endregion

        # region main panel 
        # self.main_panel = wx.Panel(parent=self)
        self.main_panel_window = wx.SplitterWindow(self, id=wx.ID_ANY, style=wx.SP_3D | wx.SP_LIVE_UPDATE)
        # self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # self.main_panel.SetSizer(self.main_sizer)
        
        self.editor_panel = wx.Panel(parent=self.main_panel_window)
        self.editor_sizer = wx.BoxSizer(wx.VERTICAL)
        self.editor_panel.SetSizer(self.editor_sizer)
        self.editor_panel.DragAcceptFiles(True)
        self.editor_panel.Bind(wx.EVT_DROP_FILES, self.open_page)

        self.sniplets_panel = Sniplet_Control(parent=self.main_panel_window)
        
        # self.main_sizer.Add(self.editor_panel, 3, wx.EXPAND)
        # self.main_sizer.Add(self.sniplets_panel,1,wx.EXPAND)
        self.main_panel_window.SplitVertically(self.editor_panel, self.sniplets_panel, -250)
        self.main_panel_window.SetSashGravity(1)  
        # sash gravity
        # 1.0: only left/top window grows on resize
        # 0.0: only the bottom/right window is automatically resized
        # 0.5: both windows grow by equal size

        # endregion

        # region tabbed notebook definition

        self.notebook = aui.AuiNotebook(parent=self.editor_panel,
                                        style=aui.AUI_NB_CLOSE_ON_ALL_TABS |
                                        aui.AUI_NB_DEFAULT_STYLE |
                                        aui.AUI_NB_WINDOWLIST_BUTTON)
        # TODO: later to play with colours in tabs a little
        # asta = self.notebook.GetArtProvider()
        # asta.SetActiveColour(wx.Colour(77, 184, 255))
        # asta.SetColour(wx.Colour(153, 214, 255))
        self.editor_sizer.Add(self.notebook, 1, wx.EXPAND)
        # endregion

        # region status bar
        self.status_bar = wx.StatusBar(self)
        self.status_bar.SetFieldsCount(4, [-2, -1, -1, -1])
        self.SetStatusBar(self.status_bar)
        # endregion

        # region tab_popup
        self.tab_popup = wx.Menu()
        self.tab_popup_close = wx.MenuItem(self.tab_popup, wx.ID_ANY, "Close")
        self.tab_popup.Append(self.tab_popup_close)
        self.Bind(wx.EVT_MENU, self.on_tab_popup_action, self.tab_popup_close)
        self.tab_popup_close_all_others = wx.MenuItem(self.tab_popup, wx.ID_ANY, "Close All others")
        self.tab_popup.Append(self.tab_popup_close_all_others)
        self.Bind(wx.EVT_MENU, self.on_tab_popup_action, self.tab_popup_close_all_others)
        # endregion

        # region event bindings

        self.Bind(wx.EVT_MENU, self.new_page, id=EID_FILE_NEW)
        self.Bind(wx.EVT_MENU, self.open_page, id=EID_FILE_OPEN)
        self.Bind(wx.EVT_MENU, self.save_page, id=EID_FILE_SAVE)
        self.Bind(wx.EVT_MENU, self.save_as_page, id=EID_FILE_SAVEAS)
        self.Bind(wx.EVT_MENU, self.close_page, id=EID_CLOSE_TAB)
        self.Bind(wx.EVT_MENU, self.on_info, id=EID_ABOUT_INFO)
        self.Bind(wx.EVT_MENU, self.onexit, id=EID_FILE_EXIT)

        self.Bind(wx.EVT_MENU, self.on_menu_edit_event, id=EID_EDIT_UNDO)
        self.Bind(wx.EVT_MENU, self.on_menu_edit_event, id=EID_EDIT_REDO)
        self.Bind(wx.EVT_MENU, self.on_menu_edit_event, id=EID_EDIT_CUT)
        self.Bind(wx.EVT_MENU, self.on_menu_edit_event, id=EID_EDIT_COPY)
        self.Bind(wx.EVT_MENU, self.on_menu_edit_event, id=EID_EDIT_PASTE)
        self.Bind(wx.EVT_MENU, self.on_menu_edit_event, id=EID_EDIT_DELETE)
        self.Bind(wx.EVT_MENU, self.on_menu_edit_event, id=EID_EDIT_SELECTALL)
        self.Bind(wx.EVT_MENU, self.on_find, id=EID_EDIT_FIND)
        self.Bind(wx.EVT_MENU, self.on_find, id=EID_EDIT_REPLACE)  # using the same dialog as find for now.
        self.Bind(wx.EVT_MENU, self.on_jump_to, id=EID_EDIT_JUMPTO)
        self.Bind(wx.EVT_MENU, self.on_about, id=EID_ABOUT_INFO)
        self.Bind(wx.EVT_MENU, self.on_language, id=EID_LANG_TXT)
        self.Bind(wx.EVT_MENU, self.on_language, id=EID_LANG_PYTHON)
        self.Bind(wx.EVT_MENU, self.on_language, id=EID_LANG_MSSQL)
        self.Bind(wx.EVT_MENU, self.on_language, id=EID_LANG_BASH)
        self.Bind(wx.EVT_MENU, self.on_language, id=EID_LANG_POWERSHELL)
        self.Bind(wx.EVT_MENU, self.on_language, id=EID_LANG_XML)
        self.Bind(wx.EVT_MENU, self.on_language, id=EID_LANG_HTML)

        self.Bind(wx.EVT_MENU, self.on_view_whitespace, id=EID_VIEW_SPACE)
        self.Bind(wx.EVT_MENU, self.on_view_eol, id=EID_VIEW_EOL)
        self.Bind(wx.EVT_MENU, self.on_view_indent_guide, id=EID_VIEW_INDENT)
        self.Bind(wx.EVT_MENU, self.on_view_wrap, id=EID_VIEW_WRAP)
        self.Bind(wx.EVT_MENU, self.on_view_transparent, id=EID_VIEW_TRANSPARENT)

        self.Bind(wx.EVT_MENU, self.on_menu_tools_compare, id=EID_TOOLS_COMPARE)
        self.Bind(wx.EVT_MENU, self.on_menu_tools_clear_compare, id=EID_TOOLS_CLEARCOMP)
        self.Bind(wx.EVT_MENU, self.on_menu_edit_case, id=EID_EDIT_UPPER)
        self.Bind(wx.EVT_MENU, self.on_menu_edit_case, id=EID_EDIT_LOWER)

        self.Bind(wx.EVT_MENU, self.on_menu_edit_eol, id=EID_EDIT_CRLF)
        self.Bind(wx.EVT_MENU, self.on_menu_edit_eol, id=EID_EDIT_LF)
        self.Bind(wx.EVT_MENU, self.on_menu_edit_eol, id=EID_EDIT_CR)

        self.Bind(wx.EVT_MENU, self.on_select_mode, id=EID_EDIT_MULTISELECT)

        self.Bind(wx.EVT_MENU, self.on_menu_encode, id=EID_ENCODE_UTF8)
        self.Bind(wx.EVT_MENU, self.on_menu_encode, id=EID_ENCODE_WIN1252)
        self.Bind(wx.EVT_MENU, self.on_menu_encode, id=EID_ENCODE_WIN1254)

        # detect double click on tab bar empty space
        self.Bind(aui.EVT_AUINOTEBOOK_BG_DCLICK, self.new_page, id=wx.ID_ANY)
        self.Bind(aui.EVT_AUINOTEBOOK_TAB_RIGHT_UP, self.on_tab_popup, id=wx.ID_ANY)

        self.notebook.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.on_tab_close, id=wx.ID_ANY)
        self.notebook.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.on_page_select, id=wx.ID_ANY)

        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_event)

        # endregion

        self.search_dlg = Frd.FindReplaceDlg(parent=self, notebook=self.notebook)
        self.info = wx.adv.AboutDialogInfo()
        self.Show()

    def get_current_text_editor(self):
        cp = self.notebook.GetCurrentPage()  # if tab is switched when dlg is open pick new tab
        te = self.get_text_editor_from_page(self.notebook.GetPageIndex(cp))
        return te

    def on_key_event(self, event):
        if event.AltDown() and event.ShiftDown() and event.GetKeyCode() == wx.WXK_DOWN:
            print('key comb pressed')
            cp = self.notebook.GetCurrentPage()  # if tab is switched when dlg is open pick new tab
            te = self.get_text_editor_from_page(self.notebook.GetPageIndex(cp))
            te.SetAdditionalSelectionTyping(True)
            te.LineDownRectExtend()
        else:
            event.Skip()

    def get_text_editor_from_page(self, page_idx):
        page = self.notebook.GetPage(page_idx)
        if page:
            for widget in page.GetChildren():
                if isinstance(widget, TextEditor):
                    return widget
                else:
                    return None

    def on_about(self, _):
        displays = ((i, wx.Display(i)) for i in range(wx.Display.GetCount()))
        desc = [str(i) + ':' + str(display.GetGeometry().GetSize()) for i, display in displays]
        desc.append('Content Scale factor:' + str(self.GetContentScaleFactor()))
        desc.append('DPI scale factor:' + str(self.GetDPIScaleFactor()))
        self.info.SetName("ete text editor")
        self.info.SetVersion('0.3.a')
        self.info.SetDescription('Text editor using wxpython')
        self.info.SetDevelopers(['Emre Yukselen'])
        self.info.SetWebSite('https://github.com/eyukselen/ete')
        self.info.SetDescription('\n'.join(desc))
        wx.adv.AboutBox(self.info)

    def new_page(self, _):
        page = wx.Panel(parent=self.notebook)
        page_sizer = wx.BoxSizer(wx.VERTICAL)
        page.SetSizer(page_sizer)
        te = TextEditor(parent=page, filename='')
        te.code_page = 'utf-8'
        self.status_bar.SetStatusText('utf-8', 3)
        if sys.platform == 'win32':
            te.DragAcceptFiles(True)
            te.Bind(wx.EVT_DROP_FILES, self.open_page)
        page_sizer.Add(te, 1, wx.EXPAND)
        self.notebook.AddPage(page, 'New *', select=True)
        te.SetFocus()

    def open_page(self, event):
        if hasattr(event, 'Files'):
            files = event.GetFiles()
        elif event.GetId() == EID_FILE_OPEN:
            with wx.FileDialog(self, "Open file", wildcard="text files (*.txt)|*.txt|All files (*.*)|*.*",
                               style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE) as fileDialog:
                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return
                files = fileDialog.GetPaths()
        open_files = []
        for idx in range(self.notebook.GetPageCount()):
            te = self.get_text_editor_from_page(idx)
            open_files.append(te.file_name)
        for file in files:
            if file not in open_files:
                _, file_name = os.path.split(file)
                page = wx.Panel(parent=self.notebook)
                page_sizer = wx.BoxSizer(wx.VERTICAL)
                page.SetSizer(page_sizer)
                te = TextEditor(parent=page, filename=file)
                if sys.platform == 'win32':
                    te.DragAcceptFiles(True)
                    te.Bind(wx.EVT_DROP_FILES, self.open_page)
                page_sizer.Add(te, 1, wx.EXPAND)
                self.notebook.AddPage(page, select=True, caption=file_name)
                # te.LoadFile(file) # adding my method to replace builtin
                te.load_file(file)
                
                self.notebook.SetPageToolTip(self.notebook.GetPageIndex(self.notebook.GetCurrentPage()), file)
                _, f = os.path.split(file)
                self.notebook.SetPageText(self.notebook.GetPageIndex(self.notebook.GetCurrentPage()), f)
                te.Refresh()

        self.Raise()  # get the focus to main frame from outside world after files are being dragged in

    def save_page(self, _):
        if self.notebook.GetPageCount() > 0:
            te = self.get_text_editor_from_page(self.notebook.GetPageIndex(self.notebook.GetCurrentPage()))
            filename = te.file_name
            if filename:
                # te.SaveFile(filename) # adding my method to replace builtin 
                te.save_file(filename)
            else:
                self.save_as_page(None)
        else:
            return  # there is nothing open to save

    def save_as_page(self, _):
        if self.notebook.GetPageCount() > 0:
            te = self.get_text_editor_from_page(self.notebook.GetPageIndex(self.notebook.GetCurrentPage()))
            filename = te.file_name
        else:
            return  # there is nothing open to save

        with wx.FileDialog(self, "Save As", wildcard="text files (*.txt)|*.txt", defaultFile=filename,
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            filename = fileDialog.GetPath()
            # te.SaveFile(filename) # adding my method to replace builtin
            te.save_file(filename)
            te.file_name = filename
            self.notebook.SetPageToolTip(self.notebook.GetPageIndex(self.notebook.GetCurrentPage()), filename)
            _, file = os.path.split(filename)
            self.notebook.SetPageText(self.notebook.GetPageIndex(self.notebook.GetCurrentPage()), file)

    def on_page_select(self, event):
        """set focus on text editor when a page selected"""
        te = self.get_text_editor_from_page(event.Selection)
        te.SetFocus()
        event.Skip()

    def on_tab_popup(self, event):
        tab_id = event.GetSelection()
        self.notebook.SetSelection(tab_id)
        mouse_position = wx.GetMousePosition() - self.notebook.GetScreenPosition()
        self.PopupMenu(self.tab_popup, pos=mouse_position)

    def on_tab_popup_action(self, event):
        if event.GetId() == self.tab_popup_close.GetId():
            evt = aui.AuiNotebookEvent(aui.EVT_AUINOTEBOOK_PAGE_CLOSE.typeId, wx.aui.wxEVT_AUINOTEBOOK_PAGE_CLOSE)
            evt.SetEventObject(self.notebook)
            evt.SetSelection(self.notebook.GetPageIndex(self.notebook.GetCurrentPage()))
            wx.PostEvent(self.notebook, evt)
        if event.GetId() == self.tab_popup_close_all_others.GetId():
            active_tab = self.notebook.GetPageIndex(self.notebook.GetCurrentPage())
            for x in range(self.notebook.GetPageCount()-1, -1, -1):
                if x != active_tab:
                    self.close_tab(x)

    def close_page(self, _):
        if self.notebook.GetPageCount() > 0:
            page_idx = self.notebook.GetPageIndex(self.notebook.GetCurrentPage())
            self.close_tab(page_idx)

    def close_tab(self, page):
        self.notebook.SetSelection(page)
        te = self.get_text_editor_from_page(page)
        if te.IsModified():
            filename = self.notebook.GetPageToolTip(page)
            if filename:
                msg = 'Save ' + filename + ' ?'
            else:
                msg = 'Save changes to file?'
            dlg = wx.MessageBox(msg, 'Save ?', wx.YES_NO | wx.CANCEL)
            if dlg == wx.YES:
                self.save_page(None)
                self.notebook.DeletePage(page)
            elif dlg == wx.NO:
                te.SetText('')
                self.notebook.DeletePage(page)
            else:
                pass
        else:
            self.notebook.DeletePage(page)

    def on_tab_close(self, event):
        event.Veto()
        if len(self.compare_tabs) == 2:  # if its in compare mode first clear compare then close tab
            self.on_menu_tools_clear_compare(None)
            # for some reason with new IDs this is not picked correctly
            # e = wx.MenuEvent(wx.EVT_MENU.typeId, EID_TOOLS_CLEARCOMP)
            # wx.PostEvent(self, e)
        page_to_close = event.GetSelection()
        self.close_tab(page_to_close)

    def onexit(self, _):
        self.Close()

    def onclose(self, event):
        if event.CanVeto():
            event.Veto()
        for x in range(self.notebook.GetPageCount(), 0, -1):
            cp = self.notebook.GetPage(x-1)
            for widget in cp.GetChildren():
                filename = self.notebook.GetPageToolTip(self.notebook.GetPageIndex(cp))
                if filename:
                    msg = 'Save ' + filename + ' ?'
                else:
                    msg = 'Save changes to file?'
                if isinstance(widget, wx.stc.StyledTextCtrl):
                    if widget.IsModified():
                        dlg = wx.MessageBox(msg, 'Save ?', wx.YES_NO | wx.CANCEL)
                        if dlg == wx.YES:
                            self.save_page(event)
                            self.notebook.DeletePage(self.notebook.GetPageIndex(cp))
                        elif dlg == wx.NO:
                            widget.SetText('')
                            self.notebook.DeletePage(self.notebook.GetPageIndex(cp))
                        elif dlg == wx.CANCEL:
                            return
                        else:
                            pass
                    else:
                        self.notebook.DeletePage(self.notebook.GetPageIndex(cp))
        self.Destroy()

    def on_menu_edit_event(self, event):
        if self.notebook.GetPageCount() > 0:
            cp = self.notebook.GetCurrentPage()
            for widget in cp.GetChildren():
                if isinstance(widget, TextEditor):
                    widget.on_receive_event(event)
        else:
            return

    def on_info(self, event):
        _ = event
        self.on_about(None)

    def on_menu_tools_compare(self, _):
        if len(self.compare_tabs) == 2:  # already in compare so do nothing
            return

        # region splitting window for compare
        rpi = self.notebook.GetPageIndex(self.notebook.GetCurrentPage())
        if rpi < 1:  # there should be at least 1 tab left to active tab
            return
        lpi = rpi - 1

        lstc = self.get_text_editor_from_page(lpi)
        rstc = self.get_text_editor_from_page(rpi)

        lstc.set_lang('text')
        rstc.set_lang('text')

        self.compare_tabs = [lstc, rstc]
        self.notebook.Split(rpi, wx.RIGHT)
        # endregion

        l_list = []
        for i in range(lstc.GetLineCount()):
            l_list.append(lstc.GetLineText(i))

        r_list = []
        for i in range(rstc.GetLineCount()):
            r_list.append(rstc.GetLineText(i))

        res = self.diff(l_list, r_list)

        c = 0
        rstc.set_styles()
        lstc.set_styles()
        print(res)

        eol_left = lstc.get_eol_len()
        eol_right = rstc.get_eol_len()

        curline = 0
        for x in res:
            for _ in x[1]:
                if x[0] == '-':
                    rstc.InsertText(rstc.XYToPosition(0, curline), '\n')  # add empty line to left
                    lstc.MarkerAdd(curline, lstc.MARKER_MINUS)  # this line is added
                    rstc.SetLineState(curline, 1)
                    lstc.StartStyling(lstc.XYToPosition(0, curline))
                    lstc.SetStyling(lstc.GetLineLength(curline) + eol_right, 5)
                if x[0] == '+':
                    lstc.InsertText(lstc.XYToPosition(0, curline), '\n')  # add empty line to left
                    rstc.MarkerAdd(curline, rstc.MARKER_PLUS)  # this line is added
                    lstc.SetLineState(curline, 1)
                    rstc.StartStyling(rstc.XYToPosition(0, curline))
                    rstc.SetStyling(rstc.GetLineLength(curline) + eol_right, 5)
                if x[0] == '=':
                    lstc.StartStyling(lstc.XYToPosition(0, curline))
                    lstc.SetStyling(lstc.GetLineLength(curline) + eol_left, 4)
                    rstc.StartStyling(rstc.XYToPosition(0, curline))
                    rstc.SetStyling(rstc.GetLineLength(curline) + eol_right, 4)
                curline += 1
        self.set_tabs_in_sync(lstc, rstc, True)
        self.notebook.SetSelection(lpi)
        self.notebook.SetSelection(rpi)

    def on_menu_tools_clear_compare(self, _):
        if not len(self.compare_tabs) == 2:  # I will loose tab id when they are switched or new tabs added
            return
        lstc, rstc = self.compare_tabs

        # need to clean up end to start otherwise in top-down line numbers would change on every delete
        for i in range(lstc.GetMaxLineState(), -1, -1):
            if lstc.GetLineState(i) == 1 and lstc.GetLineText(i) == '':
                lstc.GotoLine(i)
                rstc.MarkerDelete(i, rstc.MARKER_PLUS)
                lstc.LineDelete()

        for i in range(rstc.GetMaxLineState(), -1, -1):
            if rstc.GetLineState(i) == 1 and rstc.GetLineText(i) == '':
                rstc.GotoLine(i)
                lstc.MarkerDelete(i, lstc.MARKER_MINUS)
                rstc.LineDelete()

        lstc.StyleClearAll()
        rstc.StyleClearAll()

        if lstc.lang:
            lstc.set_lang(lstc.lang)

        if rstc.lang:
            rstc.set_lang(lstc.lang)

        self.set_tabs_in_sync(lstc, rstc, False)
        self.compare_tabs = []
        # self.notebook.UnSplit()

        self.Freeze()

        # remember the tab now selected
        now_selected = self.notebook.GetSelection()
        # select first tab as destination
        self.notebook.SetSelection(0)
        # iterate all other tabs
        for idx in range(1, self.notebook.GetPageCount()):
            # get win reference
            win = self.notebook.GetPage(idx)
            # get tab title
            title = self.notebook.GetPageText(idx)
            # get page bitmap
            bmp = self.notebook.GetPageBitmap(idx)
            # remove from notebook
            self.notebook.RemovePage(idx)
            # re-add in the same position so it will tab
            self.notebook.InsertPage(idx, win, title, False, bmp)
        # restore original selected tab
        self.notebook.SetSelection(now_selected)

        self.Thaw()

    def set_tabs_in_sync(self, lstc, rstc, activate):
        def set_zoom_r(event):
            rstc.SetZoom(lstc.GetZoom())
            event.Skip()

        def set_zoom_l(event):
            lstc.SetZoom(rstc.GetZoom())
            event.Skip()

        def set_scroll_r(event):
            if lstc.GetFirstVisibleLine() == rstc.GetFirstVisibleLine() and lstc.GetXOffset() == rstc.GetXOffset():
                event.Skip()
                return
            else:
                rstc.SetFirstVisibleLine(lstc.GetFirstVisibleLine())
                rstc.SetXOffset(lstc.GetXOffset())
                event.Skip()

        def set_scroll_l(event):
            if lstc.GetFirstVisibleLine() == rstc.GetFirstVisibleLine() and lstc.GetXOffset() == rstc.GetXOffset():
                event.Skip()
                return
            else:
                lstc.SetXOffset(rstc.GetXOffset())
                lstc.SetFirstVisibleLine(rstc.GetFirstVisibleLine())
                event.Skip()

        if activate:
            rstc.SetZoom(lstc.GetZoom())
            lstc.GotoLine(0)
            rstc.GotoLine(0)
            lstc.Bind(stc.EVT_STC_ZOOM, set_zoom_r, id=self.ID_SYNC_ZOOM_L)
            rstc.Bind(stc.EVT_STC_ZOOM, set_zoom_l, id=self.ID_SYNC_ZOOM_R)
            lstc.Bind(stc.EVT_STC_UPDATEUI, set_scroll_r, id=self.ID_SYNC_SCROLL_L)
            rstc.Bind(stc.EVT_STC_UPDATEUI, set_scroll_l, id=self.ID_SYNC_SCROLL_R)
        else:
            lstc.Unbind(stc.EVT_STC_ZOOM, id=self.ID_SYNC_ZOOM_L)
            rstc.Unbind(stc.EVT_STC_ZOOM, id=self.ID_SYNC_ZOOM_R)
            lstc.Unbind(stc.EVT_STC_UPDATEUI, id=self.ID_SYNC_SCROLL_L)
            rstc.Unbind(stc.EVT_STC_UPDATEUI, id=self.ID_SYNC_SCROLL_R)

    def diff(self, old, new):
        old_index_map = dict()
        for i, val in enumerate(old):
            old_index_map.setdefault(val, list()).append(i)

        overlap = dict()

        sub_start_old = 0
        sub_start_new = 0
        sub_length = 0

        for inew, val in enumerate(new):
            _overlap = dict()
            for iold in old_index_map.get(val, list()):
                _overlap[iold] = (iold and overlap.get(iold - 1, 0)) + 1
                if _overlap[iold] > sub_length:
                    sub_length = _overlap[iold]
                    sub_start_old = iold - sub_length + 1
                    sub_start_new = inew - sub_length + 1
            overlap = _overlap

        if sub_length == 0:
            return (old and [('-', old)] or []) + (new and [('+', new)] or [])
        else:
            return self.diff(old[: sub_start_old], new[: sub_start_new]) + \
                   [('=', new[sub_start_new: sub_start_new + sub_length])] + \
                   self.diff(old[sub_start_old + sub_length:], new[sub_start_new + sub_length:])

    def on_find(self, _):
        if self.notebook.GetPageCount() == 0 or self.search_dlg.IsShown():
            return
        cp = self.notebook.GetCurrentPage()  # if tab is switched when dlg is open pick new tab
        te = self.get_text_editor_from_page(self.notebook.GetPageIndex(cp))
        self.search_dlg.text_find_str.SetValue(te.GetSelectedText())
        self.search_dlg.Show()

    def on_jump_to(self, _):
        if self.notebook.GetPageCount() == 0:
            return
        cp = self.notebook.GetCurrentPage()
        jump_to_dlg = wx.TextEntryDialog(parent=self, message='Enter line number to jump to:', caption='Jump To')
        if jump_to_dlg.ShowModal() == wx.ID_OK:
            line_to_jump = jump_to_dlg.GetValue()
            if line_to_jump.isdigit():
                te = self.get_text_editor_from_page(self.notebook.GetPageIndex(cp))
                if 1 <= int(line_to_jump) <= te.GetLineCount():
                    te.GotoLine(int(line_to_jump) - 1)
                    # if max lines < line_to_jump < 0 does not give error goes to first or last line
                else:
                    wx.MessageBox('Could not locate line number:' + line_to_jump, 'Warning', wx.OK | wx.ICON_WARNING)
            else:
                wx.MessageBox('Could not locate line number:' + line_to_jump, 'Warning', wx.OK | wx.ICON_WARNING)

    def on_view_whitespace(self, _):
        if self.notebook.GetPageCount() == 0:
            return
        cp = self.notebook.GetCurrentPage()  # returns none if there is no page open
        te = self.get_text_editor_from_page(self.notebook.GetPageIndex(cp))
        if te.ViewWhiteSpace:
            te.SetViewWhiteSpace(False)
        else:
            te.SetViewWhiteSpace(True)

    def on_view_eol(self, _):
        if self.notebook.GetPageCount() == 0:
            return
        cp = self.notebook.GetCurrentPage()
        te = self.get_text_editor_from_page(self.notebook.GetPageIndex(cp))
        if te.ViewEOL:
            te.SetViewEOL(False)
        else:
            te.SetViewEOL(True)

    def on_view_indent_guide(self, _):
        if self.notebook.GetPageCount() == 0:
            return
        cp = self.notebook.GetCurrentPage()
        te = self.get_text_editor_from_page(self.notebook.GetPageIndex(cp))
        if te.IndentationGuides:
            te.SetIndentationGuides(False)
        else:
            te.SetIndentationGuides(True)

    def on_view_wrap(self, _):
        if self.notebook.GetPageCount() == 0:
            return
        cp = self.notebook.GetCurrentPage()
        te = self.get_text_editor_from_page(self.notebook.GetPageIndex(cp))
        if te.WrapMode:
            te.SetWrapMode(False)
        else:
            te.SetWrapMode(True)

    def on_view_transparent(self, _):
        tp = TransparencyDlg(self)
        tp.Show()

    def on_language(self, event):
        if self.notebook.GetPageCount() == 0:
            return
        if event.GetId() == EID_LANG_PYTHON:
            lang = 'python'
        elif event.GetId() == EID_LANG_MSSQL:
            lang = 'mssql'
        elif event.GetId() == EID_LANG_TXT:
            lang = 'txt'
        elif event.GetId() == EID_LANG_BASH:
            lang = 'bash'
        elif event.GetId() == EID_LANG_POWERSHELL:
            lang = 'ps'
        elif event.GetId() == EID_LANG_XML:
            lang = 'xml'
        elif event.GetId() == EID_LANG_HTML:
            lang = 'html'
        else:
            lang = 'txt'
        cp = self.notebook.GetCurrentPage()
        te = self.get_text_editor_from_page(self.notebook.GetPageIndex(cp))
        te.set_lang(lang)

    def on_select_mode(self, _):
        if self.notebook.GetPageCount() == 0:
            return
        cp = self.notebook.GetCurrentPage()
        te = self.get_text_editor_from_page(self.notebook.GetPageIndex(cp))
        if te.GetMultipleSelection():
            te.SetMultipleSelection(False)
        else:
            te.SetMultipleSelection(True)

    def on_menu_edit_case(self, event):
        if self.notebook.GetPageCount() == 0:
            return
        cs = None
        if event.GetId() == 2011:
            cs = 'upper'
        elif event.GetId() == 2012:
            cs = 'lower'
        cp = self.notebook.GetCurrentPage()
        te = self.get_text_editor_from_page(self.notebook.GetPageIndex(cp))
        te.set_case(cs)

    def on_menu_edit_eol(self, event):
        if self.notebook.GetPageCount() == 0:
            return
        eol_mode = 0
        if event.GetId() == EID_EDIT_CRLF:
            eol_mode = wx.stc.STC_EOL_CRLF
        elif event.GetId() == EID_EDIT_LF:
            eol_mode = wx.stc.STC_EOL_LF
        elif event.GetId() == EID_EDIT_CR:
            eol_mode = wx.stc.STC_EOL_CR
        cp = self.notebook.GetCurrentPage()
        te = self.get_text_editor_from_page(self.notebook.GetPageIndex(cp))
        te.set_eol(eol_mode)
        te.update_toolbar_eol_mode()

    def on_menu_encode(self, event):
        if event.GetId() == EID_ENCODE_UTF8:
            self.set_encoding('utf-8')
        elif event.GetId() == EID_ENCODE_WIN1252:
            self.set_encoding('windows-1252')
        elif event.GetId() == EID_ENCODE_WIN1254:
            self.set_encoding('windows-1254')
        else:
            return
    
    def set_encoding(self, enc):
        if self.notebook.GetPageCount() == 0:
            return
        cp = self.notebook.GetCurrentPage()
        te = self.get_text_editor_from_page(self.notebook.GetPageIndex(cp))
        if te.code_page == enc:
            return
        xx = te.GetText()

        if enc == 'utf-8':
            str_tr = bytes(xx, encoding=te.code_page).decode(te.code_page)  # pseudo conversion
            te.SetText(str_tr)
            te.code_page = enc
            self.status_bar.SetStatusText(enc, 3)
        elif enc == 'windows-1254':
            if te.code_page != 'utf-8':
                str_tr = xx.encode('windows-1252').decode('windows-1254')  # works for ansi2ansi not uni2ansi
            else:
                str_tr = bytes(xx, encoding='windows-1254').decode('windows-1254')
            te.SetText(str_tr)
            te.code_page = enc
            self.status_bar.SetStatusText(enc, 3)
        elif enc == 'windows-1252':
            if te.code_page != 'utf-8':
                str_tr = xx.encode(te.code_page).decode('windows-1252')  # works for ansi2 ansi not uni2ansi
            else:
                str_tr = bytes(xx, encoding='windows-1252').decode('windows-1252')
            te.SetText(str_tr)
            te.code_page = enc
            self.status_bar.SetStatusText(enc, 3)


class TransparencyDlg(wx.Dialog):
    def __init__(self, parent):
        self.parent = parent
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title="Set Transparency", pos=wx.DefaultPosition,
                           size=(300, 150), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.STAY_ON_TOP)
        slider = wx.Slider(self, 100, 100, 0, 255, size=(250, 100),
                           style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)
        slider.SetTickFreq(10)
        slider.SetValue(self.parent.transparency)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(slider, 0, wx.LEFT, 10)
        self.SetSizer(sizer)
        self.Bind(wx.EVT_SLIDER, self.on_slide)

    def on_slide(self, event):
        x = event.Selection
        self.parent.transparency = x
        self.parent.SetTransparent(max(x, 10))  # unexpectedly printing alpha on console with DeprecationWarning


app = wx.App()
MainWindow(None)
# wx.lib.inspection.InspectionTool().Show() # for debugging
app.MainLoop()
