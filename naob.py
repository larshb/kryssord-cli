#!/usr/bin/env python3

import re
import html
from pathlib import Path

import requests

from markup import Element, ElementTree


class FormattedString:

    def __init__(self, txt, fmt="\x1b[0m"):
        self.txt = txt
        self.fmt = fmt

        # if txt == " ":
        #     print("' '")

    def __str__(self):
        if self.fmt:
            return self.fmt + self.txt  # + "\x1b[0m"
        else:
            return self.txt

    __repr__ = __str__


NEWLINE = FormattedString("\n", fmt="\x1b[0m")
full_output = []


def minidom_refresh(max_lines=24):
    global full_output

    # Cleanup
    for i, x in enumerate(full_output):
        try:
            if x.txt.startswith(")"):
                full_output[i - 1].txt = full_output[i - 1].txt.rstrip()
        except:
            pass

    raw_list = [str(x) for x in full_output]
    raw = "".join(raw_list)
    orig = raw
    # raw = raw.replace("\n", " ")
    # raw = raw.strip()
    raw = html.unescape(raw)
    raw = raw.replace(" )", ")")
    raw = raw.strip()
    if raw:
        for i, line in enumerate(raw.splitlines()):
            print(line.strip())
            if (i + 1) == max_lines:
                break
        return True
    return False


def minidom(et: ElementTree):

    def recurse(parents, element, selected, fmt):

        global full_output

        if not selected and isinstance(element, Element):
            selected = element.attributes.get("class") == "article"

        if selected:

            # Inner
            if isinstance(element, str):
                output = element
                output = output.replace("\n", " ")

                while "  " in output:
                    output = output.replace("  ", " ")

                # Clear intrusive white-space
                try:
                    while (
                        len(output)
                        and output[0] in ";,)"
                        and full_output[-1].txt[-1] == " "
                    ):
                        full_output[-1].txt = full_output[-1].txt[:-1]
                except:
                    pass
                try:
                    while (
                        len(output)
                        and output[0] in " "
                        and full_output[-1].txt[0] in "\n"
                    ):
                        output = output[1:]
                except:
                    pass
                try:
                    while (
                        len(output)
                        and output[0] in " "
                        and full_output[-1].txt[-1] in " "
                    ):
                        output = output[1:]
                except:
                    pass

                if output.strip() == "":
                    output = ""
                if output != "":
                    full_output += [FormattedString(output, fmt)]

            # Element
            else:
                if element.name in ["div"] and (
                    "inline-eske" not in element.attributes.get("class", "")
                ):
                    full_output += [NEWLINE]

            while (len(full_output) > 1) and (full_output[-2:] == [NEWLINE, NEWLINE]):
                full_output = full_output[:-1]

        # Formatted inline heading
        overskrift = isinstance(element, Element) and (
            "overskrift" in element.attributes.get("class", "")
        )
        if overskrift:
            full_output += [NEWLINE]
            fmt += "\x1b[1m\x1b[31m"

        # .oppslagsord => Bold
        oppslagsord = isinstance(element, Element) and (
            "oppslagsord" == element.attributes.get("class", "")
        )
        if oppslagsord:
            fmt += "\x1b[1m"

        # .betydningnr => Bold
        betydningnr = isinstance(element, Element) and (
            "betydningnr" == element.attributes.get("class", "")
        )
        if betydningnr:
            fmt += "\x1b[1m"

        # .uttrykk => Bold
        uttrykk = isinstance(element, Element) and (
            "uttrykk" == element.attributes.get("class", "")
        )
        uttrykk |= isinstance(element, Element) and (
            "uttrykk " in element.attributes.get("class", "")
        )
        if uttrykk:
            fmt += "\x1b[1m"

        # .histform => Italic
        histform = isinstance(element, Element) and (
            "histform" in element.attributes.get("class", "")
        )
        if histform:
            fmt += "\x1b[3m"

        # .redeks => Italic
        redeks = isinstance(element, Element) and (
            "redeks " in element.attributes.get("class", "")
        )
        redeks |= isinstance(element, Element) and (
            "redeks" == element.attributes.get("class", "")
        )
        if redeks:
            fmt += "\x1b[3m"

        # Ignore collapsed
        content = isinstance(element, Element) and (
            "content" in element.attributes.get("class", "")
        )
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


def clean_string(string):
    string = html.unescape(string)
    lines = []
    for line in string.splitlines():
        line = line.strip()
        if line:
            lines.append(line)
    return "\n".join(lines)


def naob_multi_result(html):
    treff = None
    for capt in re.finditer(r"<p class=\"page[^>]*?>.*?(\d+).*?treff", html):
        treff = capt.group(1)
        print(f"{treff} treff")
        print()

        for capt in re.finditer(
            r"<li class=\"page[^>]*?>(.*?)</li>", html, re.M | re.S
        ):
            entry = capt.group(1)

            try:
                capt = re.match(
                    r".*?href=\"([^\"]*?)\">([^<]*?)<.*?<span class=\"ordklasse[^>]*?>([^<]*?)</span>([^<]*?)<.*",
                    entry,
                    re.M | re.S,
                )
                href, ordbok, ordklasse, beskrivelse = capt.groups()
                print("\x1b[1m" + ordbok + "\x1b[0m")
                if href != f"/ordbok/{ordbok}":
                    print("\x1b[4m\x1b[34m" + "https://naob.no" + href + "\x1b[0m")
                print("\x1b[1m\x1b[31m" + ordklasse + "\x1b[0m")
                print(clean_string(beskrivelse))
            except:
                print("<PARSE ERROR>")

            print()

        return True

    return False


def naob_search(word, max_lines=24, load_from_cache=True, save_to_cache=True):

    url = f"https://naob.no/ordbok/{word}"
    cache_path = Path(__file__).parent / ".cache" / (word + ".html")

    if load_from_cache and cache_path.exists():
        print(cache_path)
        text = open(cache_path).read()
    else:
        response = requests.get(url)
        text = response.text
        if save_to_cache:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            open(cache_path, "w").write(text)

    if not naob_multi_result(text):
        et = ElementTree(text)
        minidom(et)
        if minidom_refresh(max_lines=max_lines):
            print()

    print("\x1b[4m\x1b[34m" + url + "\x1b[0m\n")


if __name__ == "__main__":

    import sys

    if len(sys.argv) > 1:
        word = sys.argv[1]
    else:
        # word = "løs"
        word = "stoisisme"
        # word = "golde"
        # word = "gold"
    naob_search(word)
