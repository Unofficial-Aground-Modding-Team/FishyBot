"""
Custom XML Parser created to convert Aground XML files into a more standard format
(in particular, `&&`, `<` and such existing where they shouldn't causes normal parsers to error)
"""

import collections
import textwrap
import typing
import re

class _XmlDict(typing.TypedDict):
    name: str
    attributes: dict[str, str]
    children: typing.NotRequired[list["_XmlDict"]]
    text: typing.NotRequired[str]


class XmlNode:
    def __init__(self, name: str, attributes: dict[str, str], children: list["XmlNode"], text: str):
        self.name = name
        self.attributes = attributes
        self.children = children
        self.text = text

    def get_children(self, name: str | None = None, recursive: bool = False) -> typing.Generator['XmlNode', None, None]:
        for child in self.children:
            if name is None or child.name == name:
                yield child
            if recursive:
                yield from child.get_children(name, recursive)

    def clean(self) -> None:
        "Escapes special characters in this node and its children (modifies in place)"
        self.text = escape(self.text)
        # TODO THINK SOME MORE ABOUT QUOTES
        self.attributes = {key: escape(value).replace('"', "'") for key, value in self.attributes.items()}
        for child in self.get_children():
            child.clean()

    def __repr__(self) -> str:
        _id = f"${self.attributes['id']}" if 'id' in self.attributes else ''
        return f"XmlNode({self.name}{_id}, attributes={set(self.attributes)}, children={[child.name for child in self.children]})"

    def __str__(self) -> str:
        _attrs = " ".join(f'''{key}="{value}"''' for key, value in self.attributes.items())
        if _attrs:
            _attrs = ' ' + _attrs
        if self.children:
            _child = "\n".join(child.__str__() for child in self.children)
            _child = textwrap.indent(_child, "    ")
            return f"""<{self.name}{_attrs}>\n{_child}\n</{self.name}>"""
        elif self.text:
            if '\n' in self.text:
                text = textwrap.indent(textwrap.dedent(self.text).strip(), "    ")
                return f"""<{self.name}{_attrs}>\n{text}\n</{self.name}>"""
            else:
                return f"""<{self.name}{_attrs}>{self.text}</{self.name}>"""
        else:
            return f"""<{self.name}{_attrs}/>"""

    def to_str(self) -> str:
        return str(self)

    def to_dict(self) -> _XmlDict:
        result: _XmlDict = {
            "name": self.name,
            "attributes": self.attributes,
        }
        if self.children:
            result["children"] = [child.to_dict() for child in self.children]
        if (txt := self.text.strip()):
            result["text"] = txt
        return result


class Parser:
    def __init__(self, text: str):
        self._text = text
        self.buffer = collections.deque(text)

    def parse(self, clean: bool = True) -> XmlNode:
        while True:
            try:
                char = self.buffer.popleft()
            except IndexError:
                raise Exception('unexpected state')
            if self.buffer[0] == "?":  # skip the header
                continue
            if self.buffer[0] == "!":  # ignore comments before the start of the file
                continue
            if char == "<":
                root = self.parse_element()
                if clean:
                    root.clean()
                return root

    def parse_element(self) -> XmlNode:
        name, has_attributes, has_children = self._read_name()
        if has_attributes:
            attributes, has_children = self._parse_attributes()
        else:
            attributes = {}
        assert has_children is not None
        if has_children:
            children, text = self.parse_children(name)
        else:
            children = []
            text = ""
        return XmlNode(name, attributes, children, text)

    def _read_name(self) -> tuple[str, bool, bool | None]:
        "Returned values: `name`, `has_attributes`, `has_children`"
        name = ''
        while True:
            character = self.buffer.popleft()
            # <name ; may have attributes ; may or may not have children
            if character == ' ':
                return name, True, None
            # <name/> ; must not have attributes ; must not have children 
            elif character == "/":
                assert self.buffer.popleft() == ">"
                return name, False, False
            # <name> ; must not have attributes ; may have children 
            elif character == '>':
                return name, False, True
            elif not character.isspace():
                name += character

    def _parse_attributes(self) -> tuple[dict[str, str], str]:
        attributes = {}
        while True:
            try:
                name, value = self._parse_attribute()
            except StopIteration as err:
                has_children = err.args[0]['has_children']
                break
            attributes[name] = value
        return attributes, has_children
    
    def _parse_attribute(self) -> tuple[str, str]:
        name = ''
        while True:
            character = self.buffer.popleft()
            if character == "=":
                start_quote = self.buffer.popleft()
                break
            elif character == "/":
                if self.buffer.popleft() == ">":
                    raise StopIteration({"has_children": False})
                else:
                    raise Exception("Unexpected state")
            elif character == ">":
                raise StopIteration({"has_children": True})
            elif not character.isspace():
                name += character
        value = ''
        while True:
            character = self.buffer.popleft()
            if character == start_quote:
                break
            value += character
        return name, value        

    def parse_children(self, node_name: str) -> tuple[list[XmlNode], str]:
        children: list[XmlNode] = []
        text = ""
        while True:
            character = self.buffer.popleft()
            if character == "<":
                # <!-- comments -->
                if self.buffer[0] == "!":
                    minus2 = ''
                    minus1 = ''
                    char = ''
                    while not (char == ">" and minus1 == "-" and minus2 == "-"):
                        minus2, minus1, char = minus1, char, self.buffer.popleft()
                    continue
                # </closing>
                if self.buffer[0] == "/" and all(self.buffer[i+1] == node_name[i] for i in range(len(node_name))):
                    # remove from the buffer
                    while True:
                        character = self.buffer.popleft()
                        if character == '>':
                            break
                    return children, text
                # <child>
                child = self.parse_element()
                children.append(child)
            # random text (e.g. inside of <action> or <text>). Also ends up catching a lot of whitespace junk.
            else:
                text += character


def parse(text: str) -> XmlNode:
    return Parser(text).parse()

_replacements = {
    # '"': "&quot;",
    # "'": "&apos;",
    r"<": "&lt;",
    r">": "&gt;",
    r"&(?!(gt;|lt;|amp;))": "&amp;",
}

_replacements = [(re.compile(pattern), replacement) for pattern, replacement in _replacements.items()]

def escape(string: str) -> str:
    for pattern, replacement in _replacements:
        string = re.sub(pattern, replacement, string)
    return string



if __name__ == "__main__":

    import pathlib

    with (pathlib.Path(__file__).parent / 'file.xml').open() as file:
        parser = Parser(file.read())

    data = parser.parse()

    with (pathlib.Path(__file__).parent / 'test_out.xml').open('w') as file:
        file.write(data.to_str())

    import json
    with (pathlib.Path(__file__).parent / 'test_out.json').open('w') as file:
        json.dump(data.to_dict(), file, indent=4)
