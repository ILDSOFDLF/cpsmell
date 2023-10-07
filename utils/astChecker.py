import ast,_ast
import re
import astunparse
# import yaml

# stream = open("config",'r')
# config = yaml.load(stream)
library_list=["cdll", "CDLL", "LoadLibrary", "windll", "WinDLL"]
class MyAst(ast.NodeVisitor):
    def __init__(self,call_module=None):
        self.fileName = None
        self.call_names = set()
        self.call_module = call_module
        self.component = set()
        self.imports = set()
        self.constant=set()
        self.load_cdll=set()
        self.if_interval = [-1, -1]

    def count_lines(self,node):
        childnodes = list(ast.walk(node))
        lines = set()
        for n in childnodes:
          if hasattr(n,'lineno'):
            lines.add(n.lineno)
        return len(lines)

    def visit_If(self, node):
        if node.end_lineno>self.if_interval[1]:
            self.if_interval=[node.lineno,node.end_lineno]
        self.generic_visit(node)

    def visit_Call(self,node):
        f = node.func
        if isinstance(f, _ast.Name) and f.id is not None:
            self.call_names.add((f.id, f.lineno))
            if f.id in library_list:
                self.load_cdll.add((f.id,node.lineno,self.if_interval[0]))
        self.generic_visit(node)

    def visit_For(self,node):

        self.generic_visit(node)

    def visit_While(self, node):
        self.generic_visit(node)

    def visit_Constant(self, node):
        str1 = node.value
        if isinstance(str1, str) and len(str1) < 100:
            self.constant.add((str1, node.lineno))

        self.generic_visit(node)

    def visit_Attribute(self,node):
        v = node.value
        if isinstance(v, _ast.Attribute):
            attr_node = v.value
            if self.call_module is not None:
                if isinstance(attr_node, _ast.Name) and attr_node.id == self.call_module:
                    print("-----------------------")
                    print(v.attr)
                    if v.attr is not None:
                        self.component.add((v.attr, node.attr,node.lineno))
            else:
                if isinstance(attr_node, _ast.Name) and v.attr is not None:
                    self.component.add((attr_node.id,attr_node.lineno))
                    self.component.add((v.attr, node.lineno))
                    self.component.add((node.attr, node.lineno))
        else:
            self.component.add((node.attr, node.lineno))
        if node.attr in library_list:
            if node.lineno < self.if_interval[0] or node.lineno > self.if_interval[1]:
                self.load_cdll.add((node.attr, node.lineno, 0))
            else:
                self.load_cdll.add((node.attr, node.lineno, self.if_interval[0]))

        if isinstance(v, _ast.Name):
            if self.call_module is not None:
                if v.id == self.call_module:
                    print("===========================")
                    print(node.attr)
                    self.component.add((node.attr,node.lineno))
            else:
                self.component.add((v.id,v.lineno))
                self.component.add((node.attr, node.lineno))
        self.generic_visit(node)

    def visit_Import(self,node):
        for alias in node.names:
            if alias.name != '*':
                for (name,asname,file,lineno) in self.imports:
                    if name==alias.name and asname==alias.asname and self.fileName==file:
                        break
                else:
                    index=alias.name.rfind('.')
                    if index!=-1:
                        alias.name=alias.name[index+1:]

                    self.imports.add((alias.name,alias.asname,self.fileName,node.lineno))
        self.generic_visit(node)

    def visit_ImportFrom(self,node):
        if node.module is not None:
            index=node.module.rfind('.')
            if index!=-1:
                node.module=node.module[index+1:]
            self.imports.add((node.module,None,self.fileName,node.lineno))

        for alias in node.names:

            if alias.name != '*':
                for (name, asname, file, lineno) in self.imports:
                    if name == alias.name and asname == alias.asname and self.fileName == file:
                        break
                else:
                    self.imports.add((alias.name, alias.asname, self.fileName, node.lineno))

        self.generic_visit(node)

if __name__ == '__main__':
    pass