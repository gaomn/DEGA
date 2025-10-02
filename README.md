# DEGA: A Dual-Encoding-based Genetic Algorithm for Multi-UAV Scheduling

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![IEEE CEC 2025](https://img.shields.io/badge/IEEE%20CEC-2025-green.svg)](https://ieeexplore.ieee.org/abstract/document/11043008)

[English](./README_EN.md) | 中文

---

## 📖 项目简介

本仓库是论文 **"A Dual-Encoding-based Genetic Algorithm for Multi-Objective Multi-UAV Scheduling in Firefighting Scenarios"** 的官方实现代码。

该算法针对消防场景下的多无人机多任务调度问题，提出了一种基于双编码策略的遗传算法（DEGA）。算法将任务序列编码（R编码）和任务分配编码（X编码）解耦，能够有效求解具有多个冲突目标的复杂调度问题。

### 🎯 核心特性

- **双编码策略**：
  - **R编码**：排列编码，表示全局任务执行顺序
  - **X编码**：二进制矩阵编码，表示无人机与任务的分配关系

- **多目标优化**：同时优化任务完成时间（makespan）和总飞行距离

- **离散事件仿真**：精确模拟消防场景中的火势增长和灭火过程

- **NSGA-II框架**：基于Pareto支配关系进行解的评估和选择

## 📁 仓库结构

```text
DEGA/
├── main.py                           # 主程序入口
├── visualize_results.py              # 结果可视化工具
├── requirements.txt                  # Python依赖包
├── README.md                         # 中文文档
├── README_EN.md                      # 英文文档
├── LICENSE                           # MIT许可证
├── DEGA.pdf                          # 论文预览版
├── AllInstance/                      # 测试实例数据集（50个实例）
│   ├── S_*.txt                      # 小规模实例（23个）
│   ├── M_*.txt                      # 中规模实例（10个）
│   └── L_*.txt                      # 大规模实例（17个）
├── DEGA/                            # DEGA算法实现
│   ├── run.py                       # 主算法逻辑
│   └── utils.py                     # 评估函数和工具
├── ILS/                             # ILS对比算法
│   ├── run.py
│   └── evalute.py
├── MSGA/                            # MSGA对比算法
│   └── run.py
├── CACS/                            # CACS对比算法
│   ├── run.py
│   └── utils.py
└── utils/                           # 公共工具模块
    ├── mpdaInstance.py              # 问题实例加载
    ├── readcfg.py                   # 配置文件读取
    └── read_task.py                 # 任务数据读取
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 依赖包: `numpy`, `matplotlib`, `pandas`, `deap`, `pymoo`, `tqdm`

### 安装

```bash
git clone https://github.com/gaomn/DEGA.git
cd DEGA
pip install -r requirements.txt
```

### 基本使用

```bash
# 使用DEGA算法运行单个实例
python main.py --method DEGA --instance S_5_4_0.39

# 运行所有小规模实例
python main.py --method DEGA --scale small

# 启用并行处理，运行5次
python main.py --method DEGA --scale medium --parallel --num_runs 5

# 使用对比算法
python main.py --method ILS --instance M_15_30_2.16
python main.py --method MSGA --instance M_15_30_2.16
python main.py --method CACS --instance M_15_30_2.16
```

### 结果可视化

```bash
# 生成无人机路径可视化图
python visualize_results.py --results_dir ./results --output_dir ./figures
```

## 🔬 算法实现

### 主算法：DEGA

**DEGA (Dual-Encoding-based Genetic Algorithm)** 是本文提出的双编码遗传算法，核心创新点包括：

- **双编码表示**：R编码（任务序列）+ X编码（任务分配矩阵）
- **多样化交叉算子**：18种交叉策略组合
- **双层局部搜索**：针对R编码和X编码的独立局部搜索
- **NSGA-II选择**：基于非支配排序的环境选择

### 对比算法

为验证DEGA的性能，本仓库实现了以下对比算法：

| 算法 | 全称 | 类型 | 说明 |
|------|------|------|------|
| **DEGA** | Dual-Encoding-based Genetic Algorithm | 遗传算法 | 本文提出的算法 |
| **ILS** | Iterated Local Search | 局部搜索 | 经典迭代局部搜索 |
| **MSGA** | Multi-Strategy Genetic Algorithm | 遗传算法 | 多策略遗传算法 |
| **CACS** | Cooperative Ant Colony System | 蚁群算法 | 协作蚁群系统 |

## 📊 测试实例

本仓库包含 **50个** 不同规模的测试实例，用于算法性能评估：

| 规模 | 前缀 | 数量 | 无人机数 | 任务数 | 说明 |
|------|------|------|----------|--------|------|
| 小规模 | `S_` | 23个 | 3-30 | 4-40 | 快速测试 |
| 中规模 | `M_` | 10个 | 15-40 | 10-30 | 中等难度 |
| 大规模 | `L_` | 17个 | 20-120 | 15-120 | 高难度挑战 |

**实例命名格式**: `{规模}_{无人机数}_{任务数}_{难度系数}.txt`

**示例**: `S_5_4_0.39` 表示小规模实例，5架无人机，4个任务，难度系数0.39

## ⚙️ 参数说明

### 命令行参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--method` | str | `DEGA` | 算法选择：`DEGA`, `ILS`, `MSGA`, `CACS` |
| `--instance` | str | None | 指定单个实例，如 `S_5_4_0.39` |
| `--scale` | str | `small` | 批量运行规模：`small`, `medium`, `large`, `all` |
| `--generations` | int | 200 | 进化代数 |
| `--pop_size` | int | 100 | 种群大小 |
| `--cross_rate` | float | 0.9 | 交叉概率 |
| `--mutate_rate` | float | 0.1 | 变异概率 |
| `--num_runs` | int | 1 | 每个实例运行次数 |
| `--parallel` | flag | False | 启用多进程并行计算 |
| `--seed` | int | 123 | 随机种子 |
| `--output_dir` | str | `./results` | 结果输出目录 |
| `--instance_dir` | str | `./AllInstance` | 实例文件目录 |

### 使用示例

```bash
# 基础运行
python main.py --method DEGA --instance S_5_4_0.39

# 自定义参数
python main.py --method DEGA --instance M_20_20_0.58 \
    --generations 300 --pop_size 150 --cross_rate 0.85

# 批量运行并行计算
python main.py --method DEGA --scale all --parallel --num_runs 10

# 对比不同算法
for method in DEGA ILS MSGA CACS; do
    python main.py --method $method --scale small
done
```

## 📝 论文引用

本仓库是以下论文的官方实现：

> **Gao, M., Liu, X., Zhan, Z., & Zhang, J.** (2025). A Dual-Encoding-based Genetic Algorithm for Multi-Objective Multi-UAV Scheduling in Firefighting Scenarios. *2025 IEEE Congress on Evolutionary Computation (CEC)*, 1-4. Hangzhou, China.
> DOI: [10.1109/CEC65147.2025.11043008](https://doi.org/10.1109/CEC65147.2025.11043008)

**注意**: 本仓库包含的 `DEGA.pdf` 为论文预览版，正式版本请访问 [IEEE Xplore](https://ieeexplore.ieee.org/abstract/document/11043008)。

### BibTeX

如果您在研究中使用了本代码，请引用我们的论文：

```bibtex
@inproceedings{gao2025dual,
  title     = {A Dual-Encoding-based Genetic Algorithm for Multi-Objective Multi-UAV Scheduling in Firefighting Scenarios},
  author    = {Gao, Meng and Liu, Xin and Zhan, Zhi-Hui and Zhang, Jun},
  booktitle = {2025 IEEE Congress on Evolutionary Computation (CEC)},
  pages     = {1--4},
  year      = {2025},
  address   = {Hangzhou, China},
  doi       = {10.1109/CEC65147.2025.11043008}
}
```

## 🤝 贡献指南

我们欢迎任何形式的贡献！包括但不限于：

- 🐛 报告Bug
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交代码修复

### 贡献流程

1. Fork 本仓库
2. 创建特性分支: `git checkout -b feature/AmazingFeature`
3. 提交更改: `git commit -m 'Add some AmazingFeature'`
4. 推送到分支: `git push origin feature/AmazingFeature`
5. 提交 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 📧 联系方式

- **作者**: 高猛 (Gao Meng)
- **单位**: 南开大学 (Nankai University)
- **邮箱**: [gaom@mail.nankai.edu.cn](mailto:gaom@mail.nankai.edu.cn)
- **GitHub**: [@gaomn](https://github.com/gaomn)

---

<div align="center">

**如果本项目对您的研究有所帮助，欢迎给予 ⭐ Star 支持！**

**[⬆ 回到顶部](#dega-a-dual-encoding-based-genetic-algorithm-for-multi-uav-scheduling)**

Made with ❤️ by [Gao Meng](https://github.com/gaomn)

</div>
