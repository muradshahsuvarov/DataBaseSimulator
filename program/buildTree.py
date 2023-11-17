import json
import os
import math
from utility import load_schema, count_records, BPlusTree


# Assuming utility.py has necessary functions like count_records and load_schema

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
    counter = 0
    for attribute, page_name, index in attribute_list:
        if counter < 4:
            bPlusTree.insert(attribute, page_name, index)
            counter = counter + 1
        else:
            break
    bPlusTree.remove("s02")

    # Write the updated page pool back to the file
    # with open(page_pool_path, 'w') as page_pool_file:
        # json.dump(page_pool, page_pool_file)

    # Save the tree structure to files
    # You would need to iterate over the tree dictionary
    # and save each node to a corresponding .txt file in the index folder.

    # Update directory.txt
    # Add the new B+ tree information to directory.txt

    # Return the B+ tree or the root node reference
    return bPlusTree.root
