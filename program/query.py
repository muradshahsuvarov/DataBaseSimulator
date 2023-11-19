import relAlg
import buildTree
import remove
import display
from utility import BPlusTree

if __name__ == '__main__':

    # Experiments

    #root = buildTree.build("Suppliers", "sid", 2)
    #root = buildTree.build("Supply", "pid", 2)
    #BPlusTree.display(root)
    #display.displayTree("pg946.txt")
    #remove.removeTree("Supply", "pid")
    #remove.removeTree("Suppliers", "sid")
    #remove.removeTree("Supply", "cost")
    #remove.removeTable("Suppliers2")
    #display.displayTable("Products", "queryResult.txt")
    #relAlg.select("Supply", "cost", ">", 34.02)
    #relAlg.select("Suppliers", "sid", "=", "s04")
    #relAlg.project("Products", ["pid", "pname"])
    #relAlg.join("Suppliers", "sid", "Supply", "sid")
    #relAlg.select("Supply", "sid", "<", "s03")

    # TASK 8.a

    #selected_supplier = relAlg.select(rel='Suppliers', att='sid', op='==', val='s23')


    # TASK 8.b

    #remove.removeTree("Suppliers", "sid")
    #selected_supplier = relAlg.select(rel='Suppliers', att='sid', op='==', val='s23')

    # TASK 8.c

    # Step 1: Select suppliers who supplied 'p15'
    supplied_p15 = relAlg.select('Supply', 'pid', '=', 'p15')

    # Step 2: Project sid and address from Suppliers
    suppliers_addresses = relAlg.project('Suppliers', ['sid', 'address'])

    # Step 3: Join the results to get the addresses of suppliers who supplied 'p15'
    suppliers_who_supplied_p15 = relAlg.join(supplied_p15, 'sid', suppliers_addresses, 'sid')


