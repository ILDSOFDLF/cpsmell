import clang.cindex
from clang.cindex import Index  #主要API
from clang.cindex import Config  #配置
from clang.cindex import CursorKind  #索引结点的类别
from clang.cindex import TypeKind    #节点的语义类别


def preorder_travers_AST(cursor):
    for cur in cursor.get_children():
        #do something
        print(cur.spelling)
        preorder_travers_AST(cur)

if __name__ == '__main__':
    libclangPath=r'/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/libclang.dylib'
    if Config.loaded == True:
        print("Config.loaded == True:")
        # pass
    else:
        Config.set_library_file(libclangPath)
        print("install path")




    file_path = r"guards.cpp"
    index = Index.create()

    tu = index.parse(file_path)
    AST_root_node= tu.cursor  #cursor根节点
    print(AST_root_node)

    for token in AST_root_node.get_tokens():
        print(f'{token.spelling}"------"{token.kind}')

    #preorder_travers_AST(AST_root_node)

