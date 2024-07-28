import requests
from dataclasses import dataclass
from typing import List
import re

def fail(msg):
    print(msg)
    exit(1)

@dataclass
class Element:

    name: str
    attributes: dict
    children: List

class ElementTree:

    def __init__(self, string):

        self.root = Element("root", {}, [])
        parents = [self.root]
        element = None

        string = string.strip()
        for data in re.findall(r"((?:<.*?>)|(?:[^<]*))", string, re.M):

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
                    #element = parents.pop()
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
                
                # Parse tag
                if capt := re.match(r"<(?P<name>\w+) (?P<attributes>.*)>", data):
                    tag = capt.groupdict()
                    name = tag["name"]
                    attributes = {}
                    for kw_attribute in re.findall(r"(\w+)=\"(.*?)\"", tag["attributes"]):
                        k, v = kw_attribute
                        attributes[k] = v
                    element = Element(name, attributes, [])
                elif capt := re.match(r"<(?P<name>\w+)/*>", data):
                    tag = capt.groupdict()
                    name = tag["name"]
                    attributes = {}
                    element = Element(name, attributes, [])
                else:
                    fail("Unparsed: " + data)

                # Hierarchy
                parents[-1].children.append(element)

                # Self closing?
                if data.replace(" ", "").endswith("/>"):
                    element = None

            # Inner?
            else:
                if element is None:
                    fail("Inner data without element")
                else:
                    element.children.append(data)

        if element != self.root:
            fail("Incomplete tree")

    def print_structure(self, indent=2, max_level=3):

        def recurse(level, element, max_level=max_level):
            if level == max_level:
                return
            print(" "*(level*indent) + "<" + element.name + ">")
            if element.children:
                for child in element.children:
                    recurse(level + 1, child)
            print(" "*(level*indent) + "</" + element.name + ">")
        
        recurse(0, self.root)

full_output = []

class FormattedString:

    def __init__(self, txt, fmt="\x1b[0m"):
        self.txt = txt
        self.fmt = fmt

        # if txt == " ":
        #     print("' '")

    def __str__(self):
        if self.fmt:
            return self.fmt + self.txt #+ "\x1b[0m"
        else:
            return self.txt
    
    __repr__ = __str__

NEWLINE = FormattedString("\n", fmt="\x1b[0m")

def minidom_refresh(max_lines=24):
    global full_output

    # Cleanup
    for i, x in enumerate(full_output):
        try:
            if x.txt.startswith(")"):
                full_output[i-1].txt = full_output[i-1].txt.rstrip()
        except:
            pass

    # print("\x1b[2J\x1b[H")
    raw_list = [str(x) for x in full_output]
    raw = ''.join(raw_list)
    orig = raw
    #raw = raw.replace("\n", " ")
    # raw = raw.strip()
    raw = raw.replace("&#160;", " ")
    raw = raw.replace("&aelig;", "æ")
    raw = raw.replace("&oslash;", "ø")
    raw = raw.replace("&aring;", "å")
    raw = raw.replace("&Aelig;", "Æ")
    raw = raw.replace("&Oslash;", "Ø")
    raw = raw.replace("&Aring;", "Å")
    raw = raw.replace("&aacute;", "á")
    raw = raw.replace("&acute;", "´")
    raw = raw.replace("&hellip;", "…")
    raw = raw.replace("&ndash;", "–")
    raw = raw.replace(" )", ")")
    raw = raw.strip()
    if raw:
        for i, line in enumerate(raw.splitlines()):
            print(line.strip())
            if (i+1) == max_lines:
                break
        return True
    return False

