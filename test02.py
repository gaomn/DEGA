import os
import shutil

def copy_all_jsonl_files(parent_folder, destination_folder):
    """
    遍历父文件夹中的所有子文件夹，将每个子文件夹中的 JSONL 文件复制到目标文件夹。

    :param parent_folder: 父文件夹路径
    :param destination_folder: 目标文件夹路径
    """
    # 如果目标文件夹不存在，则创建
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # 遍历父文件夹的所有子文件夹
    for root, dirs, files in os.walk(parent_folder):
        for file in files:
            if file.endswith(".jsonl"):  # 筛选 .jsonl 文件
                source_path = os.path.join(root, file)
                destination_path = os.path.join(destination_folder, file)

                # 复制文件
                shutil.copy(source_path, destination_path)
                print(f"Copied: {source_path} -> {destination_path}")

if __name__ == "__main__":
    # 示例文件夹路径
    parent_folder = "./data_DEGA/20241227_182438"  # 替换为包含子文件夹的父文件夹路径
    destination_folder = "./collected_jsonl"  # 替换为目标文件夹路径

    copy_all_jsonl_files(parent_folder, destination_folder)

# if __name__ == "__main__":
#     # 示例文件夹路径
#     parent_folder = "./data_DEGA/20241227_182438"  # 替换为包含子文件夹的父文件夹路径
#     destination_folder = "./plot_data/DEGA"  # 替换为目标文件夹路径

#     copy_all_json_files(parent_folder, destination_folder)