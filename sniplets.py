from logging import root
from operator import itemgetter
import wx
from wx import TreeCtrl
import os.path
import pickle

app_dummy = wx.App()
add_ico = wx.ArtProvider.GetBitmap(wx.ART_PLUS, wx.ART_TOOLBAR, (32, 32))
del_ico = wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_TOOLBAR, (32, 32))
edit_ico = wx.ArtProvider.GetBitmap(wx.ART_REPORT_VIEW, wx.ART_TOOLBAR, (32, 32))
save_ico = wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_TOOLBAR, (32, 32))


class Sniplet_Tree(TreeCtrl):
    def __init__(self, parent):
        TreeCtrl.__init__(self, parent,
                          style=wx.TR_FULL_ROW_HIGHLIGHT |
                          wx.TR_LINES_AT_ROOT |
                          wx.TR_HAS_BUTTONS |
                          wx.TR_SINGLE |
                          wx.TR_TWIST_BUTTONS |
                          wx.TR_EDIT_LABELS)
        self.root = self.AddRoot('Sniplets')
        self.SetItemData(self.root, (0, None))
        self.file = 'sniplets.pkl'
        self.dragging_node = None
        self.dummy_list = []
        self.node_counter = 0  # for keeping an Id for all nodes
        self.current_node = self.root
        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.on_begin_drag)
        self.Bind(wx.EVT_TREE_END_DRAG, self.on_end_drag)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_selection_changed)

    def find_list_item(self, items, item_id):
        for item in items:
            if item_id == item[0]:
                return item
            elif isinstance(item[4], list) and len(item[4]) > 0:
                self.find_list_item(item[4], item_id)
        return None

    def build_tree_children(self, node, items):
        child_node, cookie = self.GetFirstChild(node)
        while child_node.IsOk():
            item = [self.GetItemData(child_node)[0],  # id
                    self.GetItemText(child_node),  # label
                    self.GetItemData(child_node)[1],  # data
                    self.IsExpanded(child_node),  # if it is expanded
                    [], ]  # children
            item_to_append_to = self.find_list_item(items, self.GetItemData(self.GetItemParent(child_node))[0])
            print('item parent id' , self.GetItemData(self.GetItemParent(child_node))[0])

            if item_to_append_to:
                item_to_append_to[4].append(item)
            if self.GetChildrenCount(child_node) > 0:
                self.build_tree_children(child_node, items)
            child_node, cookie = self.GetNextChild(self.root, cookie)

    def build_tree(self):
        node_list = [[self.GetItemData(self.root)[0],  # id
                     self.GetItemText(self.root),  # label
                     self.GetItemData(self.root)[1],  # data
                     self.IsExpanded(self.root),  # if it is expanded
                     []], ]  # children
        if self.GetChildrenCount(self.root) > 0:
            self.build_tree_children(self.root, node_list)
        return node_list

    def on_selection_changed(self, event):
        node = event.GetItem()
        self.current_node = node
        self.SelectItem(node, True)
        # self.SetFocusedItem(node)
        self.SetFocus()
        self.Refresh()

    def get_children(self, search_node):
        # print('searching node:' + self.GetItemText(search_node))
        node, cookie = self.GetFirstChild(search_node)
        while node.IsOk():
            self.dummy_list.append(node)
            # print('found: ' + self.GetItemText(node))
            if self.GetChildrenCount(node) > 0:
                self.get_children(node)
            node, cookie = self.GetNextChild(search_node, cookie)
        return self.dummy_list

    def check_can_move(self, source_node, target_node):
        res = True
        childs = self.get_children(source_node)
        if target_node in childs:
            # print('cannot move ' + self.GetItemText(source_node) + ' ' + self.GetItemText(target_node))
            res = False
        self.dummy_list = []
        return res

    def on_begin_drag(self, event):
        if not self.dragging_node:
            self.dragging_node = event.GetItem()
        if self.dragging_node:
            # print("Beginning Drag...")
            # print("dragging" + self.GetItemText(self.dragging_node))
            # print("Beginning Drag...")
            event.Allow()

    def copy_node(self, source_node, target_node):
        expand_collapse = []
        new_node = self.AppendItem(parent=target_node,
                                   text=self.GetItemText(source_node),
                                   data=self.GetItemData(source_node),)
        expand_collapse.append((new_node, self.IsExpanded(source_node)))
        if self.GetChildrenCount(source_node) > 0:
            childs = self.get_children(source_node)
            print('childs are ' + str(childs))
            for child in childs:
                print('child is ' + self.GetItemText(child))
                self.copy_node(child, new_node)
        for node, state in expand_collapse:
            if state:
                self.Expand(node)

    def on_end_drag(self, event):
        self.target_node = event.GetItem()
        if self.check_can_move(self.dragging_node, self.target_node):
            if self.dragging_node:
                if self.target_node:
                    # print("End Drag...")
                    # print(self.GetItemText(self.dragging_node))
                    # print(self.GetItemText(self.target_node))
                    # print("End Drag...")
                    event.Allow()
                    self.copy_node(self.dragging_node, self.target_node)
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
        new_node = self.AppendItem(parent=node, text='New'
                                   + str(self.node_counter),
                                   data=[self.node_counter, ''])
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
        if item.IsOk():
            print(self.GetItemText(item))
            print(item.GetID())
            print(item.__hash__)
            print('done')

    def save_tree(self):
        # pickle.dump(self, open(self.file, "wb"))
        print(self.build_tree())

    def load_tree(self):
        pass


class Sniplet_Control(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.main_sizer)

        self.tool_bar = wx.ToolBar(parent=self)
        self.tool_bar.AddTool(toolId=wx.ID_ADD, label='Add', bitmap=add_ico,
                              bmpDisabled=add_ico, kind=wx.ITEM_NORMAL, shortHelp='Add',
                              longHelp='', clientData=None)
        self.tool_bar.AddTool(toolId=wx.ID_DELETE, label='Del', bitmap=del_ico,
                              bmpDisabled=del_ico, kind=wx.ITEM_NORMAL, shortHelp='Dell',
                              longHelp='', clientData=None)
        self.tool_bar.AddTool(toolId=wx.ID_EDIT, label='Edit', bitmap=edit_ico,
                              bmpDisabled=edit_ico, kind=wx.ITEM_NORMAL, shortHelp='Edit',
                              longHelp='', clientData=None)
        self.tool_bar.AddTool(toolId=wx.ID_SAVE, label='Save', bitmap=save_ico,
                              bmpDisabled=save_ico, kind=wx.ITEM_NORMAL, shortHelp='Save',
                              longHelp='', clientData=None)

        self.sniplets = Sniplet_Tree(parent=self)

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
        # print(self.sniplets.get_current_node())
            