import os
import random


def process_text_files(insConfDir, savepath, random_seed=None):
    # 设置随机种子
    if random_seed is not None:
        random.seed(random_seed)

    # 确保保存目录存在
    os.makedirs(savepath, exist_ok=True)

    # 遍历初始目录中的所有文件
    for filename in os.listdir(insConfDir):
        if filename.endswith('.txt'):
            filepath = os.path.join(insConfDir, filename)
            # 读取文件内容
            with open(filepath, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            # 在文件内容末尾添加一行零
            if lines:
                cl = lines[-4].strip().split()
                for line in lines:
                    if len(line.strip().split()) > 0 and line.strip().split()[0] == 'task_x':
                        cl = line.strip().split()
                        break

                add_line = 'task_value_rate ' + ' '.join(str(random.random()) for _ in range(len(cl) - 1))
                lines.append(add_line)

            # 将修改后的内容保存到保存路径目录中的新文件中
            new_filepath = os.path.join(savepath, filename)
            with open(new_filepath, 'w', encoding='utf-8') as file:
                file.writelines(lines)


if __name__ == '__main__':
    # 设置随机种子
    random_seed = 42

    # 运行函数
    process_text_files('.//staticMpdaBenchmarkSet//', './/newInstance//', random_seed)

# 示例用法
# process_text_files('.//staticMpdaBenchmarkSet//', './/newInstance//')

# 注意：取消注释示例用法行以在需要时运行函数一次。
