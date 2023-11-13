import json
import os


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


def select(rel, att, op, val):
    result = []  # To store the tuples that satisfy the condition
    pages_read = 0  # Count the number of pages read
    pages_path = f'../data/{rel}'  # Assuming the directory structure from the project description
    page_link_path = os.path.join(pages_path, 'pageLink.txt')
    schema_dict = load_schema(rel)  # Load the schema for the relation

    # Check if the attribute is in the schema
    if att not in schema_dict:
        raise ValueError(f"Attribute {att} not found in schema for relation {rel}")

    # Get the index of the attribute in the record based on the schema
    att_index = schema_dict[att]

    # Check for B+_tree existence
    bplus_tree_root = check_bplus_tree_exists(rel, att)
    if bplus_tree_root:
        # TODO: Implement search using B+_tree
        print(f"With B+_tree, the cost of searching {att} {op} {val} on {rel} is {pages_read} pages")
    else:
        # Read the order of the pages from pageLink.txt
        with open(page_link_path, 'r') as link_file:
            page_order = json.load(link_file)

        # Load each page in the specified order and apply the select condition
        for page_file in page_order:
            with open(os.path.join(pages_path, page_file), 'r') as file:
                page_data = json.load(file)
                pages_read += 1  # Increment page read count
                for record in page_data:
                    # Access the attribute by index as per the schema
                    attribute_value = record[att_index]
                    # Perform the comparison based on the attribute type
                    if type(attribute_value) is int:
                        condition = eval(f"{attribute_value} {op} {val}")
                    else:
                        condition = eval(f"'{attribute_value}' {op} '{val}'")
                    if condition:
                        result.append(record)

        print(f"Without B+_tree, the cost of searching {att} {op} {val} on {rel} is {pages_read} pages")

    # Save the result to a file and return its name
    result_file_path = '../queryOutput/queryResult.txt'
    with open(result_file_path, 'w') as file:
        json.dump(result, file)

    result_relation_name = f"{rel}_selected_on_{att}_{op}_{val}"
    return result_relation_name


def project(rel, attList):
    return 0


def join(rel1, att1, rel2, att2):
    return 0
