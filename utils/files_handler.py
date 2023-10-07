
import re
import os

from pylibsrcml import srcml
import pandas as pd

from utils import astChecker
from utils.customast import parse_file
from utils.version_management import DFLs_version, Frame_names

# frame_names=['tensorflow','pytorch','mindspore','Paddle','chainer']
def write_files(path,frame_name,file_name):
    postfixs = (".c", ".cpp", ".cc", ".h", ".py")
    c_files_list = []
    py_files_list = []
    for dirpaths, dirnames, fs in os.walk(path):
        for f in fs:
            if len(path)+1<len(dirpaths):
                index=len(path)+1
                if dirpaths[index]=='.' or dirpaths[index:index+4] in ["cmake","venv"]:
                    continue
            for postfix in postfixs:
                if f.endswith(postfix):
                    if postfix == ".py":
                        py_files_list.append(os.path.join(dirpaths, f))
                    else:
                        c_files_list.append(os.path.join(dirpaths, f))

    c_df = pd.DataFrame(c_files_list)
    c_df.to_csv(os.path.join("c_files",frame_name,file_name+"_c_files.csv"),header=False,index=False)

    py_df = pd.DataFrame(py_files_list)
    py_df.to_csv(os.path.join("py_files",frame_name,file_name + "_py_files.csv"), header=False, index=False)


def read_py_files(frame_name,frame_version):
    path = os.path.join("py_files",frame_name,frame_version + "_py_files.csv")
    if os.path.exists(path):
        py_files = pd.read_csv(path,header=None).values.flatten()
    else:
        print("the path of file is not exist--->",path)
    return py_files


def parse_file_to_ast(py_path):
    file_name = py_path[py_path.rfind("\\") + 1:]

    myast = astChecker.MyAst()
    myast.fileName = file_name
    try:
        astContent = parse_file(py_path)
    except Exception as e:
        print(py_path)
        print(e)
        return False
    myast.visit(astContent)
    return myast


def code_toXML(frame_name):

    # Setup options and attributes
    srcml.set_version("211")
    srcml.set_tabstop(4)

    # Treat ".h" ,".cc" as C++
    srcml.register_file_extension("h", srcml.SRCML_LANGUAGE_CXX)
    srcml.register_file_extension("cc",srcml.SRCML_LANGUAGE_CXX)

    c_path = "c_files\\" + frame_name + "_c_files.csv"

    if os.path.exists(c_path):
        c_files = pd.read_csv(c_path,header=None).values.flatten()
    else:
        print("the path of file is not exist--->",c_path)

    xml_path="xml_files\\"+frame_name
    if not os.path.exists(xml_path):
        os.mkdir(xml_path)

    sum = len(c_files)
    index = 0
    count=0
    print(sum)
    for item in c_files:
        index=item.rfind("\\")
        file_name = item[index + 1:]
        str=re.findall("\\\\{}\\\\(.*)\\\\{}".format(frame_name,file_name),item)

        if str:
            dir_name=str[0]
            dir_path = os.path.join(xml_path, dir_name)
        else:
            dir_path=xml_path
        print(dir_path)


        if not os.path.exists(dir_path):
            os.makedirs(dir_path)


        dest_path=os.path.join(dir_path, file_name + '.xml')

        count=count+1
        srcml.srcml(item, dest_path)


    print(count)








# def zip_files():
#     zipf = zipfile.ZipFile(output_filename, 'w')




if __name__ == '__main__':
    # frame_names=['Paddle-develop','mindspore-master','tensorflow-master','pytorch-master','chainer-master']
    # frames_names=['Paddle','mindspore','tensorflow','pytorch','chainer']
    for frame_name in Frame_names:
        c_files_path=os.path.join("c_files",frame_name)
        py_files_path=os.path.join("py_files",frame_name)
        if not os.path.exists(c_files_path):
            os.makedirs(c_files_path)
        if not os.path.exists(py_files_path):
            os.makedirs(py_files_path)

    for i in range(len(DFLs_version)):
        for path in DFLs_version[i]:
            file_name=path[path.find('\\')+1:]
            write_files(path,Frame_names[i],file_name)
    #code_toXML("torch")
    #print(parse_c_files("tensorflow", QUERY_MOUDLE_NAME))
