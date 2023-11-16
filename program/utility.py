import json
import os
import re
import sys


def count_records(rel):
    record_count = 0  # To store the total number of records
    pages_path = f'../data/{rel}'  # Assuming the directory structure from the project description
    page_link_path = os.path.join(pages_path, 'pageLink.txt')

    # Read the order of the pages from pageLink.txt
    with open(page_link_path, 'r') as link_file:
        page_order = json.load(link_file)

    # Load each page in the specified order and count the records
    for page_file in page_order:
        with open(os.path.join(pages_path, page_file), 'r') as file:
            page_data = json.load(file)
            # Each sublist in page_data is a record, count them all
            record_count += len(page_data)

    return record_count


def load_schema(rel):
    # Load the schema from the root data directory
    schema_path = '../data/schemas.txt'
    with open(schema_path, 'r') as schema_file:
        schema = json.load(schema_file)
    # Create a dictionary to map attribute names to their positions
    schema_dict = {attr[1]: attr[3] for attr in schema if attr[0] == rel}
    return schema_dict


def check_bplus_tree_exists(rel, att):
    directory_path = '../index/directory.txt'
    with open(directory_path, 'r') as directory_file:
        directory = json.load(directory_file)
    # Search for a B+ tree for the given relation and attribute
    for entry in directory:
        if entry[0] == rel and entry[1] == att:
            return entry[2]  # Return the root if a B+ tree exists
    return None


class Node:
    def __init__(self, name, node_type, parent, capacity):
        self.name = name
        self.type = node_type
        self.parent = parent
        self.capacity = capacity
        self.current_keys = 0
        self.body = []


class LeafNode(Node):
    def __init__(self, name, parent, capacity):
        super().__init__(name, 'L', parent, capacity)
        self.leftNode = 'nil'
        self.rightNode = 'nil'


class InternalNodeEntry:
    def __init__(self, key, left_child, right_child):
        self.key = key
        self.left_child = left_child
        self.right_child = right_child


class InternalNode(Node):
    def __init__(self, name, parent, capacity):
        super().__init__(name, 'I', parent, capacity)

    def add_entry(self, key, left_child, right_child):
        entry = InternalNodeEntry(key, left_child, right_child)
        self.body.append(entry)
        self.body.sort(key=lambda item: int(re.search(r'\d+', entry.key).group()))


class BPlusTree:
    def __init__(self, order, page_pool):
        self.order = order
        self.page_pool = page_pool

        # Check if there are available pages for the root
        if not self.page_pool:
            raise ValueError("Page pool is empty, cannot initialize B+ Tree")

        # Create the root node as a leaf
        root_page_name = self.page_pool.pop()
        self.root = LeafNode(root_page_name, 'nil', order * 2)

    def find_leaf_node(self, attribute):
        node = self.root

        attr_num = int(re.search(r'\d+', attribute).group())  # Extract the numeric part of the attribute

        while node.type != 'L':  # Continue until a leaf node is reached
            found = False
            for entry in node.body:
                entry_key_num = int(re.search(r'\d+', entry.key).group())  # Numeric part of the entry's key

                if attr_num < entry_key_num:
                    node = entry.left_child
                    found = True
                    break
                elif attr_num >= entry_key_num:
                    continue

            # This is to handle the case where attr_num is greater than all keys in the node
            if not found:
                node = node.body[-1].right_child

        return node

    def insert_into_tree(self, value):
        attribute, page_name, index = value
        leaf_node = self.find_leaf_node(attribute)
        leaf_node.body.append((attribute, f"{page_name}", index))
        leaf_node.body.sort(key=lambda x: int(re.search(r'\d+', x[0]).group()))  # Sort by numeric part of attribute
        leaf_node.current_keys += 1
        if leaf_node.current_keys > leaf_node.capacity:
            self.split_node(leaf_node)

    def split_node(self, node):
        mid_index = len(node.body) // 2
        mid_value = node.body[mid_index][0] if node.type == 'L' else node.body[mid_index].key

        new_node_name = self.page_pool.pop()
        if node.type == 'L':
            new_node = LeafNode(new_node_name, node.parent, self.order * 2)
            new_node.body = node.body[mid_index:]
            new_node.current_keys = len(new_node.body)
            node.body = node.body[:mid_index]
            node.current_keys = len(node.body)

            if node.rightNode != 'nil':
                node.rightNode.leftNode = new_node
            new_node.rightNode = node.rightNode
            new_node.leftNode = node
            node.rightNode = new_node
        else:
            new_node = InternalNode(new_node_name, node.parent, self.order * 2)
            new_node.body = node.body[mid_index + 1:]
            new_node.current_keys = len(new_node.body)

            for entry in new_node.body:
                if entry.left_child != 'nil':
                    entry.left_child.parent = new_node
                if entry.right_child != 'nil':
                    entry.right_child.parent = new_node

            node.body = node.body[:mid_index]
            node.current_keys = len(node.body)

        if node.parent == 'nil':
            new_root = InternalNode(self.page_pool.pop(), 'nil', self.order * 2)
            new_root.body = [InternalNodeEntry(mid_value, node, new_node)]
            new_root.current_keys = 1
            self.root = new_root
            node.parent = new_root
            new_node.parent = new_root
        else:
            # Check if the mid_value already exists in the parent node
            parent_update_required = True
            for entry in node.parent.body:
                if entry.key == mid_value:
                    entry.right_child = new_node
                    parent_update_required = False
                    break

            if parent_update_required:
                new_entry = InternalNodeEntry(mid_value, node, new_node)
                node.parent.body.append(new_entry)
                node.parent.body.sort(key=lambda item: int(re.search(r'\d+', item.key).group()))
                node.parent.current_keys += 1

            if node.parent.current_keys > node.parent.capacity:
                self.split_node(node.parent)

    def insert(self, attribute, page_name, index):
        # Public method to insert a new value into the tree
        value = (attribute, page_name, index)
        self.insert_into_tree(value)

    def display(self):
        def display_node(node, indent=0):
            if node is None:
                return

            if node.type == 'I':
                node_info = f"{' ' * indent}Node {node.name}: ["
                entries_info = ', '.join([
                    f"({e.left_child.name if e.left_child else 'nil'}, {e.key}, {e.right_child.name if e.right_child else 'nil'})"
                    for e in node.body])
                node_info += entries_info + "]"
                print(node_info)

                for entry in node.body:
                    display_node(entry.left_child, indent + 4)
                    display_node(entry.right_child, indent + 4)
            elif node.type == 'L':
                leaf_info = f"{' ' * indent}Leaf {node.name}: ["
                entries_info = ', '.join([str(item) for item in node.body])
                leaf_info += entries_info + "]"
                print(leaf_info)

        display_node(self.root)
