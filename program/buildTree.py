import json
import os
import math
from utility import load_schema, count_records, BPlusTree


def build(rel, att, od):
    # Load the schema to find the index of the attribute
    schema_dict = load_schema(rel)
    if att not in schema_dict:
        raise ValueError(f"Attribute {att} not found in schema for relation {rel}")
    att_index = schema_dict[att]

    # Step 1: Get total number of all records from relation named rel
    total_records = count_records(rel)

    # Step 2: Retrieve the list of attributes and page names
    attribute_list = []
    pages_path = f'../data/{rel}'
    page_link_path = os.path.join(pages_path, 'pageLink.txt')

    with open(page_link_path, 'r') as link_file:
        page_order = json.load(link_file)

    for page_file in page_order:
        with open(os.path.join(pages_path, page_file), 'r') as file:
            page_data = json.load(file)
            for index, record in enumerate(page_data):
                attribute_list.append((record[att_index], page_file, index))

    # Step 3: Parse the list of available page names from the page pool
    page_pool_path = '../index/pagePool.txt'
    with open(page_pool_path, 'r') as page_pool_file:
        page_pool = json.load(page_pool_file)

        # Check if there are enough pages in the page pool
        if len(page_pool) == 0:
            return "Can't create a B+ Tree because the page pool is empty"
        elif total_records / (2 * od) > len(page_pool):
            return "Not enough available pages to create a B+ tree for {rel} relation"

    # Initialize the B+ tree structure
    bPlusTree = BPlusTree(od, page_pool)

    # Insert attributes into the B+ tree
    for attribute, page_name, index in attribute_list:
        bPlusTree.insert(attribute, page_name, index)

    # Save the B+ tree root information in the directory
    directory_path = '../index/directory.txt'
    new_entry = (rel, att, bPlusTree.root.name)

    # Read the existing directory entries
    with open(directory_path, 'r') as directory_file:
        try:
            directory_entries = json.load(directory_file)
        except json.JSONDecodeError:  # In case the file is empty or invalid JSON
            directory_entries = []

    # Append the new entry
    directory_entries.append(new_entry)

    # Write the updated list of entries back to the file in JSON format
    with open(directory_path, 'w') as directory_file:
        json.dump(directory_entries, directory_file, indent=4)

    # Save the updated page pool back to the file in JSON format
    page_pool_path = '../index/pagePool.txt'
    with open(page_pool_path, 'w') as page_pool_file:
        json.dump(page_pool, page_pool_file, indent=4)

    # Save the tree structure to files
    BPlusTree.save(bPlusTree.root)

    # Serialize the entire B+ tree
    def serialize_tree(node):
        if node is None:
            return None

        tree_data = {
            'name': node.name,
            'type': node.type,
            'capacity': node.capacity,
            'current_keys': node.current_keys,
            'parent': node.parent.name if node.parent and hasattr(node.parent, 'name') else None
        }

        if node.type == 'L':
            tree_data.update({
                'leftNode': node.leftNode.name if node.leftNode else None,
                'rightNode': node.rightNode.name if node.rightNode else None,
                'body': node.body
            })
        else:
            tree_data['body'] = [serialize_tree(entry.left_child) for entry in node.body] + \
                                [serialize_tree(entry.right_child) for entry in node.body]

        return tree_data

    # Ensure the directory exists
    os.makedirs('../generatedTrees/', exist_ok=True)

    # Save the serialized tree to a file
    tree_file_path = f'../generatedTrees/{rel}.{att}.txt'
    with open(tree_file_path, 'w') as tree_file:
        json.dump(serialize_tree(bPlusTree.root), tree_file, indent=4)

    # Return the B+ tree or the root node reference
    return bPlusTree.root
