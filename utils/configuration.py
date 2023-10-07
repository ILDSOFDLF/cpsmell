XML_Line_Shifting=3
Lambda_MAX_Char=80
Max_Function_Num=7
Max_Call_Sum_Count=5
IGNORE_KEYWORDS=["numpy","type","name","int","range","item","dim","dims","size",
                 "split","float","stack","index","long","index","bool","double"]

import os

# 定义权限模式: 读+写+执行权限给文件所有者, 只读+执行权限给组和其他用户
mode = 0o755
def setp():
# 使用chmod改变文件权限
    os.chmod('find_api.py', mode)
    os.chmod('detect_smells.py',mode)
