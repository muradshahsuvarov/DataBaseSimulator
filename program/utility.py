import json
import os
import re


def initialize_bplus_tree(root_file_name):
    previous_leaf = None  # Variable to keep track of the previous leaf node

    def reconstruct_node(file_name, is_leaf=False):
        nonlocal previous_leaf
        if not file_name:
            return None
        file_path = os.path.join('../index/', file_name)
        with open(file_path, 'r') as file:
            node_data = json.load(file)

        if node_data['type'] == 'L':
            node = LeafNode(node_data['name'], None, node_data['capacity'])
            node.body = node_data['body']
            if previous_leaf:
                previous_leaf.rightNode = node  # Link previous leaf's rightNode to current leaf
                node.leftNode = previous_leaf  # Link current leaf's leftNode to previous leaf
            previous_leaf = node  # Update previous leaf to current node
        else:
            node = InternalNode(node_data['name'], None, node_data['capacity'])
            for entry in node_data['body']:
                left_child = reconstruct_node(entry['left_child'])
                right_child = reconstruct_node(entry['right_child'])
                node_entry = InternalNodeEntry(entry['key'], left_child, right_child)
                node.body.append(node_entry)

        return node

    return reconstruct_node(root_file_name, is_leaf=True)


def traverse_bplus_tree(root, op, val, pages_read):
    relevant_leaves = []
    node = root  # Start from the root of the tree

    # Function to parse the key into a comparable format
    def parse_key(key):
        if isinstance(key, (int, float)):
            return key
        match = re.search(r'\d+', key)
        return int(match.group()) if match else float('inf')

    # Function to compare values based on the operation
    def compare(key_val, op, search_val):
        if op == '=':
            return key_val == search_val
        elif op == '<':
            return key_val < search_val
        elif op == '<=':
            return key_val <= search_val
        elif op == '>':
            return key_val > search_val
        elif op == '>=':
            return key_val >= search_val

    val = parse_key(val)  # Ensure the search value is parsed

    # Traverse the tree to find relevant leaves
    while node:
        pages_read += 1  # Increment page count when a new node is visited
        if node.type == 'L':
            # For leaf nodes, check if records satisfy the condition
            for record in node.body:
                record_val = parse_key(record[0])
                if compare(record_val, op, val):
                    relevant_leaves.append(node)
                    break  # Break after finding the first matching record for '='

            # If searching for equality and the key is not found, traverse left or right nodes
            if op == '=':
                # Traverse left siblings
                left_sibling = node.leftNode
                while left_sibling:
                    pages_read += 1
                    for record in left_sibling.body:
                        record_val = parse_key(record[0])
                        if record_val == val:
                            relevant_leaves.append(left_sibling)
                        elif record_val > val:
                            break  # No more relevant records in this sibling
                    left_sibling = left_sibling.leftNode

                # Traverse right siblings
                right_sibling = node.rightNode
                while right_sibling:
                    pages_read += 1
                    for record in right_sibling.body:
                        record_val = parse_key(record[0])
                        if record_val == val:
                            relevant_leaves.append(right_sibling)
                        elif record_val < val:
                            break  # No more relevant records in this sibling
                    right_sibling = right_sibling.rightNode

                break  # Completed searching through siblings for '=' operation
            elif op == '<' or op == '<=':
                first_key_in_leaf = parse_key(node.body[0][0]) if node.body else None
                if first_key_in_leaf is not None:
                    node = node.leftNode
                    continue
            elif op == '>' or op == '>=':
                first_key_in_leaf = parse_key(node.body[0][0]) if node.body else None
                if first_key_in_leaf is not None:
                    node = node.rightNode
                    continue
            # For range queries, check adjacent nodes
            if op in ['<', '<='] and node.leftNode:
                node = node.leftNode
            elif op in ['>', '>='] and node.rightNode:
                node = node.rightNode
            else:
                break  # No adjacent node to traverse for the current operation
        else:  # Handling for internal nodes
            for i, entry in enumerate(node.body):
                entry_val = parse_key(entry.key)

                if op in ['<', '<=']:
                    if val == entry_val:
                        node = entry.left_child
                        break
                    elif i < len(node.body) - 1:
                        # If val is greater than the key of the next entry, continue moving right
                        if val > parse_key(node.body[i + 1].key):
                            if i + 1 == len(node.body) - 1:
                                # If we are at the last entry, take its right child
                                node = node.body[-1].right_child
                                break # CHECK WITH OTHER RELATIONS, CALL THE SELECT AND CHECK
                            else:
                                # Otherwise, continue with the next entry
                                continue
                        # If val is less than the key of the next entry, take the right child of the current entry
                        elif val < parse_key(node.body[i + 1].key):
                            node = entry.right_child
                            break
                    else:
                        if val > entry_val:
                            node = entry.right_child
                            break
                        elif val < entry_val:
                            node = entry.left_child
                            break
                elif op in ['>', '>='] and val >= entry_val:
                    node = entry.right_child
                    break
                elif op in ['>', '>='] and val < entry_val:
                    node = entry.left_child
                    break
                elif op == '=':
                    if val == entry_val:
                        node = entry.left_child
                        break
                    elif i < len(node.body) - 1:
                        # If val is greater than the key of the next entry, continue moving right
                        if val > parse_key(node.body[i + 1].key):
                            if i + 1 == len(node.body) - 1:
                                # If we are at the last entry, take its right child
                                node = node.body[-1].right_child
                                break # CHECK WITH OTHER RELATIONS, CALL THE SELECT AND CHECK
                            else:
                                # Otherwise, continue with the next entry
                                continue
                        # If val is less than the key of the next entry, take the right child of the current entry
                        elif val < parse_key(node.body[i + 1].key):
                            node = entry.right_child
                            break
                    else:
                        if val > entry_val:
                            node = entry.right_child
                            break
                        elif val < entry_val:
                            node = entry.left_child
                            break
            else:
                if op == '=' and node.body:
                    node = node.body[-1].right_child
                else:
                    break

    return relevant_leaves, pages_read


