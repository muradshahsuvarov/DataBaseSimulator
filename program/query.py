import relAlg
import buildTree
import remove
import display
from utility import BPlusTree

if __name__ == '__main__':
    root = buildTree.build("Suppliers2", "sid", 1)
    #BPlusTree.display(root)
    #display.displayTree("pg30.txt")
    #remove.removeTree("Suppliers", "sid")
    #remove.removeTable("Suppliers2")
    #display.displayTable("Products", "queryResult.txt")

    # relAlg.select("Products", "color", "==", "pink")
