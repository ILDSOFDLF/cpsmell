from lxml import etree
from pylibsrcml import srcml

from utils.srcml_parse import SrcML_Parser

#srcml.srcml("dim.cpp","dim.cpp.xml")
QUERY_METHODS_TABLE="//decl_stmt/decl[type[name=\'PyMethodDef\']]|//decl_stmt/decl[type[name[name[last()]=\'PyMethodDef\']]]"

def getPyMethodDef(self):
    SrcML_Parser().read_c_files(self.frame_name)
    for path in SrcML_Parser().c_files:
        archive = SrcML_Parser().parse_c_files(path)
        list = etree.XML(archive.srcML().encode(), self.parser).xpath(QUERY_METHODS_TABLE)
parser = etree.HTMLParser(encoding="utf-8")

e=etree.parse('F:\\python_workplace\\check_utils\\utils\\test\\python_variable_methods.cpp.xml',parser)
root=e.getroot()

py_c_fun_list=[]

for node in e.xpath(QUERY_METHODS_TABLE):

    methods_table=node.find("name")
    if methods_table.text is None:
        methods_table=node.find("name/name")

    print(methods_table.text)
    blocks=node.findall("init/expr/block/expr/block")

    if len(blocks) == 0:
        py_fun = node.find("init/expr/block/expr[1]/literal")
        if py_fun is None or py_fun.text is None:
            continue
        c_fun = node.find("init/expr/block/expr[2]/name[last()]")
        if c_fun is None or c_fun.text is None:
            name_list = block.findall("init/expr/block/expr[2]//name")
            if len(name_list) > 0:
                c_fun = name_list[-1]
            else:
                continue
        if c_fun is None:
            continue
        print(py_fun.text)
        print(c_fun.text)
        sub_py_c_fun_list = []
        sub_py_c_fun_list.append(py_fun.text[1:-1])
        sub_py_c_fun_list.append(c_fun.text)
        sub_py_c_fun_list.append(py_fun.sourceline - 1)
        sub_py_c_fun_list.append(methods_table.text)


        py_c_fun_list.append(sub_py_c_fun_list)
    else:
        for block in blocks:
            sub_py_c_fun_list = []
            py_fun = block.find("expr[1]/literal")
            if py_fun is None or py_fun.text is None:
                continue
            c_fun = block.find("expr[2]/name[last()]")

            if c_fun is None or c_fun.text is None:
                print("-------------------------------------")
                name_list = block.findall("expr[2]//name")
                if len(name_list) > 0:
                    c_fun = name_list[-1]
                else:
                    continue
            if c_fun is None:
                continue
            print(py_fun.text)
            print(c_fun.text)
            sub_py_c_fun_list.append(py_fun.text[1:-1])
            sub_py_c_fun_list.append(c_fun.text)
            sub_py_c_fun_list.append(py_fun.sourceline - 1)
            sub_py_c_fun_list.append(methods_table.text)

            py_c_fun_list.append(sub_py_c_fun_list)

for res in py_c_fun_list:
    print(res)
print(len(py_c_fun_list))