def minidom(et: ElementTree):

    def recurse(parents, element, selected, fmt):

        global full_output

        if not selected and isinstance(element, Element):
            selected = (element.attributes.get("class") == "article")

        if selected:

            # Inner
            if isinstance(element, str):
                output = element
                output = output.replace("\n", " ")
                
                # output = output.strip()
                while "  " in output:
                    output = output.replace("  ", " ")

                # Clear intrusive white-space
                try:
                    while len(output) and output[0] in ";,)" and full_output[-1].txt[-1] == " ":
                        full_output[-1].txt = full_output[-1].txt[:-1]
                except:
                    pass
                try:
                    while len(output) and output[0] in " " and full_output[-1].txt[0] in "\n":
                        output = output[1:]
                except:
                    pass
                try:
                    while len(output) and output[0] in " " and full_output[-1].txt[-1] in " ":
                        output = output[1:]
                except:
                    pass

                # output = output.replace("&#160;", " ")
                # output = output.replace("&aelig;", "æ")
                # output = output.replace("&oslash;", "ø")
                # output = output.replace("&aring;", "å")
                # output = output.replace("&Aelig;", "Æ")
                # output = output.replace("&Oslash;", "Ø")
                # output = output.replace("&Aring;", "Å")
                if output.strip() == "":
                    output = ""
                if output != "":
                    full_output += [FormattedString(output, fmt)]

            # Element
            else:
                if element.name in ["p", "br"]:
                    pass #full_output += [NEWLINE]
                elif element.name in ["div"] and ("inline-eske" not in element.attributes.get("class", "")):
                    full_output += [NEWLINE]
                # elif element.name in ["span"]:
                #     if str(full_output[-1])[-1] != " ":
                #         full_output += [" "]
                else:
                    pass
                    # print(f"\n<{element.name}>\n")
                    # if output != "":
                    #     exit(0)

            while (len(full_output) > 1) and (full_output[-2:] == [NEWLINE, NEWLINE]):
                full_output = full_output[:-1]

            # if True:
            #     print("\x1b[2J\x1b[H" + ''.join(str(x) for x in full_output))
            #     print("...")
        
        # Formatted inline heading
        overskrift = isinstance(element, Element) and ("overskrift" in element.attributes.get("class", ""))
        if overskrift:
            full_output += [NEWLINE]
            fmt += "\x1b[1m\x1b[31m"

        # .oppslagsord => Bold
        oppslagsord = isinstance(element, Element) and ("oppslagsord" == element.attributes.get("class", ""))
        if oppslagsord:
            fmt += "\x1b[1m"

        # .betydningnr => Bold
        betydningnr = isinstance(element, Element) and ("betydningnr" == element.attributes.get("class", ""))
        if betydningnr:
            fmt += "\x1b[1m"

        # .uttrykk => Bold
        uttrykk = isinstance(element, Element) and ("uttrykk" == element.attributes.get("class", ""))
        uttrykk |= isinstance(element, Element) and ("uttrykk " in element.attributes.get("class", ""))
        if uttrykk:
            fmt += "\x1b[1m"

        # .histform => Italic
        histform = isinstance(element, Element) and ("histform" in element.attributes.get("class", ""))
        if histform:
            fmt += "\x1b[3m"

        # .redeks => Italic
        redeks = isinstance(element, Element) and ("redeks " in element.attributes.get("class", ""))
        redeks |= isinstance(element, Element) and ("redeks" == element.attributes.get("class", ""))
        if redeks:
            fmt += "\x1b[3m"

        # Ignore collapsed
        content = isinstance(element, Element) and ("content" in element.attributes.get("class", ""))
        if content:
            return

        # ul
        li = isinstance(element, Element) and ("li" == element.name)
        if li:
            try:
                if full_output[-1].txt[-1] != "\n":
                    full_output += [FormattedString("\n")]
                full_output += [FormattedString("\x1b[0m• ")]
            except:
                pass

        # a
        a = isinstance(element, Element) and ("a" == element.name)
        if a:
            fmt += "\x1b[4m"

        # span
        span = isinstance(element, Element) and ("span" == element.name)
        if span:
            pass

        # Recurse
        if isinstance(element, Element) and element.children:
            for child in element.children:
                if isinstance(child, Element) and child.name == "script":
                    pass
                else:
                    recurse(parents + [element], child, selected, fmt)

        fmt = "\x1b[0m"

        if overskrift or li:
            full_output += [NEWLINE]

        if oppslagsord:
            full_output += [FormattedString(" \t")]

        if span or a:
            try:
                if full_output[-1].txt[-1] not in " \n":
                    full_output += [FormattedString(" ")]
            except:
                pass

        # if minidom_refresh():
        #     print()
    
    recurse([], et.root, False, "\x1b[0m")


def naob_search(word, max_lines=24):

    url = f"https://naob.no/ordbok/{word}"
    response = requests.get(url)
    text = response.text
    
    et = ElementTree(text)
    #et.print_structure()
    minidom(et)
    if minidom_refresh(max_lines=max_lines):
        print()
    
    print("\x1b[4m\x1b[34m" + url + "\x1b[0m\n")


if __name__ == "__main__":
    # text = open("test.html").read()
    
    # # url = "https://naob.no/ordbok/l%C3%B8s"
    # # url = "https://naob.no/ordbok/løs"
    # url = "https://naob.no/ordbok/stoisisme"
    # response = requests.get(url)
    # text = response.text
    
    # et = ElementTree(text)
    # #et.print_structure()
    # minidom(et)
    # if minidom_refresh(max_lines=30):
    #     print()

    import sys
    if len(sys.argv) > 1:
        word = sys.argv[1]
    else:
        word = "golde"
    naob_search(word)
