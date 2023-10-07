from lxml import etree

path="init.cpp.xml"
parser = etree.HTMLParser(encoding="utf-8")
e = etree.parse(path, parser)
nodes=e.xpath("//call[name/name[contains(text(),\"def\")]]")
for node in nodes:
    print(node,node.sourceline)
    results=node.xpath("descendant::literal")
    for ans in results:
        print(ans.text[1:-1])