from typing import List
import wx
from wx import TreeCtrl
import os
from configs import icons
import io
import zlib
import base64

def get_icon(name):
    with io.BytesIO(zlib.decompress(base64.b64decode(icons[name]))) as stream:
        icon = wx.Bitmap(wx.Image(stream))
    return icon


class FileManager:
    root_path: str
    files: List[str] = []
    open_files: List[str] = []

    def __init__(self, root_path: str) -> None:
        if root_path:
            self.root_path = root_path
        else:
            self.root_path = os.getcwd()

    def add(self, filename):
        pass



class Explorer_Tree(TreeCtrl):
    def __init__(self, parent, main_window):
        TreeCtrl.__init__(self, parent,
                          style=wx.TR_FULL_ROW_HIGHLIGHT |
                          wx.TR_LINES_AT_ROOT |
                          wx.TR_HAS_BUTTONS |
                          wx.TR_SINGLE |
                          wx.TR_TWIST_BUTTONS |
                          wx.TR_EDIT_LABELS)
        self.main_window = main_window

        self.populate()
        self.tree_popup = wx.Menu()
        self.tree_popup_open = wx.MenuItem(self.tree_popup,
                                           wx.ID_ANY, "Open")
        self.tree_popup_close = wx.MenuItem(self.tree_popup,
                                            wx.ID_ANY, "Close")
        self.tree_popup.Append(self.tree_popup_open)
        self.Bind(wx.EVT_MENU, self.on_popup_action, self.tree_popup_open)
        self.tree_popup.Append(self.tree_popup_close)
        self.Bind(wx.EVT_MENU, self.on_popup_action, self.tree_popup_close)
        # self.Bind(wx.EVT_RIGHT_UP, self.on_popup)
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.on_popup)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.node_activated)
        # self.current_node = self.root
        # self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.on_begin_drag)
        # self.Bind(wx.EVT_TREE_END_DRAG, self.on_end_drag)
        # self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_selection_changed)

    def node_activated(self, event):
        node = event.GetItem()
        file_name = os.path.join(self.GetItemData(node),
                                 self.GetItemText(node))
        if os.path.isfile(file_name):
            self.main_window.open_file([file_name, ])
            self.SetItemBold(node)
        event.Skip()

    def on_popup_action(self, event):
        node = self.GetSelection()
        if event.GetId() == self.tree_popup_open.GetId():
            file_name = os.path.join(self.GetItemData(node),
                                     self.GetItemText(node))
            self.node_open(file_name)
            self.SetItemBold(node)
        if event.GetId() == self.tree_popup_close.GetId():
            file_name = os.path.join(self.GetItemData(node),
                                     self.GetItemText(node))
            print('close', file_name)
        event.Skip()

    def on_popup(self, event):
        pos = event.GetPoint()
        self.SelectItem(event.GetItem())
        self.PopupMenu(self.tree_popup, pos=pos)
        event.Skip()

    def node_open(self, file_name):
        self.main_window.open_file(file_name)

    def node_close(self, file_name):
        print("node close")

    def populate(self, pth=None):
        if pth is None:
            pth = os.getcwd()
        if not os.path.isdir(pth):
            return
        root_pth = os.path.dirname(pth.rstrip('/'))
        root_name = os.path.basename(pth.rstrip('/'))
        self.root = self.AddRoot(text=root_name, data=root_pth)
        self.populate_expand(self.root)
        self.Expand(self.root)
        # tk = self.AppendItem(self.root, 'Toolkits')
        # self.AppendItem(tk, 'Qt')

    def populate_expand(self, node):
        # TODO: update this to only refresh selected node not traverse all
        root_pth = self.GetItemData(node)
        pth = self.GetItemText(node)
        res = []
        for item in os.listdir(os.path.join(root_pth, pth)):
            res.append(('d' if os.path.isdir(item) else 'f', item))
        res.sort(key=lambda x: x[0])
        # print(*res, sep='\n')
        self.DeleteChildren(node)
        for item in res:
            if item[0] == 'd':
                nod = self.AppendItem(node, text=item[1],
                                      data=os.path.join(root_pth, pth))
                self.populate_expand(nod)
            if item[0] == 'f':
                self.AppendItem(node, text=item[1],
                                data=os.path.join(root_pth, pth))


class Tree_Control(wx.Panel):
    """This is only a panel to glue together actual
    tree control and some future buttons"""
    def __init__(self, parent, main_window):
        wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.main_sizer)
        self.main_window = main_window

        self.tool_bar = wx.ToolBar(parent=self)
        self.tool_bar.AddTool(toolId=wx.ID_ADD, label='Add',
                              bitmap=get_icon('snip_add'),
                              bmpDisabled=get_icon('snip_add'),
                              kind=wx.ITEM_NORMAL, shortHelp='Add',
                              longHelp='', clientData=None)
        self.tool_bar.AddTool(toolId=wx.ID_DELETE, label='Del',
                              bitmap=get_icon('snip_del'),
                              bmpDisabled=get_icon('snip_del'),
                              kind=wx.ITEM_NORMAL, shortHelp='Delete',
                              longHelp='', clientData=None)
        self.tool_bar.AddTool(toolId=wx.ID_EDIT, label='Edit',
                              bitmap=get_icon('snip_edit'),
                              bmpDisabled=get_icon('snip_edit'),
                              kind=wx.ITEM_NORMAL, shortHelp='Edit',
                              longHelp='', clientData=None)
        self.tool_bar.AddTool(toolId=wx.ID_SAVE, label='Save',
                              bitmap=get_icon('save_ico'),
                              bmpDisabled=get_icon('save_ico'),
                              kind=wx.ITEM_NORMAL, shortHelp='Save',
                              longHelp='', clientData=None)

        self.explorer = Explorer_Tree(parent=self,
                                      main_window=self.main_window)

        self.main_sizer.Add(self.tool_bar, 0, wx.EXPAND)
        self.main_sizer.Add(self.explorer, 2, wx.EXPAND)
        self.tool_bar.Realize()
        self.Refresh()

    #     self.Bind(wx.EVT_MENU, self.on_add_node, id=wx.ID_ADD)
    #     self.Bind(wx.EVT_MENU, self.on_del_node, id=wx.ID_DELETE)
    #     self.Bind(wx.EVT_MENU, self.on_edit_node, id=wx.ID_EDIT)
    #     self.Bind(wx.EVT_MENU, self.on_save_tree, id=wx.ID_SAVE)

    # def on_save_tree(self, _):
    #     self.explorer.save_tree()

    # def on_add_node(self, _):
    #     self.explorer.add_node()

    # def on_del_node(self, _):
    #     self.explorer.del_node()

    # def on_edit_node(self, _):
    #     self.explorer.edit_node()
