import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pconst import const

newl, file = '\n', pd.read_csv("D:\\Users\\user\\Documents\\Programming\\matic_trading_data.csv") # INPUT
const.dim = file.shape[1] - 1
arr3d = np.array([
   [[float(file.iat[row_i + block_i * (1 + (const.dim)), col_i + 1]) for col_i in range(const.dim)] for row_i in range(const.dim)] for block_i in range(const.dim) #set range by counting how many times "pr level" appears
])
print(f"arr assigned, dims: {arr3d.shape}")
del file

x_src, y_src, z_src, x, y, z, vals = np.linspace(-0.17327, 0.3552, const.dim), np.linspace(0, 456523834, const.dim), np.linspace(0.01174, 2.56919, const.dim), [], [], [], []

for row_ii in range(const.dim ** 2):
   level_i = int((row_ii - (row_mod := row_ii % const.dim)) / const.dim)
   
   try:
      vals += list(arr3d[level_i, row_mod, :][[filter_obj := list(filter(lambda y2: arr3d[level_i, row_mod, y2] != 0, range(const.dim)))]])
      y += list(y_src[[filter_obj]])
      z += [z_src[level_i] for x in range(len(filter_obj))]
      x += [x_src[row_mod] for x2 in range(len(filter_obj))]
      
      if row_mod == 274:
         print(f"matrix #{level_i} done, at {row_ii / const.dim ** 2 * 100}%")
   
   except IndexError as err:
      print(f"ERROR {err}{newl}i_cnt: {row_ii}, calculated x: {row_mod}, calculated z: {level_i}")

fig, axes = plt.figure(), plt.axes(projection='3d')
axes.scatter(x, y, z, c='g')
plt.show()