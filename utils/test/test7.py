import pandas as pd
from lxml import etree
from pylibsrcml import srcml

# srcml.srcml("F:\\python_workplace\\pytorch-master\\torch\\csrc\\Generator.cpp","Generator.cpp.xml")
path="F:\\python_workplace\\pytorch-master\\tools\\autograd\\templates\\python_nested_functions.cpp"
path2="F:\\python_workplace\\check_utils\\utils\\xml_files\\torch\\csrc\\Module.cpp.xml"
path3="F:\\python_workplace\\pytorch-master\\tools\\autograd\\templates\\python_return_types.cpp"
path4="F:\\DLFs_dataset\\mindspore\\mindspore-1.10.1\\mindspore\\ccsrc\\pybind_api\\ir\\dtype_py.cc"
# srcml.srcml(path4,"dtype_py.cc.xml")
# parser = etree.HTMLParser(encoding="utf-8")
# e=etree.parse(path2,parser)
# nodes=e.xpath("//decl_stmt/decl[type//name[last()]=\'PyModuleDef\']")
# for node in nodes:
#     module_name=node.find("init/expr/block/expr[2]/literal")
#     if module_name is not None:
#         print(module_name.text)
#     methods_table=node.find("init/expr/block/expr[5]/name")
#     if methods_table is not None and methods_table.text!="NULL":
#         print(methods_table.text)
#     else:
#         print("asdsadsa")


# path10="F:\\python_workplace\\check_utils\\utils\\python_c\\mindspore\\mindspore-1.10.1\\c_py_fun_table.csv"
# files_results=pd.read_csv(path10).values
# after_handle=files_results[:,0]
# print(len(after_handle))
arr=[1,2,3]
print(arr[:0])