from lxml import etree

QUERY_CALL="//expr_stmt/expr"
path="F:\\python_workplace\\cpsmell\\utils\\xml_files\\tensorflow\\compiler\\mlir\\python\\mlir_wrapper\\mlir_wrapper.cc.xml"
path2="F:\\python_workplace\\cpsmell\\utils\\xml_files\\paddle\\fluid\\pybind\\protobuf.cc.xml"
path3="rpc.cc.xml"
path4="init.cc.xml"
path5="F:\\python_workplace\\cpsmell\\utils\\xml_files\\tensorflow\\compiler\\xla\\python\\xla.cc.xml"
path6="F:\\python_workplace\\cpsmell\\utils\\xml_files\\tensorflow\\compiler\\xla\\mlir_hlo\\bindings\\python\\MlirHloModule.cc.xml"
parser = etree.HTMLParser(encoding="utf-8")
e=etree.parse(path6,parser)
#
for call_name in e.xpath(QUERY_CALL):
    dest=[]
    for nodes in call_name.iter():
        dest.append(nodes)
        if nodes.tag=='name' and dest[1].tag=='call':
            param=dest[1].xpath("argument_list[argument/expr/name=\'m\']")
            if len(dest) == 3 and len(param)!=0:
                argnum = 0
                for subnode in param[0].iter():
                    if subnode.tag == 'argument':
                        argnum = argnum + 1
                if argnum > 1:
                    break
                name = nodes.text
                if name is None:
                    name=nodes.find('name[last()]')
                    name=name.text
                if name == 'class_' or name == 'enum_':
                    break
                print(name)
            else:
                break

    print("============================")

list11=[1,21,54,13,58]
for i in list11:
    if i==54:
        list11.append(100)
    print(i)

for j in range(0):
    print("=======")
    print(j)

call_name="InitAndSetAgentInstance"
str1="//function[type/name=\'void\' and name[1]=\'{}\']/block/block_content/expr_stmt/expr/call[name/name[last()]=\'class_\']".format(call_name)
str2="//function[type/name=\'void\' and name[1]=\'{}\']/block/block_content/decl_stmt/decl[type/name/name[last()]=\'class_\']".format(call_name)
str3="//function[type/name=\'void\' and name[1]=\'{}\']/block/block_content/expr_stmt/expr/call[name[name[1]=\'m\' and name[2]=\'def\']]/child::argument_list".format(call_name)
print(str1)
print(type(str1))
nodes1=e.xpath(str1)
nodes2=e.xpath(str2)
nodes3=e.xpath(str3)
c_py_class_list = []
for node in nodes1:

    c_class1 = node.find('name/argument_list/argument/expr/name')

    if c_class1 is None or c_class1.text is None:
        c_class1 = node.find('name/argument_list/argument/expr/name/name[last()]')
    print(c_class1)
    py_class1 = node.find('argument_list/argument[2]/expr/literal')
    if py_class1 is None or c_class1 is None:
        continue
    c_py_sub_class = [path, c_class1.sourceline - 1, c_class1.text, py_class1.text[1:-1]]
    c_py_class_list.append(c_py_sub_class)
for node in nodes2:

    c_class2 = node.find('type/name/argument_list/argument/expr/name')
    if c_class2 is None or c_class2.text is None:
        c_class2 = node.find('type/name/argument_list/argument/expr/name/name[last()]')
    print(c_class2.text)
    py_class2 = node.find('argument_list/argument[2]/expr/literal')
    if py_class2 is None or c_class2 is None:
        continue
    c_py_sub_class = [path, c_class2.sourceline - 1, c_class2.text, py_class2.text[1:-1]]
    c_py_class_list.append(c_py_sub_class)

c_py_fun_list=[]
for node in nodes3:
    c_py_sub_list = []
    flag_lambda = False
    arg_num = 0
    parent_node = node
    c_py_sub_list.append(path)
    # c_py_sub_list.append(module_name)

    for childnode in node.iter():
        # print(childnode.tag)

        if childnode.tag == 'argument' and childnode.getparent() is parent_node:
            arg_num += 1
        if arg_num > 2:
            break
        if not flag_lambda and childnode.tag == "literal" and childnode.attrib.get('type') == "string":
            c_py_sub_list.append(childnode.text[1:-1])
        if not flag_lambda and childnode.tag == "name":
            c_name = childnode.text

        if not flag_lambda and childnode.tag == "lambda":
            flag_lambda = True
            len_lambda = 0
            c_py_sub_list.append("lambda expression")
            continue
        if childnode.tag == 'comment':
            continue
        if flag_lambda and childnode.text != None:
            if childnode.text.strip() in ('(', '{', '['):
                len_lambda = len_lambda + 1

            len_lambda = len_lambda + len(childnode.text.strip()) - childnode.text.count(' ')
    if flag_lambda:
        c_py_sub_list.append(node.sourceline - 1)
        c_py_sub_list.append(int(len_lambda))
    else:
        c_py_sub_list.append(c_name)
        c_py_sub_list.append(node.sourceline - 1)
        c_py_sub_list.append(None)

    c_py_fun_list.append(c_py_sub_list)

for ele in c_py_fun_list:
    print(ele)