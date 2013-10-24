"""
Script to converting tracemalloc documentation into PEP format to include it
into the PEP 454.
"""

import sys
import re
import textwrap
import subprocess

with open("Doc/library/tracemalloc.rst") as fp:
    content = fp.read()

pos = content.index("\nAPI\n")
content = content[pos:]

content = content.strip() + "\n\n"

content = content.replace("~", "")

content = re.sub(
    r"^ *\.\. (attribute|class|function|method|classmethod):: (.*)",
    r"``\2`` \1:",
    content,
    flags=re.MULTILINE)

content = re.sub(
    r":(?:func|meth):`([^`]+)`",
    r"``\1()``",
    content)

content = re.sub(
    r":(?:mod|class|attr|option|envvar):`([^`]+)`",
    r"``\1``",
    content)

content = content.splitlines()
lines = []
index = 0
start = None
while index < len(content):
    line = content[index]
    if line.startswith(' '):
        if start is None:
            start = index
    else:
        if start:
            pararaph = ' '.join(line.strip() for line in content[start:index])
            pararaph = textwrap.wrap(pararaph, 72 - 4)
            for line in pararaph:
                lines.append('    ' + line)
        lines.append(content[index])
        start = None
    index += 1

with open("pep.rst", "w") as fp:
    fp.write('\n'.join(lines))

subprocess.call(["rst2html", "pep.rst", "pep.html"])
