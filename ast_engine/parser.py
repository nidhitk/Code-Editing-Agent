# ast_engine/parser.py

from tree_sitter import Parser
import tree_sitter_python
import tree_sitter_javascript
import tree_sitter_java


LANGUAGE_MAP = {
    ".py": tree_sitter_python.language(),
    ".js": tree_sitter_javascript.language(),
    ".java": tree_sitter_java.language()
}


def get_parser(extension):
    parser = Parser()

    if extension not in LANGUAGE_MAP:
        raise ValueError(f"Unsupported extension: {extension}")

    parser.language = LANGUAGE_MAP[extension]
    return parser


def parse_code(code, extension):
    parser = get_parser(extension)
    tree = parser.parse(bytes(code, "utf8"))
    return tree