import os
import sys
import wx
import wx.adv
import wx.aui as aui
import wx.stc as stc
# import wx.lib.inspection
import FindReplaceDlg as Frd
from TextEditor import TextEditor
# region high dpi settings for windows
if sys.platform == 'win32' or wx.Platform == '__WXMSW__':
    import ctypes
    try:
        # ctypes.windll.shcore.SetProcessDpiAwareness(True)
        ctypes.OleDLL('shcore').SetProcessDpiAwareness(1)
    except (AttributeError, OSError):
        pass
# endregion


class MainWindow(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title='ete - ete text editor')
        self.SetSize((800, 600))
        self.compare_tabs = []
        self.ID_SYNC_SCROLL_R = wx.ID_ANY
        self.ID_SYNC_SCROLL_L = wx.ID_ANY
        self.ID_SYNC_ZOOM_L = wx.ID_ANY
        self.ID_SYNC_ZOOM_R = wx.ID_ANY

        # region icon set
        icon_size = (32, 32)
        new_ico = wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_TOOLBAR, icon_size)
        open_ico = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, icon_size)
        save_ico = wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_TOOLBAR, icon_size)
        save_as_ico = wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE_AS, wx.ART_TOOLBAR, icon_size)
        exit_ico = wx.ArtProvider.GetBitmap(wx.ART_QUIT, wx.ART_TOOLBAR, icon_size)
        info_ico = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_TOOLBAR, icon_size)
        undo_ico = wx.ArtProvider.GetBitmap(wx.ART_UNDO, wx.ART_TOOLBAR, icon_size)
        redo_ico = wx.ArtProvider.GetBitmap(wx.ART_REDO, wx.ART_TOOLBAR, icon_size)
        cut_ico = wx.ArtProvider.GetBitmap(wx.ART_CUT, wx.ART_TOOLBAR, icon_size)
        copy_ico = wx.ArtProvider.GetBitmap(wx.ART_COPY, wx.ART_TOOLBAR, icon_size)
        paste_ico = wx.ArtProvider.GetBitmap(wx.ART_PASTE, wx.ART_TOOLBAR, icon_size)
        delete_ico = wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_TOOLBAR, icon_size)
        select_ico = wx.ArtProvider.GetBitmap(wx.ART_LIST_VIEW, wx.ART_TOOLBAR, icon_size)
        find_ico = wx.ArtProvider.GetBitmap(wx.ART_FIND, wx.ART_TOOLBAR, icon_size)
        replace_ico = wx.ArtProvider.GetBitmap(wx.ART_FIND_AND_REPLACE, wx.ART_TOOLBAR, icon_size)
        about_ico = wx.ArtProvider.GetBitmap(wx.ART_HELP_BOOK, wx.ART_TOOLBAR, icon_size)
        # endregion

        # region menu definition

        # region file menu
        self.menu_file = wx.Menu()
        self.menu_file_new = wx.MenuItem(parentMenu=self.menu_file, id=wx.ID_NEW, text='&New\tCTRL+N',
                                         kind=wx.ITEM_NORMAL)
        self.menu_file_new.SetBitmap(new_ico)
        self.menu_file.Append(self.menu_file_new)

        self.menu_file_open = wx.MenuItem(parentMenu=self.menu_file, id=wx.ID_OPEN, text='&Open\tCTRL+O',
                                          kind=wx.ITEM_NORMAL)
        self.menu_file_open.SetBitmap(open_ico)
        self.menu_file.Append(self.menu_file_open)

        self.menu_file_save = wx.MenuItem(parentMenu=self.menu_file, id=wx.ID_SAVE, text='&Save\tCTRL+S',
                                          kind=wx.ITEM_NORMAL)
        self.menu_file_save.SetBitmap(save_ico)
        self.menu_file.Append(self.menu_file_save)

        self.menu_file_save_as = wx.MenuItem(parentMenu=self.menu_file, id=wx.ID_SAVEAS, text='Save &As\tCTRL+SHIFT+S',
                                             kind=wx.ITEM_NORMAL)
        self.menu_file_save_as.SetBitmap(save_as_ico)
        self.menu_file.Append(self.menu_file_save_as)

        self.menu_file.AppendSeparator()

        self.menu_file_exit = wx.MenuItem(parentMenu=self.menu_file, id=wx.ID_EXIT, text='E&xit', kind=wx.ITEM_NORMAL)
        self.menu_file_exit.SetBitmap(exit_ico)
        self.menu_file.Append(self.menu_file_exit)
        # did not add \tCTRL+X as it is conflicting with 'Cut'

        # endregion

        # region edit menu
        self.menu_edit = wx.Menu()
        self.menu_edit_undo = wx.MenuItem(parentMenu=self.menu_edit, id=wx.ID_UNDO, text='&Undo\tCTRL+Z',
                                          kind=wx.ITEM_NORMAL)
        self.menu_edit_undo.SetBitmap(undo_ico)
        self.menu_edit.Append(self.menu_edit_undo)

        self.menu_edit_redo = wx.MenuItem(parentMenu=self.menu_edit, id=wx.ID_REDO, text='&Redo\tCTRL+Y',
                                          kind=wx.ITEM_NORMAL)
        self.menu_edit_redo.SetBitmap(redo_ico)
        self.menu_edit.Append(self.menu_edit_redo)

        self.menu_edit.AppendSeparator()

        self.menu_edit_cut = wx.MenuItem(parentMenu=self.menu_edit, id=wx.ID_CUT, text='Cu&t\tCTRL+X',
                                         kind=wx.ITEM_NORMAL)
        self.menu_edit_cut.SetBitmap(cut_ico)
        self.menu_edit.Append(self.menu_edit_cut)

        self.menu_edit_copy = wx.MenuItem(parentMenu=self.menu_edit, id=wx.ID_COPY, text='&Copy\tCTRL+C',
                                          kind=wx.ITEM_NORMAL)
        self.menu_edit_copy.SetBitmap(copy_ico)
        self.menu_edit.Append(self.menu_edit_copy)

        self.menu_edit_paste = wx.MenuItem(parentMenu=self.menu_edit, id=wx.ID_PASTE, text='&Paste\tCTRL+V',
                                           kind=wx.ITEM_NORMAL)
        self.menu_edit_paste.SetBitmap(paste_ico)
        self.menu_edit.Append(self.menu_edit_paste)

        self.menu_edit.AppendSeparator()

        self.menu_edit_find = wx.MenuItem(parentMenu=self.menu_edit, id=wx.ID_FIND, text='&Find\tCTRL+F',
                                          kind=wx.ITEM_NORMAL)
        self.menu_edit_find.SetBitmap(find_ico)
        self.menu_edit.Append(self.menu_edit_find)

        self.menu_edit_replace = wx.MenuItem(parentMenu=self.menu_edit, id=wx.ID_REPLACE, text='&Replace\tCTRL+R',
                                             kind=wx.ITEM_NORMAL)
        self.menu_edit_replace.SetBitmap(replace_ico)
        self.menu_edit.Append(self.menu_edit_replace)

        self.menu_edit_jump_to = wx.MenuItem(parentMenu=self.menu_edit, id=wx.ID_JUMP_TO, text='Jump To\tCTRL+J',
                                             kind=wx.ITEM_NORMAL)
        self.menu_edit_jump_to.SetBitmap(select_ico)
        self.menu_edit.Append(self.menu_edit_jump_to)

        self.menu_edit.AppendSeparator()

        self.menu_edit_delete = wx.MenuItem(parentMenu=self.menu_edit, id=wx.ID_DELETE, text='Delete',
                                            kind=wx.ITEM_NORMAL)
        self.menu_edit_delete.SetBitmap(delete_ico)
        self.menu_edit.Append(self.menu_edit_delete)

        self.menu_edit_select_all = wx.MenuItem(parentMenu=self.menu_edit, id=wx.ID_SELECTALL, text='Select All',
                                                kind=wx.ITEM_NORMAL)
        self.menu_edit_select_all.SetBitmap(select_ico)
        self.menu_edit.Append(self.menu_edit_select_all)

        self.menu_edit.AppendSeparator()

        self.menu_edit_uppercase = wx.MenuItem(parentMenu=self.menu_edit, id=wx.ID_ANY, text='Upper Case',
                                               kind=wx.ITEM_NORMAL)
        self.menu_edit.Append(self.menu_edit_uppercase)

        self.menu_edit_lowercase = wx.MenuItem(parentMenu=self.menu_edit, id=wx.ID_ANY, text='Lower Case',
                                               kind=wx.ITEM_NORMAL)
        self.menu_edit.Append(self.menu_edit_lowercase)
        # endregion

        # region view menu
        self.menu_view = wx.Menu()
        self.menu_view_whitespace = wx.MenuItem(parentMenu=self.menu_view, id=wx.ID_ANY, text='Show White Space',
                                                kind=wx.ITEM_NORMAL)
        self.menu_view.Append(self.menu_view_whitespace)

        self.menu_view_eol = wx.MenuItem(parentMenu=self.menu_view, id=wx.ID_ANY, text='Show End Of Line',
                                         kind=wx.ITEM_NORMAL)
        self.menu_view.Append(self.menu_view_eol)

        self.menu_view_indentguide = wx.MenuItem(parentMenu=self.menu_view, id=wx.ID_ANY,
                                                 text='Show Indentation Guides', kind=wx.ITEM_NORMAL)
        self.menu_view.Append(self.menu_view_indentguide)

        self.menu_view.AppendSeparator()

        self.menu_view_wrap = wx.MenuItem(parentMenu=self.menu_view, id=wx.ID_ANY, text='Wrap', kind=wx.ITEM_NORMAL)
        self.menu_view.Append(self.menu_view_wrap)

        self.menu_view.AppendSeparator()

        self.menu_view_transparent = wx.MenuItem(parentMenu=self.menu_view, id=wx.ID_ANY, text='Transparent',
                                                 kind=wx.ITEM_CHECK)
        self.menu_view.Append(self.menu_view_transparent)
        # endregion

        # region language menu
        self.menu_language = wx.Menu()
        self.menu_language_txt = wx.MenuItem(parentMenu=self.menu_language, id=wx.ID_ANY, text='Text',
                                             kind=wx.ITEM_NORMAL)
        self.menu_language.Append(self.menu_language_txt)

        self.menu_language_python = wx.MenuItem(parentMenu=self.menu_language, id=wx.ID_ANY, text='Python',
                                                kind=wx.ITEM_NORMAL)
        self.menu_language.Append(self.menu_language_python)

        self.menu_language_sql = wx.MenuItem(parentMenu=self.menu_language, id=wx.ID_ANY, text='SQL',
                                             kind=wx.ITEM_NORMAL)
        self.menu_language.Append(self.menu_language_sql)
        # endregion

        # region tools menu
        self.menu_tools = wx.Menu()
        self.menu_tool_compare = wx.MenuItem(parentMenu=self.menu_tools, id=wx.ID_ANY, text='&Compare',
                                             kind=wx.ITEM_NORMAL)
        self.menu_tools.Append(self.menu_tool_compare)
        self.menu_tools_clear_compare = wx.MenuItem(parentMenu=self.menu_tools, id=wx.ID_ANY, text='Clea&r Compare',
                                                    kind=wx.ITEM_NORMAL)
        self.menu_tools.Append(self.menu_tools_clear_compare)
        # endregion

        # region about menu
        self.menu_about = wx.Menu()
        self.menu_about_about = wx.MenuItem(parentMenu=self.menu_about, id=wx.ID_ABOUT, text='About',
                                            kind=wx.ITEM_NORMAL)
        self.menu_about_about.SetBitmap(about_ico)
        self.menu_about.Append(self.menu_about_about)
        # endregion

        self.menu_bar = wx.MenuBar()

        self.menu_bar.Append(self.menu_file, '&File')
        self.menu_bar.Append(self.menu_edit, '&Edit')
        self.menu_bar.Append(self.menu_view, '&View')
        self.menu_bar.Append(self.menu_language, '&Language')
        self.menu_bar.Append(self.menu_tools, '&Tools')
        self.menu_bar.Append(self.menu_about, '&About')

        self.SetMenuBar(self.menu_bar)

        # endregion

        # region toolbar definition
        self.tool_bar = wx.ToolBar(self)

        self.tool_bar.AddTool(toolId=wx.ID_NEW, label='New', bitmap=new_ico, bmpDisabled=new_ico, kind=wx.ITEM_NORMAL,
                              shortHelp='New File', longHelp='', clientData=None)
        self.tool_bar.AddTool(toolId=wx.ID_OPEN, label='Open', bitmap=open_ico, bmpDisabled=open_ico,
                              kind=wx.ITEM_NORMAL, shortHelp='Open File', longHelp='', clientData=None)
        self.tool_bar.AddTool(toolId=wx.ID_SAVE, label='Save', bitmap=save_ico, bmpDisabled=save_ico,
                              kind=wx.ITEM_NORMAL, shortHelp='Save File', longHelp='', clientData=None)
        self.tool_bar.AddTool(toolId=wx.ID_SAVEAS, label='Save As', bitmap=save_as_ico, bmpDisabled=new_ico,
                              kind=wx.ITEM_NORMAL, shortHelp='Save File As', longHelp='', clientData=None)
        self.tool_bar.AddSeparator()
        self.tool_bar.AddTool(toolId=wx.ID_CUT, label='Cut', bitmap=cut_ico, bmpDisabled=cut_ico, kind=wx.ITEM_NORMAL,
                              shortHelp='Cut', longHelp='Cut Text', clientData=None)
        self.tool_bar.AddTool(toolId=wx.ID_COPY, label='Copy', bitmap=copy_ico, bmpDisabled=copy_ico,
                              kind=wx.ITEM_NORMAL, shortHelp='Copy', longHelp='Copy Text', clientData=None)
        self.tool_bar.AddTool(toolId=wx.ID_PASTE, label='Paste', bitmap=paste_ico, bmpDisabled=paste_ico,
                              kind=wx.ITEM_NORMAL, shortHelp='Paste', longHelp='Paste Text', clientData=None)
        self.tool_bar.AddSeparator()
        self.tool_bar.AddTool(toolId=wx.ID_FIND, label='Find', bitmap=find_ico, bmpDisabled=find_ico,
                              kind=wx.ITEM_NORMAL, shortHelp='Find', longHelp='Find Text', clientData=None)
        self.tool_bar.AddTool(toolId=wx.ID_REPLACE, label='Replace Text', bitmap=replace_ico, bmpDisabled=replace_ico,
                              kind=wx.ITEM_NORMAL,
                              shortHelp='Replace', longHelp='Replace Text', clientData=None)
        self.tool_bar.AddSeparator()
        self.tool_bar.AddTool(toolId=wx.ID_INFO, label='Info', bitmap=info_ico, bmpDisabled=info_ico,
                              kind=wx.ITEM_NORMAL, shortHelp='Information', longHelp='', clientData=None)
        self.tool_bar.AddTool(toolId=wx.ID_EXIT, label='Exit', bitmap=exit_ico, bmpDisabled=exit_ico,
                              kind=wx.ITEM_NORMAL, shortHelp='Exit Application', longHelp='', clientData=None)

        self.SetToolBar(self.tool_bar)
        self.tool_bar.Realize()
        # endregion

        # region main panel definition

        self.main_panel = wx.Panel(parent=self)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_panel.SetSizer(self.main_sizer)
        self.main_panel.DragAcceptFiles(True)
        self.main_panel.Bind(wx.EVT_DROP_FILES, self.open_page)

        # endregion

        # region tabbed notebook definition

        self.notebook = aui.AuiNotebook(parent=self.main_panel,
                                        style=aui.AUI_NB_CLOSE_ON_ALL_TABS |
                                        aui.AUI_NB_DEFAULT_STYLE |
                                        aui.AUI_NB_WINDOWLIST_BUTTON)
        self.main_sizer.Add(self.notebook, 1, wx.EXPAND)

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

        # region status bar

        self.status_bar = wx.StatusBar(self)
        self.status_bar.SetFieldsCount(2, [-2, -1])
        self.SetStatusBar(self.status_bar)

        # endregion

        # region event bindings

        self.Bind(wx.EVT_MENU, self.new_page, id=wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.open_page, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.save_page, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.save_as_page, id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.on_info, id=wx.ID_INFO)
        self.Bind(wx.EVT_MENU, self.onexit, id=wx.ID_EXIT)

        self.Bind(wx.EVT_MENU, self.on_menu_edit_event, id=wx.ID_UNDO)
        self.Bind(wx.EVT_MENU, self.on_menu_edit_event, id=wx.ID_REDO)
        self.Bind(wx.EVT_MENU, self.on_menu_edit_event, id=wx.ID_CUT)
        self.Bind(wx.EVT_MENU, self.on_menu_edit_event, id=wx.ID_COPY)
        self.Bind(wx.EVT_MENU, self.on_menu_edit_event, id=wx.ID_PASTE)
        self.Bind(wx.EVT_MENU, self.on_menu_edit_event, id=wx.ID_DELETE)
        self.Bind(wx.EVT_MENU, self.on_menu_edit_event, id=wx.ID_SELECTALL)
        self.Bind(wx.EVT_MENU, self.on_find, id=wx.ID_FIND)
        self.Bind(wx.EVT_MENU, self.on_find, id=wx.ID_REPLACE)  # using the same dialog as find for now.
        self.Bind(wx.EVT_MENU, self.on_jump_to, id=wx.ID_JUMP_TO)
        self.Bind(wx.EVT_MENU, self.on_about, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.on_language, self.menu_language_txt)
        self.Bind(wx.EVT_MENU, self.on_language, self.menu_language_python)
        self.Bind(wx.EVT_MENU, self.on_language, self.menu_language_sql)

        self.Bind(wx.EVT_MENU, self.on_view_whitespace, self.menu_view_whitespace)
        self.Bind(wx.EVT_MENU, self.on_view_eol, self.menu_view_eol)
        self.Bind(wx.EVT_MENU, self.on_view_indent_guide, self.menu_view_indentguide)
        self.Bind(wx.EVT_MENU, self.on_view_wrap, self.menu_view_wrap)
        self.Bind(wx.EVT_MENU, self.on_view_transparent, self.menu_view_transparent)

        self.Bind(wx.EVT_MENU, self.on_menu_tools_compare, self.menu_tool_compare)
        self.Bind(wx.EVT_MENU, self.on_menu_tools_clear_compare, self.menu_tools_clear_compare)
        self.Bind(wx.EVT_MENU, self.on_menu_edit_case, self.menu_edit_uppercase)
        self.Bind(wx.EVT_MENU, self.on_menu_edit_case, self.menu_edit_lowercase)

        # detect double click on tab bar empty space
        self.Bind(aui.EVT_AUINOTEBOOK_BG_DCLICK, self.new_page, id=wx.ID_ANY)  # ID_ANY?
        self.Bind(aui.EVT_AUINOTEBOOK_TAB_RIGHT_UP, self.on_tab_popup, id=wx.ID_ANY)

        self.notebook.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.on_tab_close, id=wx.ID_ANY)
        self.Bind(wx.EVT_CLOSE, self.onclose)

        # endregion

        self.search_dlg = Frd.FindReplaceDlg(parent=self, notebook=self.notebook)
        self.info = wx.adv.AboutDialogInfo()
        self.Show()

    def get_text_editor_from_page(self, page_idx):
        page = self.notebook.GetPage(page_idx)
        if page:
            for widget in page.GetChildren():
                if isinstance(widget, TextEditor):
                    return widget
                else:
                    return None

    def on_view_transparent(self, _):
        if self.menu_view_transparent.IsChecked():
            self.SetTransparent(128)
        else:
            self.SetTransparent(255)

    def on_about(self, _):
        self.info.SetName("Emre's text editor")
        self.info.SetVersion('0.1')
        self.info.SetDescription('This is a project about my experiment with wxpython')
        self.info.SetDevelopers(['Emre Yukselen'])
        wx.adv.AboutBox(self.info)

    def new_page(self, _):
        page = wx.Panel(parent=self.notebook)
        page_sizer = wx.BoxSizer(wx.VERTICAL)
        page.SetSizer(page_sizer)
        te = TextEditor(parent=page, filename='')
        te.DragAcceptFiles(True)
        te.Bind(wx.EVT_DROP_FILES, self.open_page)
        page_sizer.Add(te, 1, wx.EXPAND)
        self.notebook.AddPage(page, 'New *', select=True)

    def open_page(self, event):
        if hasattr(event, 'Files'):
            files = event.GetFiles()
        elif event.GetId() == wx.ID_OPEN:
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
                te.DragAcceptFiles(True)
                te.Bind(wx.EVT_DROP_FILES, self.open_page)
                page_sizer.Add(te, 1, wx.EXPAND)
                self.notebook.AddPage(page, select=True, caption=file_name)
                te.LoadFile(file)
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
                te.SaveFile(filename)
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
            te.SaveFile(filename)
            te.file_name = filename
            self.notebook.SetPageToolTip(self.notebook.GetPageIndex(self.notebook.GetCurrentPage()), filename)
            _, file = os.path.split(filename)
            self.notebook.SetPageText(self.notebook.GetPageIndex(self.notebook.GetCurrentPage()), file)

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
            e = wx.MenuEvent(wx.EVT_MENU.typeId, self.menu_tools_clear_compare.GetId())
            wx.PostEvent(self, e)

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
        pass

    def on_menu_tools_compare(self, _):
        if len(self.compare_tabs) == 2:  # already in compare so do nothing to avoid confusion
            return

        # region splitting window for compare
        rpi = self.notebook.GetPageIndex(self.notebook.GetCurrentPage())
        if rpi < 1:  # there should be at least 1 tab left to active tab
            return
        lpi = rpi - 1

        lstc = self.get_text_editor_from_page(lpi)
        rstc = self.get_text_editor_from_page(rpi)

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

        for x in res:
            for _ in x[1]:
                if x[0] == '-':
                    lstc.StartStyling(lstc.XYToPosition(0, c), 255)
                    lstc.SetStyling(lstc.GetLineLength(c) + 2, 5)
                    pos = max(rstc.XYToPosition(0, c), 0)
                    rstc.InsertText(pos, '\r\n')  # add empty line to right
                    rstc.SetLineState(c, 1)
                if x[0] == '+':
                    pos = max(lstc.XYToPosition(0, c), 0)
                    lstc.InsertText(pos, '\r\n')  # add empty line to left
                    lstc.SetLineState(c, 1)
                    rstc.StartStyling(rstc.XYToPosition(0, c), 255)
                    rstc.SetStyling(rstc.GetLineLength(c) + 2, 5)
                if x[0] == '=':
                    lstc.StartStyling(lstc.XYToPosition(0, c,), 255)
                    lstc.SetStyling(lstc.GetLineLength(c) + 2, 4)
                    rstc.StartStyling(rstc.XYToPosition(0, c, ), 255)
                    rstc.SetStyling(rstc.GetLineLength(c) + 2, 4)
                c += 1
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
                lstc.LineDelete()

        for i in range(rstc.GetMaxLineState(), -1, -1):
            if rstc.GetLineState(i) == 1 and rstc.GetLineText(i) == '':
                rstc.GotoLine(i)
                rstc.LineDelete()

        lstc.StyleClearAll()  # if there is pre-set style I need to check that
        rstc.StyleClearAll()

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
        # restore orignial selected tab
        self.notebook.SetSelection(now_selected)

        self.Thaw()

    def set_tabs_in_sync(self, lstc, rstc, activate):
        # DONE : in compare mode caret freezes until text area clicked. after switching to wx.aui this is working fine
        # DONE : two carets are visible at the same time one on lstc and one on rstc, after switching to wx.aui its fine
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
                # now we are considering all values of iold such that
                # `old[iold] == new[inew]`.
                _overlap[iold] = (iold and overlap.get(iold - 1, 0)) + 1
                if _overlap[iold] > sub_length:
                    # this is the largest substring seen so far, so store its
                    # indices
                    sub_length = _overlap[iold]
                    sub_start_old = iold - sub_length + 1
                    sub_start_new = inew - sub_length + 1
            overlap = _overlap

        if sub_length == 0:
            # If no common substring is found, we return an insert and delete...
            return (old and [('-', old)] or []) + (new and [('+', new)] or [])
        else:
            # ...otherwise, the common substring is unchanged and we recursively
            # diff the text before and after that substring
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
        cp = self.notebook.GetCurrentPage()  # return none if there is no page open
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

    def on_language(self, event):
        if self.notebook.GetPageCount() == 0:
            return
        if event.GetId() == self.menu_language_python.GetId():
            lang = 'python'
        elif event.GetId() == self.menu_language_sql.GetId():
            lang = 'mssql'
        elif event.GetId() == self.menu_language_txt.GetId():
            lang = 'txt'
        else:
            lang = 'txt'
        cp = self.notebook.GetCurrentPage()
        te = self.get_text_editor_from_page(self.notebook.GetPageIndex(cp))
        te.set_lang(lang)

    def on_menu_edit_case(self, event):
        if self.notebook.GetPageCount() == 0:
            return
        cs = None
        if event.GetId() == self.menu_edit_uppercase.GetId():
            cs = 'upper'
        elif event.GetId() == self.menu_edit_lowercase.GetId():
            cs = 'lower'
        cp = self.notebook.GetCurrentPage()
        te = self.get_text_editor_from_page(self.notebook.GetPageIndex(cp))
        te.set_case(cs)


app = wx.App()
MainWindow(None)
# wx.lib.inspection.InspectionTool().Show()
app.MainLoop()

# 4.0.7.post2 msw (phoenix) wxWidgets 3.0.5
# 3.7.4 (tags/v3.7.4:e09359112e, Jul  8 2019, 20:34:20) [MSC v.1916 64 bit (AMD64)]
# upgraded to
# 3.8.3 (tags/v3.8.3:6f8c832, May 13 2020, 22:37:02) [MSC v.1924 64 bit (AMD64)]
# 4.1.0 msw (phoenix) wxWidgets 3.1.4
# Scintilla 3.7.2