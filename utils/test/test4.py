import re

if __name__ == '__main__':
    line="""
   
    import options,sequence,tuple, union
    """
    match1 = re.findall("import(.*)as", line,re.M)
    match2 = re.findall("import(.*)",line,re.M)[0]
    list = match2.split(",")
    if list:
        print(list)
    if match1:
        print(match1[0])