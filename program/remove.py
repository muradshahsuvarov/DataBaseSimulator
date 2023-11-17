import json
import os


import os

def removeTree(rel, att):
    # Step 1: Read directory data and find root page
    directory_path = '../index/directory.txt'
    with open(directory_path, 'r') as file:
        directory_entries = json.load(file)

    root_page_name = None
    for entry in directory_entries:
        if entry[0] == rel and entry[1] == att:
            root_page_name = entry[2]
            break

    if not root_page_name:
        return "B+ Tree does not exist for the specified relation and attribute."

    # Step 2: Remove the tree entry from the directory
    new_directory_entries = [entry for entry in directory_entries if entry[2] != root_page_name]
    with open(directory_path, 'w') as file:
        json.dump(new_directory_entries, file, indent=4)

    # Step 3: Traverse the tree and collect node names
    def traverse_and_collect(node_name, collected_nodes=[]):
        file_path = os.path.join('../index/', node_name)
        with open(file_path, 'r') as file:
            node_data = json.load(file)

        collected_nodes.append(node_data['name'])

        if node_data['type'] == 'I':
            for entry in node_data['body']:
                if entry['left_child']:
                    traverse_and_collect(entry['left_child'], collected_nodes)
                if entry['right_child']:
                    traverse_and_collect(entry['right_child'], collected_nodes)

    nodes_to_remove = []
    traverse_and_collect(root_page_name, nodes_to_remove)

    # Step 4: Remove page files from the index directory
    for node_name in nodes_to_remove:
        file_path = os.path.join('../index/', f"{node_name}")
        if os.path.exists(file_path):
            os.remove(file_path)

    # Step 5: Update page pool
    page_pool_path = '../index/pagePool.txt'
    with open(page_pool_path, 'r') as file:
        page_pool = json.load(file)

    page_pool.extend(nodes_to_remove)

    with open(page_pool_path, 'w') as file:
        json.dump(page_pool, file, indent=4)

    return "B+ Tree removed successfully."


    with open(page_pool_path, 'w') as file:
        json.dump(page_pool, file, indent=4)

    return "B+ Tree removed successfully."



def removeTable(rel):
    return None
