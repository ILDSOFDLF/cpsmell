import re

import numpy
import numpy as np
import pandas as pd
#
# if __name__ == '__main__':
#     s="m.def(\"ExperimentalRunPassPipeline\", [](const std::string &mlir_txt, const std::string &pass_pipeline,\",return output;\"});"
#     print(type(s))
#     s=re.split(",",s)[0]
#     print(re.findall("m.def\(\"(.*)\"",s)[0])
# print("DSDJ234545_ADSA".isupper())
# t=set()
# t.add(("Format","AFDIDJ"))
# t.add("asdsad")
# for item in t:
#     if len(item)>1:
#         print(item[0])
my_words=["this is a word"]
list=[["gsfdsf","code smell",None,None]]
pd.DataFrame(my_words).to_csv('test.csv',index=False,header=False)
pd.DataFrame(list,columns=['a','b','c','d']).to_csv('test.csv',mode='a',index=False)