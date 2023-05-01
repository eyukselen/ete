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


class Explorer_Tree(TreeCtrl):
    def __init__(self, parent):
        TreeCtrl.__init__(self, parent,
                          style=wx.TR_FULL_ROW_HIGHLIGHT |
                          wx.TR_LINES_AT_ROOT |
                          wx.TR_HAS_BUTTONS |
                          wx.TR_SINGLE |
                          wx.TR_TWIST_BUTTONS |
                          wx.TR_EDIT_LABELS)

        self.populate()
        self.tree_popup = wx.Menu()
        self.tree_popup_open = wx.MenuItem(self.tree_popup, wx.ID_ANY, "Open")
        self.tree_popup_close = wx.MenuItem(self.tree_popup, wx.ID_ANY, "Close")
        self.tree_popup.Append(self.tree_popup_open)
        self.Bind(wx.EVT_MENU, self.node_open, self.tree_popup_open)
        self.tree_popup.Append(self.tree_popup_close)
        self.Bind(wx.EVT_MENU, self.node_close, self.tree_popup_close)
        self.Bind(wx.EVT_RIGHT_UP, self.on_popup)
        # self.current_node = self.root
        # self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.on_begin_drag)
        # self.Bind(wx.EVT_TREE_END_DRAG, self.on_end_drag)
        # self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_selection_changed)

    def on_popup(self, event):
        self.PopupMenu(self.tree_popup, pos=event.GetPosition())
        event.Skip()

    def node_open(self, event):
        print(event, "node open")

    def node_close(self, event):
        print(event, "node close")

    def populate(self, pth=None):
        if pth is None:
            pth = os.getcwd()
        if not os.path.isdir(pth):
            return
        root_pth = os.path.dirname(pth.rstrip('/'))
        root_name = os.path.basename(pth.rstrip('/'))
        self.root = self.AddRoot(text=root_name, data=root_pth)
        self.populate_expand(self.root)
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

    # def build_child_nodes(self, nod):
    #     child, cookie = self.GetFirstChild(nod)
    #     while child.IsOk():
    #         parent = self.GetItemParent(child)
    #         parent_id = self.GetItemData(parent)
    #         snip_id = self.GetItemData(child)
    #         node_dic = {'id': snip_id,  # id
    #                     'parent_id': parent_id,  # parent d
    #                     'text': self.GetItemText(child),  # label
    #                     'data': self.node_notes[snip_id],  # associated note
    #                     'is_expanded': self.IsExpanded(child),  # if expanded
    #                     }
    #         self.node_list.append(node_dic)
    #         if self.GetChildrenCount(child) > 0:
    #             self.build_child_nodes(child)
    #         child, cookie = self.GetNextChild(nod, cookie)

    # def on_selection_changed(self, event):
    #     node = event.GetItem()
    #     self.current_node = node
    #     self.SelectItem(node, True)
    #     # self.SetFocusedItem(node)
    #     self.SetFocus()
    #     self.Refresh()

    # def check_can_move(self, source_node, target_node):
    #     res = True
    #     childs = self.get_children(source_node)
    #     if target_node in childs:
    #         res = False
    #     self.dummy_list = []
    #     return res

    # def on_begin_drag(self, event):
    #     if not self.dragging_node:
    #         self.dragging_node = event.GetItem()
    #     if self.dragging_node:
    #         event.Allow()

    # def copy_node(self, source_node, target_node):
    #     expand_collapse = []
    #     new_node = self.AppendItem(parent=target_node,
    #                                text=self.GetItemText(source_node),
    #                                data=self.GetItemData(source_node),)
    #     expand_collapse.append((new_node, self.IsExpanded(source_node)))
    #     if self.GetChildrenCount(source_node) > 0:
    #         childs = self.get_children(source_node)
    #         for child in childs:
    #             self.copy_node(child, new_node)
    #     for node, state in expand_collapse:
    #         if state:
    #             self.Expand(node)

    # def on_end_drag(self, event):
    #     self.target_node = event.GetItem()
    #     if self.check_can_move(self.dragging_node, self.target_node):
    #         if self.dragging_node:
    #             if self.target_node:
    #                 event.Allow()
    #                 self.copy_node(self.dragging_node, self.target_node)
    #                 self.Delete(self.dragging_node)
    #                 self.dragging_node = None
    #                 self.Refresh()

    # def get_parent_node(self, node):
    #     parent_node = self.GetItemParent(node)
    #     return parent_node

    # def get_current_node(self):
    #     if self.GetFocusedItem():
    #         self.current_node = self.GetFocusedItem()
    #     else:
    #         self.current_node = self.root
    #     return self.current_node


class Tree_Control(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.main_sizer)

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

        self.explorer = Explorer_Tree(parent=self)

        self.main_sizer.Add(self.tool_bar, 0, wx.EXPAND)
        self.main_sizer.Add(self.explorer, 2, wx.EXPAND)
        self.tool_bar.Realize()
        self.Refresh()

        self.Bind(wx.EVT_MENU, self.on_add_node, id=wx.ID_ADD)
        self.Bind(wx.EVT_MENU, self.on_del_node, id=wx.ID_DELETE)
        self.Bind(wx.EVT_MENU, self.on_edit_node, id=wx.ID_EDIT)
        self.Bind(wx.EVT_MENU, self.on_save_tree, id=wx.ID_SAVE)

    def on_save_tree(self, _):
        self.explorer.save_tree()

    def on_add_node(self, _):
        self.explorer.add_node()

    def on_del_node(self, _):
        self.explorer.del_node()

    def on_edit_node(self, _):
        self.explorer.edit_node()
