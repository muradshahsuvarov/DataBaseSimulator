import relAlg
import buildTree
import remove
import display
from utility import BPlusTree

if __name__ == '__main__':
    #root = buildTree.build("Supply", "cost", 1)
    #BPlusTree.display(root)
    #display.displayTree("pg933.txt")
    #remove.removeTree("Suppliers", "sid")
    #remove.removeTable("Suppliers2")
    #display.displayTable("Products", "queryResult.txt")
    relAlg.select("Supply", "cost", ">=", 34.02)
