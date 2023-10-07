import importlib
import re
import sys
import difflib
import os
import ctypes

import parsel as parsel
from pylibsrcml import srcml
from lxml import etree
import xml.etree.ElementTree as ET
# Setup options and attributes
# srcml.set_version("211")
# srcml.set_tabstop(4)
#
# # Treat ".h" as C++
# srcml.register_file_extension("h", srcml.SRCML_LANGUAGE_CXX)
# srcml.register_file_extension("cc",srcml.SRCML_LANGUAGE_CXX)
#
# # Change prefix of standard namespace
# srcml.register_namespace("s", "http://www.sdml.info/srcML/src")
#
# # Default prefix is now for cpp namespace
#
#
# # New prefix for further processing
# srcml.register_namespace("doc", "http://www.sdml.info/srcML/doc")
#
# # Translates source code file "main.cpp" to srcML file "main.cpp.xml".
# # - Translate using the above global options
# # - The language will be automatically based on the extension of the input (first) filename
# # - Since there is only a single input file, the output file will be a non-archive by default.
# # Convenience function can also convert to archive
# srcml.srcml("main.cpp", "main.cpp.xml")
# srcml.srcml("tfe_wrapper.cc","tfe_wrapper.cc.xml")
# srcml.srcml("constants.h","constants.h.xml")
# srcml.srcml("c_test.c","c_test.c.xml")
QUERY_PY_FUNCTION = "//expr_stmt/expr/call[name[name[1]=\'m\' and operator=\'.\' and name[2]=\'def\']]/argument_list/argument[1]/expr/literal/text()"
if __name__ == '__main__':
    name_space={'xmlns':'cpp=\"http://www.srcML.org/srcML/cpp\"','xmlns':'s=\"http://www.sdml.info/srcML/src\"','xmlns':'doc=\"http://www.sdml.info/srcML/doc\"'}
    parser = etree.HTMLParser(encoding="utf-8")
    str="""
    <comment>lalallalalal</comment>
    """
    path1='//function/name/text()'
    # tree = ET.parse('c_test.c.xml')
    # root = tree.getroot()
    # for child in root:
    #     print(child.tag, child.attrib)
    # lines=open('c_test.c.xml','r').read()
    # data=parsel.Selector(lines).xpath(path).extract()
    # print(data)
    # result=data.xpath(path).extract()
    # print(result)
    # for movie in root.xpath('./function/name/text()'):
    #     print(movie)
    print(type(str))
    print(etree.XML(str).xpath('/comment/text()'))
    e=etree.parse('tfe_wrapper.cc.xml',parser)
    # root=e.getroot()
    # print(root)
    # for item in e.xpath(path1):
    #     print(item)

    path2='//macro[name=\'PYBIND11_MODULE\']/argument_list/argument[1]/text()'
    path3="//expr_stmt/expr/call[name[name[1]=\'m\' and operator=\'.\' and name[2]=\'def\']]/child::argument_list"
    path4=""
    path5="//expr_stmt/expr/call[name[name[last()]=\'class_\']]"
    path6="//decl_stmt/decl[type[name[name[last()]=\'class_\']]]"
    # for item in e.xpath(path3):
    #     print(item)
    root=e.getroot()
    c_py_list=[]
    # for node in e.xpath(path5):
    #     #print(node)
    #     c_py_sub_list=[]
    #     flag_lambda=False
    #     arg_num=0
    #     parent_node=node
    #     c_class=node.find('name/argument_list/argument/expr/name').text
    #
    #     if not c_class:
    #         c_class=node.find('name/argument_list/argument/expr/name/name[last()]').text
    #     print(c_class)
    #     print(node.find('argument_list/argument[2]/expr/literal').text[1:-1])
        # for childnode in node.iter():
        #     print(childnode.tag)

    for node in e.xpath(path6):
        #print(node)
        c_py_sub_list=[]
        flag_lambda=False
        arg_num=0
        parent_node=node
        c_class2=node.find('type/name/argument_list/argument/expr/name').text
        if not c_class2:
            c_class2 = node.find('type/name/argument_list/argument/expr/name/name[last()]').text
        print(c_class2)
        print(node.find('argument_list/argument[2]/expr/literal').text[1:-1])
        # print(node.find('argument_list/argument[last()]/expr/literal').text[1:-1])
    #     for childnode in node.iter():
    #         print(childnode.tag)


    #     for childnode in node.iter():
    #         # print(childnode.tag)
    #
    #         if childnode.tag=='argument' and childnode.getparent() is parent_node:
    #             arg_num+=1
    #         if not flag_lambda and arg_num>2:
    #             break
    #         if not flag_lambda and childnode.tag=="literal" and childnode.attrib.get('type')=="string":
    #             c_py_sub_list.append(childnode.text[1:-1])
    #         if not flag_lambda and childnode.tag=="name":
    #             c_name=childnode.text
    #
    #
    #         if not flag_lambda and childnode.tag=="lambda":
    #             flag_lambda=True
    #             len_lambda = 0
    #             c_py_sub_list.append("lambda expression")
    #             continue
    #         if childnode.tag=='comment':
    #             continue
    #         if flag_lambda and childnode.text != None:
    #             if childnode.text.strip() in ('(','{','['):
    #                 len_lambda=len_lambda+1
    #
    #             len_lambda=len_lambda+len(childnode.text.strip())-childnode.text.count(' ')
    #     if flag_lambda:
    #         c_py_sub_list.append(len_lambda)
    #     else:
    #         c_py_sub_list.append(c_name)
    #         c_py_sub_list.append(None)
    #
    #     c_py_list.append(c_py_sub_list)
    #
    # for ele in c_py_list:
    #     print(ele)



    # tree = etree.parse('c_test.c.xml')  # 将xml解析为树结构
    # print(tree)
    # ans=tree.xpath(path)
    # print(ans)
    # root = tree.getroot()  # 获得该树的树根
    # print(root)
    # for elments in root:
    #     for key in elments.attrib.keys():
    #         print(key, ":", elments.get(key))
    # for name in tree.find('/comment'):
    #     print(name)
    # print(tree)

    #
    #
    # ele=tree.xpath(path)
    # print(len(ele))

   # etree.XML("c_test.c.xml")


