import json
import os


def removeTree(rel, att):
    tree_file_path = f'../generatedTrees/{rel}.{att}.txt'
    directory_path = '../index/directory.txt'
    page_pool_path = '../index/pagePool.txt'

    # Check if the tree file exists
    if not os.path.exists(tree_file_path):
        return "B+ tree does not exist."

    # Deserialize the tree and collect page names
    with open(tree_file_path, 'r') as tree_file:
        tree_data = json.load(tree_file)

    def collect_pages(node_data):
        if node_data is None:
            return []
        pages = [node_data['name']]
        if node_data['type'] == 'I':
            for child in node_data['body']:
                pages += collect_pages(child)
        return pages

    pages_to_return = collect_pages(tree_data)

    # Remove tree file
    os.remove(tree_file_path)

    # Update directory
    with open(directory_path, 'r') as directory_file:
        directory_entries = json.load(directory_file)
    directory_entries = [entry for entry in directory_entries if not (entry[0] == rel and entry[1] == att)]
    with open(directory_path, 'w') as directory_file:
        json.dump(directory_entries, directory_file, indent=4)

    # Update page pool
    with open(page_pool_path, 'r') as page_pool_file:
        page_pool = json.load(page_pool_file)
    page_pool.extend(pages_to_return)
    with open(page_pool_path, 'w') as page_pool_file:
        json.dump(page_pool, page_pool_file, indent=4)

    return "B+ tree removed successfully."


def removeTable(rel):
    return None
