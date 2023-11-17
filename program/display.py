import json
import os


def displayTree(fname):
    # Step 1: Read directory data
    directory_path = '../index/directory.txt'
    with open(directory_path, 'r') as file:
        directory_entries = json.load(file)

    relation_name, search_key = None, None
    for entry in directory_entries:
        if entry[2] == fname:
            relation_name, search_key = entry[0], entry[1]
            break

    if not relation_name or not search_key:
        return "Tree not found in directory."

    # Step 2: Deserialize and traverse the tree
    def traverse_and_display(node_name, indent=0, result=[]):
        # Deserialize node data from file
        file_path = os.path.join('../index/', f"{node_name}")
        with open(file_path, 'r') as file:
            node_data = json.load(file)

        # Display node
        if node_data['type'] == 'I':
            node_info = f"{' ' * indent}Node {node_data['name']}: ["
            entries_info = ', '.join([
                f"({e['left_child'] if e['left_child'] else 'nil'}, {e['key']}, {e['right_child'] if e['right_child'] else 'nil'})"
                for e in node_data['body']])
            node_info += entries_info + "]"
            result.append(node_info)

            # Recursively display child nodes
            for entry in node_data['body']:
                traverse_and_display(entry['left_child'], indent + 4, result)
                traverse_and_display(entry['right_child'], indent + 4, result)
        elif node_data['type'] == 'L':
            leaf_info = f"{' ' * indent}Leaf {node_data['name']}: [{', '.join(map(str, node_data['body']))}]"
            result.append(leaf_info)

    tree_representation = []
    traverse_and_display(fname, 0, tree_representation)

    # Step 3: Write hierarchical representation
    output_file_path = f"../treePic/{relation_name}_{search_key}.txt"
    with open(output_file_path, 'w') as file:
        file.write('\n'.join(tree_representation))

    return output_file_path


def displayTable(rel, fname):
    pages_path = f'../data/{rel}'  # Directory path for the relation
    page_link_path = os.path.join(pages_path, 'pageLink.txt')

    all_records = []  # Store all records from the relation

    # Read the order of the pages from pageLink.txt
    with open(page_link_path, 'r') as link_file:
        page_order = json.load(link_file)

    # Load each page and aggregate records
    for page_file in page_order:
        with open(os.path.join(pages_path, page_file), 'r') as file:
            page_data = json.load(file)
            all_records.extend(page_data)

    # Save the aggregated data to the specified file
    output_file_path = f'../queryOutput/{fname}'
    with open(output_file_path, 'w') as file:
        json.dump(all_records, file, indent=4)

    return f"Table {rel} displayed in file {output_file_path}"

