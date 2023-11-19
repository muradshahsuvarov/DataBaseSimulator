import json
import os
import utility
import uuid

def select(rel, att, op, val):
    result = []  # To store the tuples that satisfy the condition
    pages_read = 0  # Count the number of pages read
    pages_path = f'../data/{rel}'  # Directory structure from the project description
    page_link_path = os.path.join(pages_path, 'pageLink.txt')
    schema_dict = utility.load_schema(rel)  # Load the schema for the relation

    # Check if the attribute is in the schema
    if att not in schema_dict:
        raise ValueError(f"Attribute {att} not found in schema for relation {rel}")

    # Get the index of the attribute in the record based on the schema
    att_index = schema_dict[att]

    # Check for B+_tree existence
    bplus_tree_root = utility.check_bplus_tree_exists(rel, att)
    if bplus_tree_root:
        # Initialize and build the B+ Tree
        bplus_tree = utility.initialize_bplus_tree(bplus_tree_root)
        # Traverse the B+ Tree and find relevant leaf nodes
        leaf_nodes, pages_read = utility.traverse_bplus_tree(bplus_tree, op, val, pages_read)

        # Fetch records from data pages referenced in the leaf nodes
        for leaf in leaf_nodes:
            if leaf is not None:
                for entry in leaf.body:
                    page_data = utility.read_page_data(rel,
                                                       entry[1])  # Assuming entry format: (attribute, page_name, index)
                    record = page_data[entry[2]]
                    if utility.satisfies_condition(record[att_index], op, val):
                        result.append(record)

        print(f"With B+ Tree, the cost of searching {att} {op} {val} on {rel} is {pages_read} pages")
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

    # Generate a new relation name
    new_rel_name = f"{rel}_selected_on_{att}_{op}_{val}"
    new_rel_path = f'../data/{new_rel_name}'

    # Create a new directory for this relation
    os.makedirs(new_rel_path, exist_ok=True)

    # Create a page pool for the new relation
    with open(f'../data/pagePool.txt', 'r') as page_pool_file:
        page_pool = json.load(page_pool_file)

    # Create pageLink.txt for the new relation
    page_link = []
    page_count = 0

    # Split the result into pages and write each page
    page_size = 2
    for i in range(0, len(result), page_size):
        page = result[i:i + page_size]
        page_name = page_pool.pop(0)  # or however you want to name your pages
        page_link.append(page_name)
        page_count += 1

        with open(os.path.join(new_rel_path, page_name), 'w') as page_file:
            json.dump(page, page_file)

    # Write the page link information
    with open(os.path.join(new_rel_path, 'pageLink.txt'), 'w') as link_file:
        json.dump(page_link, link_file)

    # Update the page pool
    with open(f'../data/pagePool.txt', 'w') as page_pool_file:
        json.dump(page_pool, page_pool_file)

    # Read the current schemas from schemas.txt
    with open('../data/schemas.txt', 'r') as schema_file:
        schemas = json.load(schema_file)

    # Append new schema info for the selected relation
    for attribute in schema_dict:
        schemas.append([new_rel_name, attribute, 'str', schema_dict[attribute]])

    # Write the updated schemas back to schemas.txt
    with open('../data/schemas.txt', 'w') as schema_file:
        json.dump(schemas, schema_file)

    print(f"Select operation completed. Pages written: {page_count}")
    return new_rel_name


def project(rel, attList):
    projected_data = []  # To store the projected records
    pages_path = f'../data/{rel}'  # Directory structure from the project description
    page_link_path = os.path.join(pages_path, 'pageLink.txt')
    schema_dict = utility.load_schema(rel)  # Load the schema for the relation

    # Check if all attributes in attList are in the schema
    for att in attList:
        if att not in schema_dict:
            raise ValueError(f"Attribute {att} not found in schema for relation {rel}")

    # Get the indexes of the attributes in the record based on the schema
    att_indexes = [schema_dict[att] for att in attList]

    # Read the order of the pages from pageLink.txt
    with open(page_link_path, 'r') as link_file:
        page_order = json.load(link_file)

    # Load each page in the specified order and apply the projection
    for page_file in page_order:
        with open(os.path.join(pages_path, page_file), 'r') as file:
            page_data = json.load(file)
            for record in page_data:
                projected_record = [record[i] for i in att_indexes]
                projected_data.append(projected_record)

    # Generate a new relation name
    new_rel_name = f"{rel}_projected_on_{'_'.join(attList)}"
    new_rel_path = f'../data/{new_rel_name}'

    # Create a new directory for this relation
    os.makedirs(new_rel_path, exist_ok=True)

    # Read page pool for the new relation
    with open(f'../data/pagePool.txt', 'r') as page_pool_file:
        page_pool = json.load(page_pool_file)

    # Create pageLink.txt for the new relation
    page_link = []
    page_count = 0
    page_size = 2  # Define the number of records per page

    # Split the projected data into pages and write each page
    for i in range(0, len(projected_data), page_size):
        page = projected_data[i:i + page_size]
        page_name = page_pool.pop(0)
        page_link.append(page_name)
        page_count += 1

        with open(os.path.join(new_rel_path, page_name), 'w') as page_file:
            json.dump(page, page_file)

    # Write the page link information
    with open(os.path.join(new_rel_path, 'pageLink.txt'), 'w') as link_file:
        json.dump(page_link, link_file)

    # Update the page pool
    with open(f'../data/pagePool.txt', 'w') as page_pool_file:
        json.dump(page_pool, page_pool_file)

    # Update schemas.txt with the new relation schema
    with open('../data/schemas.txt', 'r') as schema_file:
        schemas = json.load(schema_file)

    # Append new schema info for the projected relation
    for i, att in enumerate(attList):
        schemas.append([new_rel_name, att, 'str', i])  # Assuming all attributes are of type string

    with open('../data/schemas.txt', 'w') as schema_file:
        json.dump(schemas, schema_file)

    # Save the result to queryOutput/queryResult.txt
    with open('../queryOutput/queryResult.txt', 'w') as result_file:
        json.dump(projected_data, result_file)

    print(f"Projection operation completed. Pages written: {page_count}")
    return new_rel_name




