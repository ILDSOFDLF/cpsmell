from lxml import etree
from pylibsrcml import srcml

parser = etree.HTMLParser(encoding="utf-8")
src_path="F:\\DLFs_dataset\\chainer\\chainer-7.8.1\\chainerx_cc\\chainerx\\python\context.cc"
# path="F:\\python_workplace\\cpsmell\\utils\\xml_files\\tensorflow\\compiler\\xla\\python\\xla.cc.xml"
path="context.cc.xml"
srcml.srcml(src_path,path)
code_smell_list=[]
class_name = "CompiledMemoryStats"
lineno = 54

e = etree.parse(path, parser)
nodes = e.xpath(
    "//expr_stmt/expr[call/name/name[last()]=\'class_\']|//decl_stmt/decl[type/name/name[last()]=\'class_\']")
for node in nodes:
    print(node.sourceline)
    if node.sourceline - 1 != lineno:
        continue
    alias_list = node.find('name')
    extra = 0
    if alias_list is not None and alias_list.text is not None:
        alias_name = alias_list.text
        alias_line = alias_list.sourceline - 1
        indir_nodes = e.xpath("//expr_stmt/expr[call/name/name=\'{}\']".format(alias_name))
        first_nodes = e.xpath("//expr_stmt/expr/call[name[name[1]=\'{}\' and name[2][contains(text(),\"def\")]]]".format(alias_name))
        for indir_node in indir_nodes:
            if indir_node.sourceline - 1 - alias_line < 3:
                node = indir_node
                break
        if len(first_nodes) != 0:
            for first_node in first_nodes:
                first_name=first_node.find('argument_list/argument[1]/expr/literal')
                if first_name is not None:
                    print("pre=",first_name.text)
                    first_name = first_name.text[1:-1]
                    print(first_name)
                    if first_name.startswith('__') and first_name.endswith('__'):
                        continue
                    else:
                        extra = extra+1

    fun_names = node.xpath("descendant::call[name[contains(text(),\"def\")]]/argument_list/argument[1]/expr/literal")
    index = 0
    while index < len(fun_names):
        fun_name = fun_names[index].text[1:-1]
        print(fun_name)
        if fun_name.startswith("__") and fun_name.endswith("__"):
            print(fun_names.pop(index))
            print(len(fun_names))
            continue
        index = index + 1
    print(len(fun_names) + extra)
    if len(fun_names) + extra > 7:
        code_smell_list.append([path, class_name, lineno])
    break
for a in code_smell_list:
    print(a)



# print("__str__".startswith("__") and "__str__".endswith("__"))