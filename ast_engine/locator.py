# ast_engine/locator.py

def walk(node, results):
    results.append(node)

    for child in node.children:
        walk(child, results)


def get_all_nodes(tree):
    nodes = []
    walk(tree.root_node, nodes)
    return nodes



def find_python_function(tree, function_name):
    nodes = get_all_nodes(tree)

    for node in nodes:
        if node.type == "function_definition":
            name_node = node.child_by_field_name("name")

            if name_node:
                name = name_node.text.decode()

                if name == function_name:
                    return node

    return None