def join(rel1, att1, rel2, att2):
    # Load schemas for both relations
    schema1 = utility.load_schema(rel1)
    schema2 = utility.load_schema(rel2)

    # Prepare paths for data directories
    pages_path1 = os.path.join('../data', rel1)
    pages_path2 = os.path.join('../data', rel2)

    # Read page orders
    page_link_path1 = os.path.join(pages_path1, 'pageLink.txt')
    page_link_path2 = os.path.join(pages_path2, 'pageLink.txt')

    with open(page_link_path1, 'r') as file:
        page_order1 = json.load(file)
    with open(page_link_path2, 'r') as file:
        page_order2 = json.load(file)

    bplus_tree_root = utility.check_bplus_tree_exists(rel2, att2)

    # Initialize result set
    join_result = []

    if bplus_tree_root:
        print(f"B+ exists for {rel2}, {att2}. The root is {bplus_tree_root}\n")

    # Nested loop join
    for page1 in page_order1:
        page_data1 = utility.read_page_data(rel1, page1)
        for record1 in page_data1:
            if bplus_tree_root:
                # Get the root of the B+ tree
                bplus_tree = utility.initialize_bplus_tree(bplus_tree_root)

                # Search for the matching leaves in the B+ tree
                matching_leaves, _ = utility.traverse_bplus_tree(bplus_tree, '=', record1[schema1[att1]], 0)

                for leaf in matching_leaves:
                    for attribute, page_name, index in leaf.body:
                        if attribute == record1[schema1[att1]]:
                            # Read the page data for the matching record
                            page_data2 = utility.read_page_data(rel2, page_name)
                            # Extract the specific record using the index, if available
                            if 0 <= index < len(page_data2):
                                record2 = page_data2[index]
                                # Check if the join condition is satisfied
                                if record2[schema2[att2]] == record1[schema1[att1]]:
                                    # Combine records while avoiding attribute duplication
                                    combined_record = record1 + [record2[i] for i in range(len(record2)) if i != schema2[att2]]
                                    join_result.append(combined_record)
            else:
                # Fallback to nested loop join if no B+ tree is found
                for page2 in page_order2:
                    page_data2 = utility.read_page_data(rel2, page2)
                    for record2 in page_data2:
                        if record1[schema1[att1]] == record2[schema2[att2]]:
                            # Combine records, exclude duplicate join attribute from record2
                            combined_record = record1 + [record2[i] for i in range(len(record2)) if i != schema2[att2]]
                            join_result.append(combined_record)

    # Generate a new relation name for join result
    new_rel_name = f"{rel1}_{rel2}_joined"
    new_rel_path = f'../data/{new_rel_name}'

    # Create a new directory for this relation
    os.makedirs(new_rel_path, exist_ok=True)

    # Create a page pool for the new relation
    with open(f'../data/pagePool.txt', 'r') as page_pool_file:
        page_pool = json.load(page_pool_file)

    # Create pageLink.txt for the new relation
    page_link = []
    page_count = 0
    page_size = 2  # Define the number of records per page

    # Split the join result into pages and write each page
    for i in range(0, len(join_result), page_size):
        page = join_result[i:i + page_size]
        page_name = page_pool.pop(0)
        page_link.append(page_name)
        page_count += 1

        with open(os.path.join(new_rel_path, page_name), 'w') as page_file:
            json.dump(page, page_file)

    # Write the page link information
    with open(os.path.join(new_rel_path, 'pageLink.txt'), 'w') as link_file:
        json.dump(page_link, link_file)

    # Update the page pool
    with open(f'../data/pagePool.txt', 'w') as page_pool_file:
        json.dump(page_pool, page_pool_file)

    # Update schemas.txt with the new relation schema
    with open('../data/schemas.txt', 'r') as schema_file:
        schemas = json.load(schema_file)

    # Append new schema info for the joined relation
    for i, attribute in enumerate(list(schema1.keys()) + list(schema2.keys())):
        schemas.append([new_rel_name, attribute, 'str', i])  # Assuming all attributes are of type string


    with open('../data/schemas.txt', 'w') as schema_file:
        json.dump(schemas, schema_file)

    # Save the result to queryOutput/queryResult.txt
    with open('../queryOutput/queryResult.txt', 'w') as result_file:
        json.dump(join_result, result_file)

    print(f"Join operation completed. Pages written: {page_count}")
    return new_rel_name
