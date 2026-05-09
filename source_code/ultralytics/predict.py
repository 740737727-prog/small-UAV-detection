import os

def count_elements_in_txt_files(folder_path):
    total_element_count = 0  # 用于存储总元素数
    all_lists = []  # 用于存储每个文件的内容列表

    # 遍历指定文件夹下的所有文件
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):  # 确保只处理 .txt 文件
            file_path = os.path.join(folder_path, filename)  # 获取文件的完整路径
            with open(file_path, 'r', encoding='utf-8') as file:  # 打开文件
                file_content = file.read().strip()  # 读取文件内容并去除首尾空白字符
                if file_content:  # 如果文件内容不为空
                    file_list = file_content.splitlines()  # 按行分割为列表
                    all_lists.append(file_list)  # 将列表添加到总列表中
                    total_element_count += len(file_list)  # 累加元素数

    return total_element_count, all_lists  # 返回总元素数和所有列表

# 示例用法
folder_path = "E:/ultralytics-main/ultralytics/runs/detect/predict25/labels"  # 替换为你的文件夹路径
total_count, all_file_lists = count_elements_in_txt_files(folder_path)
print(f"总元素数: {total_count}")
#print("所有文件内容列表:", all_file_lists)





