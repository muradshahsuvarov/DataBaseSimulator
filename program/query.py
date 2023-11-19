import relAlg
import buildTree
import remove
import display
from utility import BPlusTree

if __name__ == '__main__':
    #root = buildTree.build("Supply", "sid", 1)
    #BPlusTree.display(root)
    #display.displayTree("pg928.txt")
    #remove.removeTree("Suppliers", "sid")
    #remove.removeTable("Suppliers2")
    #display.displayTable("Products", "queryResult.txt")
    #relAlg.select("Supply", "cost", "=", 31.0)
    #relAlg.select("Suppliers", "sid", "=", "s04")
    #relAlg.project("Products", ["pid", "pname"])
    relAlg.join("Suppliers", "sid", "Supply", "sid")
    #relAlg.select("Supply", "sid", "=", "s03")
