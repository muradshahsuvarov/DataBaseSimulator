import relAlg
import buildTree
import remove
from utility import BPlusTree

if __name__ == '__main__':
    root = buildTree.build("Suppliers", "sid", 1)
    BPlusTree.display(root)

    # relAlg.select("Products", "color", "==", "pink")
