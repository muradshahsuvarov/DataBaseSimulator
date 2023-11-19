import relAlg
import buildTree
import remove
import display
from utility import BPlusTree

if __name__ == '__main__':
    # ---------------------Experiments---------------------

    # root = buildTree.build("Suppliers", "sid", 2)
    # root = buildTree.build("Supply", "pid", 2)
    # BPlusTree.display(root)
    # display.displayTree("pg946.txt")
    # remove.removeTree("Supply", "pid")
    # remove.removeTree("Suppliers", "sid")
    # remove.removeTree("Supply", "cost")
    # remove.removeTable("Suppliers2")
    # display.displayTable("Products", "queryResult.txt")
    # relAlg.select("Supply", "cost", ">", 34.02)
    # relAlg.select("Suppliers", "sid", "=", "s04")
    # relAlg.project("Products", ["pid", "pname"])
    # relAlg.join("Suppliers", "sid", "Supply", "sid")
    # relAlg.select("Supply", "sid", "<", "s03")

    # ---------------------TASK 8.a---------------------

    # selected_supplier = relAlg.select(rel='Suppliers', att='sid', op='==', val='s23')

    # ---------------------TASK 8.b---------------------

    # remove.removeTree("Suppliers", "sid")
    # selected_supplier = relAlg.select(rel='Suppliers', att='sid', op='==', val='s23')

    # TASK 8.c

    # Step 1: Select suppliers who supplied 'p15'
    # supplied_p15 = relAlg.select('Supply', 'pid', '=', 'p15')

    # Step 2: Project sid and address from Suppliers
    # suppliers_addresses = relAlg.project('Suppliers', ['sid', 'address'])

    # Step 3: Join the results to get the addresses of suppliers who supplied 'p15'
    # suppliers_who_supplied_p15 = relAlg.join(supplied_p15, 'sid', suppliers_addresses, 'sid')

    # ---------------------TASK 8.d---------------------

    #suppliers_kiddie = relAlg.select('Suppliers', 'sname', '==', 'Kiddie')

    #products_p20 = relAlg.select('Products', 'pid', '==', 'p20')

    # Join suppliers_kiddie with Supply on supplier ID
    #join1 = relAlg.join(suppliers_kiddie, 'sid', 'Supply', 'sid')

    # Join join1 with products_p20 on product ID
    #final_join = relAlg.join(join1, 'pid', products_p20, 'pid')

    #cost_result = relAlg.project(final_join, ['cost'])

    # ---------------------TASK 8.e---------------------

    # Step 1: Select records from the Supply relation where cost >= 47
    selected_supply = relAlg.select('Supply', 'cost', '>=', 47)

    # Step 2: Join the selected_supply with Suppliers on supplier ID
    joined_with_suppliers = relAlg.join(selected_supply, 'sid', 'Suppliers', 'sid')

    # Step 3: Join the joined_with_suppliers with Products on product ID
    final_join = relAlg.join(joined_with_suppliers, 'pid', 'Products', 'pid')

    # Step 4: Project the required attributes: supplier's name, product's name, and cost
    projected_result = relAlg.project(final_join, ['sname', 'pname', 'cost'])



