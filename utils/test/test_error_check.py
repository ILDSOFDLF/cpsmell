from lxml import etree

parser = etree.HTMLParser(encoding="utf-8")
path="F:\\python_workplace\\cpsmell\\utils\\xml_files\\torch\\csrc\\Exceptions.cpp.xml"
path2="dim.cpp.xml"
path3="python_return_types.cpp.xml"
path4="Generator.cpp.xml"
e=etree.parse(path4,parser)
list=e.xpath("//expr[call/name=\'PyModule_AddObject\']")
error_detection=[]
for node in list:
    print(node.tag)
    print(node.getparent().tag)
    if node.getparent().tag == 'condition':
        print("has condition")
        continue
    if node.find('operator') is not None:
        print("has operation")
        continue
    try_list=e.xpath("//try//expr[call/name=\'PyModule_AddObject\']")
    flag_try=False
    if try_list is not None:
        for t in try_list:
            if t==node:
                flag_try=True
                print("try.............")
                break
    print(flag_try)
    if not flag_try:
        sub_error_detection=[node.sourceline-1]
        error_detection.append(sub_error_detection)
for ans in error_detection:
    print(ans)