def read_page_data(rel, page_file):
    file_path = os.path.join(f'../data/{rel}', page_file)
    with open(file_path, 'r') as file:
        return json.load(file)


def satisfies_condition(record_val, op, val):
    if op == '=':
        return record_val == val
    elif op == '<':
        return record_val < val
    elif op == '<=':
        return record_val <= val
    elif op == '>':
        return record_val > val
    elif op == '>=':
        return record_val >= val
    return False


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
        self.leftNode = None
        self.rightNode = None


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
        self.body.sort(key=lambda item: self.parse_key(item.key))

    @staticmethod
    def parse_key(key):
        # If the key is already a numeric type, return as is
        if isinstance(key, (int, float)):
            return key
        # If the key is a string, extract the numeric part
        match = re.search(r'\d+', key)
        return int(match.group()) if match else float('inf')


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

        # Function to extract the numeric part of the key
        def extract_numeric_part(key):
            if isinstance(key, (int, float)):
                return key
            match = re.search(r'\d+', key)
            return int(match.group()) if match else None

        # Extract the numeric part of the attribute
        attr_num = extract_numeric_part(attribute)

        while node.type != 'L':  # Continue until a leaf node is reached
            found = False
            for entry in node.body:
                entry_key_num = extract_numeric_part(entry.key)

                if entry_key_num is not None and attr_num < entry_key_num:
                    node = entry.left_child
                    found = True
                    break
                elif entry_key_num is not None and attr_num >= entry_key_num:
                    continue

            # This is to handle the case where attr_num is greater than all keys in the node
            if not found:
                node = node.body[-1].right_child

        return node

    def insert_into_tree(self, value):
        attribute, page_name, index = value
        leaf_node = self.find_leaf_node(attribute)

        # Function to extract the numeric part for sorting
        def extract_sort_key(item):
            key = item[0]
            if isinstance(key, (int, float)):
                return key
            match = re.search(r'\d+', key)
            return int(match.group()) if match else None

        leaf_node.body.append((attribute, f"{page_name}", index))
        leaf_node.body.sort(key=extract_sort_key)  # Sort using the numeric part of attribute
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

            if node.rightNode is not None:
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

                # Function to extract the numeric part for sorting
                def extract_sort_key(item):
                    key = item.key
                    if isinstance(key, (int, float)):
                        return key
                    match = re.search(r'\d+', key)
                    return int(match.group()) if match else None

                node.parent.body.sort(key=extract_sort_key)  # Sort using the numeric part of the key
                node.parent.current_keys += 1

            if node.parent.current_keys > node.parent.capacity:
                self.split_node(node.parent)

    def insert(self, attribute, page_name, index):
        value = (attribute, page_name, index)
        self.insert_into_tree(value)

    @staticmethod
    def display(root_node):
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

        display_node(root_node)

    def remove(self, attribute):
        # Find the leaf node containing the attribute
        leaf_node = self.find_leaf_node(attribute)

        # Check whether removing the element would cause the underflow
        leaf_node.current_keys -= 1

        # Check if the leaf node is under capacity
        if leaf_node.current_keys < self.order:
            self.handle_underflow(leaf_node)
        else:
            # Remove the attribute from the leaf node
            leaf_node.body = [item for item in leaf_node.body if item[0] != attribute]

    def handle_underflow(self, leaf_node):
        if leaf_node.leftNode and leaf_node.leftNode.current_keys - 1 > self.order:
            self.borrow_from_left(leaf_node)
        elif leaf_node.rightNode and leaf_node.rightNode.current_keys - 1 > self.order:
            self.borrow_from_right(leaf_node)
        else:
            self.merge_leaf(leaf_node)

    def borrow_from_left(self, leaf_node):
        left_sibling = leaf_node.leftNode
        parent = leaf_node.parent

        # Borrow the last entry from the left sibling
        borrowed_entry = left_sibling.body.pop()
        leaf_node.body.insert(0, borrowed_entry)
        leaf_node.current_keys += 1
        left_sibling.current_keys -= 1

        # Update the parent's key
        for entry in parent.body:
            if entry.right_child == leaf_node:
                entry.key = leaf_node.body[0][0]
                break

    def borrow_from_right(self, leaf_node):
        right_sibling = leaf_node.rightNode
        parent = leaf_node.parent

        # Borrow the first entry from the right sibling
        borrowed_entry = right_sibling.body.pop(0)
        leaf_node.body.append(borrowed_entry)
        leaf_node.current_keys += 1
        right_sibling.current_keys -= 1

        # Update the parent's key
        for entry in parent.body:
            if entry.left_child == leaf_node:
                entry.key = right_sibling.body[0][0]
                break

    def merge_leaf(self, leaf_node):
        parent = leaf_node.parent
        left_sibling = leaf_node.leftNode
        right_sibling = leaf_node.rightNode

        # Determine which sibling to merge with
        merge_with = left_sibling if left_sibling else right_sibling
        is_left_merge = left_sibling is not None

        # Merge sibling's entries into leaf_node
        if is_left_merge:
            # Merge all items from the left sibling into leaf_node
            leaf_node.body = merge_with.body + leaf_node.body[1:]
            leaf_node.leftNode = merge_with.leftNode
            if merge_with.leftNode:
                merge_with.leftNode.rightNode = leaf_node
        else:
            # Merge all items from the right sibling into leaf_node
            leaf_node.body = leaf_node.body[:-1] + merge_with.body
            leaf_node.rightNode = merge_with.rightNode
            if merge_with.rightNode:
                merge_with.rightNode.leftNode = leaf_node

        leaf_node.current_keys = len(leaf_node.body)

        # Update the parent's entry to point to leaf_node and remove the redundant entry
        for e in parent.body:
            if is_left_merge and e.right_child == merge_with:
                e.right_child = leaf_node
            elif not is_left_merge and e.left_child == merge_with:
                e.left_child = leaf_node

        parent.body = [e for e in parent.body if e.left_child != merge_with and e.right_child != merge_with]
        parent.current_keys = len(parent.body)

        # Handle potential underflow in the parent
        if parent.current_keys < self.order:
            self.handle_internal_node_underflow(parent)

    def handle_internal_node_underflow(self, node):
        if node == self.root:
            # Handle the special case where the root is the underflow node
            if node.current_keys == 0 and node.body[0].left_child:
                self.root = node.body[0].left_child
                self.root.parent = 'nil'
            return

        parent = node.parent
        left_sibling = self.find_left_sibling(node)
        right_sibling = self.find_right_sibling(node)

        if left_sibling and left_sibling.current_keys - 1 >= self.order:
            self.borrow_from_left_internal(node, left_sibling)
        elif right_sibling and right_sibling.current_keys - 1 >= self.order:
            self.borrow_from_right_internal(node, right_sibling)
        else:
            self.merge_internal(node, left_sibling if left_sibling else right_sibling)

    def find_left_sibling(self, node):
        # Find the left sibling of the node
        parent = node.parent
        for i, entry in enumerate(parent.body):
            if entry.right_child == node and i > 0:
                return parent.body[i - 1].left_child
        return None

    def find_right_sibling(self, node):
        # Find the right sibling of the node
        parent = node.parent
        for i, entry in enumerate(parent.body):
            if entry.left_child == node and i < len(parent.body) - 1:
                return parent.body[i + 1].right_child
        return None

    def borrow_from_left_internal(self, node, left_sibling):
        parent = node.parent

        # Borrow the last entry from left_sibling
        borrowed_entry = left_sibling.body.pop()
        left_sibling.current_keys -= 1

        # Insert the borrowed entry into the start of the node
        # and move the parent's key down
        node.body.insert(0, InternalNodeEntry(parent.body[0].key, borrowed_entry.right_child, node.body[0].left_child))
        parent.body[0].key = borrowed_entry.key
        node.current_keys += 1

        # Update child node's parent pointers
        if borrowed_entry.right_child:
            borrowed_entry.right_child.parent = node

    def borrow_from_right_internal(self, node, right_sibling):
        parent = node.parent

        # Borrow the first entry from right_sibling
        borrowed_entry = right_sibling.body.pop(0)
        right_sibling.current_keys -= 1

        # Insert the borrowed entry into the end of the node
        # and move the parent's key down
        node.body.append(InternalNodeEntry(parent.body[-1].key, node.body[-1].right_child, borrowed_entry.left_child))
        parent.body[-1].key = borrowed_entry.key
        node.current_keys += 1

        # Update child node's parent pointers
        if borrowed_entry.left_child:
            borrowed_entry.left_child.parent = node

    def merge_internal(self, node, sibling):
        if sibling is None:
            # No sibling to merge with, should not typically happen, but handle gracefully
            return

        parent = node.parent
        is_left_merge = sibling.body[0].key < node.body[0].key if sibling.body and node.body else False

        # Merge node with its sibling
        merge_with = sibling if is_left_merge else node
        merge_into = node if is_left_merge else sibling

        # Move the parent's key down and merge entries
        parent_key_index = parent.body.index(
            next(e for e in parent.body if e.left_child == merge_with or e.right_child == merge_with))
        parent_key = parent.body[parent_key_index].key
        if is_left_merge:
            merge_into.body.append(
                InternalNodeEntry(parent_key, merge_with.body[-1].right_child, merge_into.body[0].left_child))
            merge_into.body = merge_with.body + merge_into.body
        else:
            merge_into.body.insert(0, InternalNodeEntry(parent_key, merge_into.body[-1].right_child,
                                                        merge_with.body[0].left_child))
            merge_into.body += merge_with.body

        # Update current keys count
        merge_into.current_keys = len(merge_into.body)

        # Remove the merge_with node and the corresponding key from the parent
        parent.body.pop(parent_key_index)
        parent.current_keys -= 1

        # Update child node's parent pointers
        for entry in merge_with.body:
            if entry.left_child:
                entry.left_child.parent = merge_into
            if entry.right_child:
                entry.right_child.parent = merge_into

        # Handle potential underflow in the parent
        if parent.current_keys < self.order:
            self.handle_internal_node_underflow(parent)

    @staticmethod
    def save(node, folder_path='../index/'):
        if node is None:
            return

        # Serialize node data
        node_data = {
            'name': node.name,
            'type': node.type,
            'capacity': node.capacity,
            'current_keys': node.current_keys,
            'parent': node.parent.name if node.parent and hasattr(node.parent, 'name') else None
        }

        if node.type == 'L':
            node_data['leftNode'] = node.leftNode.name if node.leftNode else None
            node_data['rightNode'] = node.rightNode.name if node.rightNode else None
            node_data['body'] = node.body
        else:
            # For InternalNode, serialize each entry in the body
            node_data['body'] = []
            for entry in node.body:
                entry_data = {
                    'key': entry.key,
                    'left_child': entry.left_child.name if entry.left_child else None,
                    'right_child': entry.right_child.name if entry.right_child else None
                }
                node_data['body'].append(entry_data)

        # Save node data to file
        file_path = os.path.join(folder_path, f"{node.name}")
        with open(file_path, 'w') as file:
            json.dump(node_data, file, indent=4)

        # Recursively save child nodes (for internal nodes)
        if node.type == 'I':
            for entry in node.body:
                BPlusTree.save(entry.left_child, folder_path)
                BPlusTree.save(entry.right_child, folder_path)
