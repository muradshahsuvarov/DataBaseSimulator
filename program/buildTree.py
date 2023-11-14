import math
import utility
import json


def build(rel, att, od):

    # Step 1: Get total number of all records from relation named rel
    total_records = utility.count_records(rel)

    # Step 2: Calculate the height and the fanout of the tree
    # The fanout is 2 * od + 1 in our case
    fanout = (2 * od + 1)
    height = math.ceil(math.log((total_records / fanout - 1), (fanout + 1)))

    # Step 3: Start building a balanced B+ tree
    # Check if the attribute is in the schema
    schema_dict = utility.load_schema(rel)
    if att not in schema_dict:
        raise ValueError(f"Attribute {att} not found in schema for relation {rel}")

    # Initialize the root of the B+ tree
    root = {
        'page_name': '',
        'type': 'I',
        'parent': 'nil',
        'children': []
    }

    # Path to the page pool
    page_pool_path = '../index/pagePool.txt'

    # Read the available pages from the page pool
    with open(page_pool_path, 'r') as page_pool_file:
        page_pool = json.load(page_pool_file)

    # Take a page from the end of the page pool to use as the root
    if page_pool:
        root['page_name'] = page_pool.pop()  # Get the last page in the pool
    else:
        raise Exception("No pages available in the page pool.")

    # Write the updated page pool back to the file
    with open(page_pool_path, 'w') as page_pool_file:
        json.dump(page_pool, page_pool_file)

    # TODO: Build the B+ tree by inserting records into the tree
    # This will involve creating pages for leaf nodes and internal nodes,
    # distributing keys and pointers according to B+ tree properties,
    # and handling splits and merges as you insert records.

    # Save the structure of the newly created B+ tree
    # TODO: Save the root and all other pages to files in the index folder
    # TODO: Update the directory.txt with the new B+ tree's root page information

    # Return a reference to the root page of the constructed B+ tree
    return height


def removeTable(rel):
    return None
