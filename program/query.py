import relAlg
import buildTree

if __name__ == '__main__':
    bTree = buildTree.build("Suppliers", "sid", 1)
    bTree.display()
    # relAlg.build("Products", "color", "==", "pink")
