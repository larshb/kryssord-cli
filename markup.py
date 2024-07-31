import requests
from dataclasses import dataclass
from typing import List
import re


def fail(msg):
    print(msg)
    exit(1)


def prune_unrenderable_html(html, remove=True, max_passes=5):

    PATTERN_REPL = [
        (r"<script[^>]*?/>", "<script />"),
        (r"<script[^>]*?>[^<]*?</script>", r"<script></script>"),
        (r"<link[^>]*?/>", "<link />"),
        (r"<link[^>]*?>[^<]*?</link>", r"<link></link>"),
        (r"<meta[^>]*?/>", "<meta />"),
        (r"<meta[^>]*?>[^<]*?</meta>", r"<meta></meta>"),
    ]

    for _ in range(max_passes):

        total = 0
        for pattern, repl in PATTERN_REPL:

            # Remove the tag alltogether to clean up HTML
            if remove:
                repl = ""

            html, n = re.subn(pattern, repl, html, re.M)
            total += n

        if total == 0:
            return html

    fail(f"Still running substitutions after {max_passes} passes")
    return html


@dataclass
class Element:

    name: str
    attributes: dict
    children: List
    self_closing: bool


def create_element_from_html(html):

    self_closing = html.replace(" ", "").endswith("/>")

    if capt := re.match(r"<(?P<name>\w+) (?P<attributes>.*)>", html):
        tag = capt.groupdict()
        name = tag["name"]
        attributes = {}
        for kw_attribute in re.findall(r"(\w+)=\"(.*?)\"", tag["attributes"]):
            k, v = kw_attribute
            attributes[k] = v
        element = Element(name, attributes, [], self_closing)

    elif capt := re.match(r"<(?P<name>\w+)/*>", html):
        tag = capt.groupdict()
        name = tag["name"]
        attributes = {}
        element = Element(name, attributes, [], self_closing)

    else:
        fail("Unparsed: " + html)

    return element


class ElementTree:

    def __init__(self, html=""):

        # Top level pseudo-element
        self.root = Element("root", {}, [], False)

        if html != "":
            self.html_parse(html)

    def html_parse(self, html):

        parents = [self.root]
        element = None

        html = html.strip()
        html = prune_unrenderable_html(html)

        for data in re.findall(r"((?:<.*?>)|(?:[^<]*))", html, re.M | re.S):

            # Empty match?
            if not len(data):
                continue

            # Tag?
            if data[0] == "<":

                # Meta-tag?
                if data[1] == "!":
                    continue

                # Closing?
                if capt := re.match(r"</(.*)>", data):
                    name = capt.group(1)
                    if (element is None) and parents:
                        element = parents.pop()
                    if element.name != name:

                        # Implicit self closing
                        element = parents.pop()
                        if element.name != name:
                            fail(f"Closing {element.name=}, {name=}")

                    if parents:
                        element = parents.pop()
                    else:
                        element = None
                    continue

                # Is child?
                if element is not None:
                    parents.append(element)

                element = create_element_from_html(data)

                # Hierarchy
                parents[-1].children.append(element)

                if element.self_closing:
                    element = None

            # Inner?
            else:
                if element is None:
                    fail("Inner data without element")
                else:
                    element.children.append(data)

        if element != self.root:
            fail("Incomplete tree")

    def export(self, indent=2, max_level=-1):

        def recurse(level, element):
            lines = []
            if level == max_level:
                return lines
            if isinstance(element, str):
                return [" " * (level * indent) + element]
            opening = " " * (level * indent) + "<" + element.name
            for k, v in element.attributes.items():
                opening += f' {k}="{v}"'
            if element.self_closing:
                opening += " /"
            opening += ">"
            lines += [opening]
            if element.children:
                for child in element.children:
                    lines += recurse(level + 1, child)
            lines += [" " * (level * indent) + "</" + element.name + ">"]
            return lines

        lines = []
        for child in self.root.children:
            lines += recurse(0, child)
        return "\n".join(lines)


if __name__ == "__main__":
    text = open("test.html").read()
    et = ElementTree(text)
    print(et.export())
