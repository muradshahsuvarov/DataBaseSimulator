import json
import os


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
