<!--
 * @Author       : Tianzw
 * @Date         : 2021-03-26 12:12:17
 * @LastEditors  : Please set LastEditors
 * @LastEditTime : 2021-03-26 12:32:12
 * @FilePath     : /my_github/NUMPY/pandas 的复制问题.md
-->
```python
import numpy as np
import pandas as pd

arr = np.random.normal(10, 10, (4, 3))

df = pd.DataFrame(arr, columns = ['a', 'b', 'c'])

def test(df):
    df.iloc[0, 0] = 1

test(df)    # 原地修改 df

df          # df 发生了修改

arr         # 对应地，arr 也发生了修改


arr[0, 1] = -1  # 修改 arr，df 也同时发生修改
df


id(df.values) # 创建新对象，但是其值由 arr 保存

id(df.values) # 每一次运行，结果都不同，说明 df.values 创建了新的对象

id(df) is id(df.iloc[:, :]), id(df) == id(df.iloc[:, :])
# (False, True)

arr.flags.owndata, df.values.flags.owndata
# (True, False)
# 故：df.values 的值，由 arr 保存。df 只是在 arr 的基础上，做了一层包装而已。
```
1. 函数参数，**传递的是原始对象**，故在函数内部修改对象，是原地修改
2. `df = pd.DataFrame(data)` 构造的新对象，其值由 data 对象拥有。
