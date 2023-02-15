import pandas as pd
import matplotlib.pyplot as plt

"""axis2 = ['0.00', '78834.99', '157669.99', '236504.98', '315339.98', '394174.97', '473009.96', '551844.96', '630679.95', '709514.95', '788349.94', '867184.93', '946019.93', '1024854.92',
               '1103689.91', '1182524.91', '1261359.90', '1340194.90', '1419029.89', '1497864.88', '1576699.88', '1655534.87', '1734369.87', '1813204.86', '1892039.85', '1970874.85', '2049709.84',
               '2128544.84', '2207379.83', '2286214.82', '2365049.82', '2443884.81', '2522719.80', '2601554.80', '2680389.79', '2759224.79', '2838059.78', '2916894.77', '2995729.77', '3074564.76',
               '3153399.76', '3232234.75', '3311069.74', '3389904.74', '3468739.73', '3547574.73', '3626409.72', '3705244.71', '3784079.71', '3862914.70', '3941749.70', '4020584.69', '4099419.68',
               '4178254.68', '4257089.67', '4335924.66', '4414759.66', '4493594.65', '4572429.65', '4651264.64', '4730099.63', '4808934.63', '4887769.62', '4966604.62', '5045439.61', '5124274.60',
               '5203109.60', '5281944.59', '5360779.59', '5439614.58', '5518449.57', '5597284.57', '5676119.56', '5754954.56', '5833789.55', '5912624.54', '5991459.54', '6070294.53', '6149129.52',
               '6227964.52', '6306799.51', '6385634.51', '6464469.50', '6543304.49', '6622139.49', '6700974.48', '6779809.48', '6858644.47', '6937479.46', '7016314.46', '7095149.45', '7173984.45',
               '7252819.44', '7331654.43', '7410489.43', '7489324.42', '7568159.41', '7646994.41', '7725829.40', '7804664.40', '7883499.39', '7962334.38', '8041169.38', '8120004.37', '8198839.37',
               '8277674.36', '8356509.35', '8435344.35', '8514179.34', '8593014.34', '8671849.33', '8750684.32', '8829519.32', '8908354.31', '8987189.31', '9066024.30', '9144859.29', '9223694.29',
               '9302529.28', '9381364.27', '9460199.27', '9539034.26', '9617869.26', '9696704.25', '9775539.24', '9854374.24', '9933209.23', '10012044.23', '10090879.22', '10169714.21', '10248549.21',
               '10327384.20', '10406219.20', '10485054.19', '10563889.18', '10642724.18', '10721559.17', '10800394.16', '10879229.16', '10958064.15', '11036899.15', '11115734.14', '11194569.13',
               '11273404.13', '11352239.12', '11431074.12', '11509909.11', '11588744.10', '11667579.10', '11746414.09', '11825249.09', '11904084.08', '11982919.07', '12061754.07', '12140589.06',
               '12219424.06', '12298259.05', '12377094.04', '12455929.04', '12534764.03', '12613599.02', '12692434.02', '12771269.01', '12850104.01', '12928939.00', '13007773.99', '13086608.99',
               '13165443.98', '13244278.98', '13323113.97', '13401948.96', '13480783.96', '13559618.95', '13638453.95', '13717288.94', '13796123.93', '13874958.93', '13953793.92', '14032628.92',
               '14111463.91', '14190298.90', '14269133.90', '14347968.89', '14426803.88', '14505638.88', '14584473.87', '14663308.87', '14742143.86', '14820978.85', '14899813.85', '14978648.84',
               '15057483.84', '15136318.83', '15215153.82', '15293988.82', '15372823.81', '15451658.81', '15530493.80', '15609328.79', '15688163.79', '15766998.78', '15845833.77', '15924668.77',
               '16003503.76', '16082338.76', '16161173.75', '16240008.74', '16318843.74', '16397678.73', '16476513.73', '16555348.72', '16634183.71', '16713018.71', '16791853.70', '16870688.70',
               '16949523.69', '17028358.68', '17107193.68', '17186028.67', '17264863.67', '17343698.66', '17422533.65', '17501368.65', '17580203.64', '17659038.63', '17737873.63', '17816708.62',
               '17895543.62', '17974378.61', '18053213.60', '18132048.60', '18210883.59', '18289718.59', '18368553.58', '18447388.57', '18526223.57', '18605058.56', '18683893.56', '18762728.55',
               '18841563.54', '18920398.54', '18999233.53', '19078068.53', '19156903.52', '19235738.51', '19314573.51', '19393408.50', '19472243.49', '19551078.49', '19629913.48', '19708748.48',
               '19787583.47', '19866418.46', '19945253.46', '20024088.45', '20102923.45', '20181758.44', '20260593.43', '20339428.43', '20418263.42', '20497098.42', '20575933.41', '20654768.40',
               '20733603.40', '20812438.39', '20891273.38', '20970108.38', '21048943.37', '21127778.37', '21206613.36', '21285448.35', '21364283.35', '21443118.34', '21521953.34', '21600788.33']"""
df = pd.DataFrame(pd.read_excel('D:\\Users\\user\\Documents\\Programming\\matic_chgvol.xlsx'))  # INPUT: file
axis1 = [float(df.iat[x, 0]) for x in range(275)]  # INPUT: uniform length
axis2 = [float(df.iat[275, x + 1]) for x in range(275)]

fig = plt.figure()
ax = plt.axes(projection='3d')
x = [x1 for x1 in axis1 for x2 in
     range(len(axis2))]  # for each index of axis2, there will be len(axis1) indexes of {axis1[axis2.index]}
y = [item for sublist in [[float(x2) for x2 in axis2] for x1 in range(len(axis1))] for item in
     sublist]  # for ea index of axis1, there will be {axis1} indexes in order
z = [float(df.iat[x1, x2 + 1]) for x1 in range(len(axis1)) for x2 in range(len(axis2))]

ax.bar3d([x1 for x1 in range(len(axis1)) for x2 in range(len(axis2))],
         [item for sublist in [[x1 for x1 in range(len(axis2))] for x2 in range(len(axis1))] for item in sublist],
         [0 for x1 in range(len(z))],
         [1 for x1 in range(len(x))],
         [1 for x1 in range(len(y))],
         z, color='b', shade=True)
plt.show()
