## 简介

DEGA： 使用双编码方法，优化多无人机多任务协调分配系统。

## 特性

- 特性一：多任务
- 特性二：多无人机
- 特性三：多目标

## 安装与提交

提供安装该项目的步骤。以下是一个示例步骤：

1. 初始化环境：
   ```bash
   git init
   git config --global user.name "gaomn"
   git config --global user.email "gaom@mail.nankai.edu.cn"
   ```
   
2. 克隆该仓库：
   ```bash
   git clone https://github.com/gaomn/MPDA_GA.git
   ```
3. 进入项目目录：
   ```bash
   cd MPDA_GA
   ```
4. 添加远程仓库：
   ```bash
   git remote add origin https://github.com/gaomn/MPDA_GA.git
   ```
5. 提交更改：
   ```bash
   git add .
   git commit -m 'Add some foo'
   ```
6. 推送到远程仓库：
   ```bash
   git push origin main
   ```

## 帮助
1. 安装anaconda, vscode, git:
   ```bash
   anaconda: https://www.anaconda.com/products/individual
   vscode: https://code.visualstudio.com/download
   git: https://git-scm.com/downloads
   ```

2. terminal激活conda环境显示：
   ```bash
   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
   ```
   注意：运行该命令后，需要重启powershell。


3. conda相关：
   ```bash
   conda create -n mpda python=3.8
   conda activate mpda
   ```
   
4. pip安装：
   ```bash
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```

## 贡献

如果有其他人希望对该项目进行贡献，可以提供贡献的指南。例如：

1. Fork 该仓库。
2. 创建你的特性分支：
   ```bash
   git checkout -b feature-foo
   ```
3. 提交更改：
   ```bash
   git commit -m 'Add some foo'
   ```
4. 推送到分支：
   ```bash
   git push origin feature-foo
   ```
5. 提交 Pull Request。

## 许可证

无。

