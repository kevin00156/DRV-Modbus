import utils

"""
這個檔案用來寫入位置姿態到csv
"""

positions = {#根據需要自行增加 或直接改csv檔案就可以了
    'home': [424.863, 0.328, 663.11, 178.333, -0.679, -111.784]#,
    #'pick': [424.863, 0.328, 663.11, 178.333, -0.679, -111.784],
    #'place': [424.863, 0.328, 663.11, 178.333, -0.679, -111.784],
}

utils.csvListUtils.writeListToCsv(positions, "examples/datas/positions.csv")
