import json
from json import JSONEncoder


class NodeEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


class Node:
    name = None
    id = None
    parent_id = None
    data = None
    is_expanded = None
    children = None

    def __init__(self, name=None, data=None, idx=None, parent_id=None,
                 is_expanded=False):
        self.id = idx
        self.parent_id = parent_id
        self.name = name
        self.data = data
        self.children = {}
        self.is_expanded = is_expanded


class Tree:
    def __init__(self):
        self.root = Node(name='Root', idx=0, is_expanded=True)
        self.max_id = 0
        self.map = {0: self.root}

    def add_node(self, node, parent_id):
        parent = self.get_node(parent_id)
        self.max_id += 1
        node.id = self.max_id
        node.parent_id = parent_id
        parent.children[node.id] = node
        self.map[node.id] = node

    def del_node(self, idx):
        node = self.map.pop(idx)
        pnode = self.map[node.parent_id]
        pnode.children.pop(node.id)

    def get_node(self, idx):
        return self.map.get(idx, None)

    def move_node(self, src_idx, tgt_idx):
        if src_idx == 0 or src_idx == tgt_idx:
            return
        status = self.is_parent_of(src_idx, tgt_idx)
        if not status:
            parent_old = self.get_node(src_idx).parent_id
            node_to_move = self.get_node(parent_old).children.pop(src_idx)
            parent_new = self.get_node(tgt_idx)
            parent_new.children[node_to_move.id] = node_to_move
            node_to_move.parent_id = tgt_idx
        else:
            print('cannot move')

    def to_json(self):
        return json.dumps(self.root, indent=2, cls=NodeEncoder)

    def save(self, filename):
        with open(filename, 'w') as f:
            f.write(self.to_json())

    def load(self, filename):
        root = self.map.pop(0)
        del root
        self.max_id = 0
        self.map = {}
        with open(filename, 'r') as f:
            json_tree = json.loads(f.read())
        self.loads(json_tree)

    def loads(self, js):
        n = Node(name=js['name'],
                 idx=js['id'],
                 parent_id=js['parent_id'],
                 data=js['data'],
                 is_expanded=js['is_expanded']
                 )
        if js['id'] == 0:
            self.root = n
            self.map[js['id']] = n
            self.max_id = 0
        else:
            self.map[js['id']] = n
            pn = self.get_node(js['parent_id'])
            pn.children[js['id']] = n
            self.max_id = max(self.max_id + 1, js['id'])
        if len(js['children']) > 0:
            for k, v in js['children'].items():
                self.loads(v)

    def is_parent_of(self, src_idx, tgt_idx):
        if src_idx == tgt_idx:
            return False
        return self._is_parent_traverse(src_idx, tgt_idx)

    def _is_parent_traverse(self, src_idx, tgt_idx, res=False):
        if res:
            return res
        nod = self.map.get(src_idx)
        if nod:
            if len(nod.children) > 0:
                for k, n in nod.children.items():
                    if n.id == tgt_idx:
                        return True
                    if len(n.children) > 0:
                        return self._is_parent_traverse(n.id, tgt_idx, res)
            else:
                return False

        else:
            return False
