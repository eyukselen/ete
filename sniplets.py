from collections import defaultdict
import wx
from wx import TreeCtrl
import os.path
import json
from sniplet_edit import SnipletEditor
from configs import icons
import io
import zlib
import base64
from epytree import Tree

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
        self.load_tree()
        self.dragging_node = None

        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.on_begin_drag)
        self.Bind(wx.EVT_TREE_END_DRAG, self.on_end_drag)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_selection_changed)

    def build_child_nodes(self, nod):
        child, cookie = self.GetFirstChild(nod)
        while child.IsOk():
            parent = self.GetItemParent(child)
            parent_id = self.GetItemData(parent)
            snip_id = self.GetItemData(child)
            node_dic = {'id': snip_id,  # id
                        'parent_id': parent_id,  # parent d
                        'text': self.GetItemText(child),  # label
                        'data': self.node_notes[snip_id],  # associated note
                        'is_expanded': self.IsExpanded(child),  # if expanded
                        }
            self.node_list.append(node_dic)
            if self.GetChildrenCount(child) > 0:
                self.build_child_nodes(child)
            child, cookie = self.GetNextChild(nod, cookie)

    def build_tree(self, nod):
        snip_id = self.GetItemData(nod)
        node_dic = {'id': snip_id,  # id
                    'parent_id': 0,  # root parent_id
                    'text': self.GetItemText(nod),  # label
                    'data': self.node_notes[snip_id],  # associated note
                    'is_expanded': self.IsExpanded(nod),  # if it is expanded
                    }
        self.node_list = []
        self.node_list.append(node_dic)
        if self.GetChildrenCount(nod) > 0:
            self.build_child_nodes(nod)
        return self.node_list

    def on_selection_changed(self, event):
        node = event.GetItem()
        self.current_node = node
        self.SelectItem(node, True)
        # self.SetFocusedItem(node)
        self.SetFocus()
        self.Refresh()

    def get_children(self, search_node):
        node, cookie = self.GetFirstChild(search_node)
        while node.IsOk():
            self.dummy_list.append(node)
            if self.GetChildrenCount(node) > 0:
                self.get_children(node)
            node, cookie = self.GetNextChild(search_node, cookie)
        return self.dummy_list

    def check_can_move(self, source_node, target_node):
        res = True
        childs = self.get_children(source_node)
        if target_node in childs:
            res = False
        self.dummy_list = []
        return res

    def on_begin_drag(self, event):
        if not self.dragging_node:
            self.dragging_node = event.GetItem()
        if self.dragging_node:
            event.Allow()

    def copy_node(self, source_node, target_node):
        expand_collapse = []
        new_node = self.AppendItem(parent=target_node,
                                   text=self.GetItemText(source_node),
                                   data=self.GetItemData(source_node),)
        expand_collapse.append((new_node, self.IsExpanded(source_node)))
        if self.GetChildrenCount(source_node) > 0:
            childs = self.get_children(source_node)
            for child in childs:
                self.copy_node(child, new_node)
        for node, state in expand_collapse:
            if state:
                self.Expand(node)

    def on_end_drag(self, event):
        # TODO this needs review for move sub item to parent
        target_node = event.GetItem()
        if self.check_can_move(self.dragging_node, target_node):
            if self.dragging_node:
                if target_node:
                    event.Allow()
                    self.copy_node(self.dragging_node, target_node)
                    self.Delete(self.dragging_node)
                    self.dragging_node = None
                    self.Refresh()

    def get_parent_node(self, node):
        parent_node = self.GetItemParent(node)
        return parent_node

    def get_current_node(self):
        if self.GetFocusedItem():
            self.current_node = self.GetFocusedItem()
        else:
            self.current_node = self.root
        return self.current_node

    def add_node(self):
        node = self.get_current_node()
        self.node_counter += 1
        new_node = self.AppendItem(parent=node, text='New '
                                   + str(self.node_counter),
                                   data=self.node_counter)
        self.SelectItem(new_node, True)
        self.SetFocusedItem(new_node)
        self.SetFocus()
        self.Refresh()

    def del_node(self):
        node = self.get_current_node()
        self.Delete(node)
        self.Refresh()

    def edit_node(self):
        item = self.GetFocusedItem()
        snip_id = self.GetItemData(item)
        snip_name = self.GetItemText(item)
        snip_body = self.node_notes[snip_id]
        if item.IsOk():
            se = SnipletEditor(self, snip_name=snip_name, snip_body=snip_body)
            res = se.ShowModal()
            if res == wx.ID_OK:
                snip_name = se.snip_name
                snip_body = se.snip_body
                self.SetItemText(item, snip_name)
                self.node_notes[snip_id] = snip_body
            if res == wx.ID_CANCEL:
                pass
            se.Destroy()

    def save_tree(self):
        dumptree = self.build_tree(self.GetRootItem())
        with open(self.file, "w") as file:
            json.dump(dumptree, file)

    def load_find_node(self, search_id, root_item):
        if search_id == 0:
            return self.GetRootItem()
        item, cookie = self.GetFirstChild(root_item)
        while item.IsOk():
            node_id = self.GetItemData(item)
            if node_id == search_id:
                return item
            if self.ItemHasChildren(item):
                match = self.load_find_node(search_id, item)
                if match.IsOk():
                    return match
            item, cookie = self.GetNextChild(root_item, cookie)

        return wx.TreeItemId()

    def load_tree(self):
        if not os.path.exists(self.file):
            return
        self.tree.load(self.file)
        self.DeleteAllItems()
        nid = self.AddRoot(text=self.tree.root.name, data=self.tree.root.id)

        for idx, node in self.tree.map.items():
            parent = self.load_find_node(node.parent_id, self.GetRootItem())
            print(parent)
            self.AppendItem(parent,
                            text=node.name,
                            data=node.id
                            )

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
