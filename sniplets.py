import wx
from wx import TreeCtrl
from sniplet_edit import SnipletEditor
from configs import icons
import io
import zlib
import base64
from epytree import Tree, Node


def get_icon(name):
    with io.BytesIO(zlib.decompress(base64.b64decode(icons[name]))) as stream:
        icon = wx.Bitmap(wx.Image(stream))
    return icon


class SnipletTree(TreeCtrl):
    def __init__(self, parent):
        TreeCtrl.__init__(self, parent,
                          style=wx.TR_FULL_ROW_HIGHLIGHT |
                          wx.TR_LINES_AT_ROOT |
                          wx.TR_HAS_BUTTONS |
                          wx.TR_SINGLE |
                          wx.TR_TWIST_BUTTONS |
                          wx.TR_EDIT_LABELS)
        # self.file = 'sniplets.json'
        self.file = 'tree.json'
        self.tree = Tree()
        self.tree.load(self.file)  # load tree data
        self.populate_tree()
        self.dragging_node = None

        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.on_begin_drag)
        self.Bind(wx.EVT_TREE_END_DRAG, self.on_end_drag)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.on_expanded)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.on_collapsed)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_activate)

    def populate_tree(self):
        if self.GetRootItem().IsOk():
            self.Delete(self.GetRootItem())
        self.AddRoot(text=self.tree.root.name, data=self.tree.root.id)
        self.populate_children(self.GetRootItem(), self.tree.root)
        self.apply_expands()
        self.Refresh()

    def on_expanded(self, event):
        nod = event.GetItem()
        idx = self.GetItemData(nod)
        self.tree.map[idx].is_expanded = True
        event.Skip()

    def on_collapsed(self, event):
        nod = event.GetItem()
        idx = self.GetItemData(nod)
        self.tree.map[idx].is_expanded = False
        event.Skip()

    def apply_expands(self):
        if len(self.tree.map) < 1:
            return
        for idx, node in self.tree.map.items():
            tree_item_id = self.find_node_by_id(idx, self.GetRootItem())
            if tree_item_id.IsOk():
                if node.is_expanded:
                    self.Expand(tree_item_id)
                else:
                    self.Collapse(tree_item_id)
        self.Refresh()

    def find_node_by_id(self, search_id, root_item):
        if search_id == 0:
            return self.GetRootItem()
        item, cookie = self.GetFirstChild(root_item)
        while item.IsOk():
            node_id = self.GetItemData(item)
            if node_id == search_id:
                return item
            if self.ItemHasChildren(item):
                match = self.find_node_by_id(search_id, item)
                if match.IsOk():
                    return match
            item, cookie = self.GetNextChild(root_item, cookie)

        return wx.TreeItemId()

    def populate_children(self, vnode, dnode):
        """
        :param vnode: node in treectrl for visual
        :param dnode: node in tree data for actual data
        """
        if len(dnode.children) > 0:
            for idx, node in dnode.children.items():
                vnode_child = self.AppendItem(parent=vnode,
                                              text=node.name,
                                              data=node.id
                                              )
                if len(node.children) > 0:
                    self.populate_children(vnode_child, node)

    def on_activate(self, event):
        nod = event.GetItem()
        self.SetFocusedItem(nod)
        event.Veto()
        self.edit_node()

    def on_begin_drag(self, event):
        if not self.dragging_node:
            self.dragging_node = event.GetItem()
        if self.dragging_node:
            event.Allow()

    def on_end_drag(self, event):
        tgt_nod = event.GetItem()
        tgt_note = self.GetItemData(tgt_nod)
        src_nod = self.dragging_node
        src_note = self.GetItemData(src_nod)
        if src_note and tgt_note:
            self.tree.move_node(src_note, tgt_note)
            self.save_tree()
            self.populate_tree()
            self.Refresh()

    def add_node(self):
        node = self.GetFocusedItem()
        if node.IsOk():
            pass
        else:
            node = self.GetRootItem()

        idx = self.GetItemData(node)
        nod = Node(name='New', data='', parent_id=idx)
        self.tree.add_node(nod, idx)
        self.tree.map[idx].is_expanded = True
        self.save_tree()
        self.populate_tree()
        self.SetFocusedItem(self.find_node_by_id(self.tree.max_id, self.GetRootItem()))
        self.SetFocus()
        self.Refresh()

    def del_node(self):
        node = self.GetFocusedItem()
        idx = self.GetItemData(node)
        print('deleting node id:', idx)
        self.tree.del_node(idx)
        print(self.tree.to_json())
        self.save_tree()
        self.populate_tree()
        self.Refresh()

    def edit_node(self):
        nod = self.GetFocusedItem()
        idx = self.GetItemData(nod)
        snip_name = self.GetItemText(nod)
        snip_body = self.tree.map[idx].data or ''
        if nod.IsOk():
            se = SnipletEditor(self, snip_name=snip_name, snip_body=snip_body)
            res = se.ShowModal()
            if res == wx.ID_OK:
                snip_name = se.snip_name
                snip_body = se.snip_body
                self.SetItemText(nod, snip_name)
                self.tree.map[idx].data = snip_body
                self.tree.map[idx].name = snip_name
            if res == wx.ID_CANCEL:
                pass
            se.Destroy()
        self.save_tree()

    def save_tree(self):
        self.tree.save(self.file)


class SnipletControl(wx.Panel):
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

        self.sniplets = SnipletTree(parent=self)

        self.main_sizer.Add(self.tool_bar, 0, wx.EXPAND)
        self.main_sizer.Add(self.sniplets, 2, wx.EXPAND)
        self.tool_bar.Realize()
        self.Refresh()

        self.Bind(wx.EVT_MENU, self.on_add_node, id=wx.ID_ADD)
        self.Bind(wx.EVT_MENU, self.on_del_node, id=wx.ID_DELETE)
        self.Bind(wx.EVT_MENU, self.on_edit_node, id=wx.ID_EDIT)
        self.Bind(wx.EVT_MENU, self.on_save_tree, id=wx.ID_SAVE)

    def on_save_tree(self, _):
        self.sniplets.save_tree()

    def on_add_node(self, _):
        self.sniplets.add_node()

    def on_del_node(self, _):
        self.sniplets.del_node()

    def on_edit_node(self, _):
        self.sniplets.edit_node()
