from lxml import etree

path="F:\\python_workplace\\check_utils\\utils\\xml_files\\torch\\csrc\\dynamo\\eval_frame.c.xml"
path2="dim.cpp.xml"
fun_name="_set_pointwise_optimize"
parser = etree.HTMLParser(encoding="utf-8")
e=etree.parse(path2,parser)
nodes=e.xpath("//function[name=\'{}\']".format(fun_name))
code_smell_list=[]
if len(nodes)!=0:
    print("nodes_length=",len(nodes))
    print(nodes[0].getparent().tag)
    st_node=nodes[0].find("type/specifier")
    # print("std_node_len=",len(st_node))
    print(st_node)
    print(type(st_node))
    if st_node is not None and st_node.text=='static':
        print("lalalalalala")
    else:
        code_smell_list.append([path,fun_name,nodes[0].sourceline-3])
else:
    print(path)
    print(fun_name)
    print("======================================")
for item in code_smell_list:
    print(item)