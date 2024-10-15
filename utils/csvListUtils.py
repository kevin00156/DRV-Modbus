import csv
import ast
"""
這是以List做讀寫csv，並以List管理數據的功能
"""

def writeListToCsv(data, filePath):
    ret = False
    if not data or not isinstance(data, dict):
        return ret

    with open(filePath, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["key", "value"])  # 寫入標題行

        for key, value in data.items():
            writer.writerow([key, str(value)])

    ret = True
    return ret


def readListFromCsv(filePath):
    data = {}
    
    with open(filePath, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # 跳過標題行

        for row in reader:
            if len(row) == 2:
                key, value_str = row
                try:
                    # 使用 ast.literal_eval 安全地評估字符串
                    value = ast.literal_eval(value_str)
                    if isinstance(value, tuple):
                        value = list(value)  # 將元組轉換為列表
                    data[key] = value
                except (ValueError, SyntaxError):
                    # 如果無法評估，則保留原始字符串
                    data[key] = value_str

    return data

"""
# 使用函數的例子
if __name__ == "__main__":
    # 寫入示例
    test_data = {
        "key1": [1, 2, 3],
        "key2": ["string1", "string2", "string3", "string4"],
        "key3": [1.23, 4.56]
    }
    writeListToCsv(test_data, "test_output.csv")

    # 讀取示例
    read_data = readListFromCsv("test_output.csv")
    print("讀取的數據：")
    for key, value in read_data.items():
        print(f"{key}: {value}")
"""