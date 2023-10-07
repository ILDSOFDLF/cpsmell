import re

import numpy as np
from pylibsrcml import srcml

# str="F:\\python_workplace\\mindspore-master\\mindspore\\core\\mindspore\\ops\\apply_momentum.cc"
# frame_name="mindspore"
# file_name="apply_momentum.cc"
# ans=re.findall("\\\\{}\\\\(.*)\\\\{}".format(frame_name,file_name),str)
# if ans:
#     print(ans[0])
# else:print("match failed")
list1=[[1,23,412],[31,52,12]]
list2=np.array(list1)[:,2].flatten()
print(list2)