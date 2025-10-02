# DEGA: 基于双编码的多无人机任务分配遗传算法

[English](./README_EN.md) | 中文

---

### 项目简介

本仓库包含了DEGA（Dual-Encoding Genetic Algorithm，双编码遗传算法）的实现代码，这是一种针对消防场景下多无人机多任务调度问题的多目标优化算法。该算法采用双编码策略，将路径规划编码（R编码）和任务分配编码（X编码）分离，以有效求解具有多个冲突目标的复杂调度问题。

### 算法特点

本算法针对消防场景中的多无人机任务分配问题，同时优化任务完成时间和飞行距离两个目标。算法采用双编码遗传算法框架，其中：

- 路径编码（R）：采用排列编码表示任务执行顺序
- 分配编码（X）：采用二进制矩阵编码表示无人机与任务的分配关系
- 双编码策略：将路径规划和任务分配解耦，提高算法搜索效率
- 多目标优化：基于Pareto支配关系进行解的评估和选择

### 仓库结构

```text
DEGA/
├── main.py                           # 主程序入口
├── visualize_results.py              # 结果可视化工具
├── requirements.txt                  # Python依赖包
├── README.md                         # 本文件（中文）
├── README_EN.md                      # 英文文档
├── DEGA.pdf                          # 研究论文（预览版）
├── AllInstance/                      # 测试实例数据集
│   ├── S_*.txt                      # 小规模实例
│   ├── M_*.txt                      # 中规模实例
│   └── L_*.txt                      # 大规模实例
├── DEGA/                            # 双编码遗传算法实现
├── ILS/                             # 迭代局部搜索算法实现
├── MSGA/                            # 多目标遗传算法实现
├── CACS/                            # 协作蚁群算法实现
├── MSDE_SPEA2/                      # 多目标差分进化算法实现
└── utils/                           # 工具模块
```

### 快速开始

#### 环境要求

- Python 3.8+
- 所需包: numpy, matplotlib, pandas, deap, pymoo, tqdm

#### 安装

```bash
git clone https://github.com/gaomn/DEGA.git
cd DEGA
pip install -r requirements.txt
```

#### 基本使用

```bash
# 使用默认DEGA算法运行小实例
python main.py --method DEGA --instance S_5_4_0.39

# 运行所有小规模实例
python main.py --method DEGA --scale small

# 启用并行处理
python main.py --method DEGA --scale medium --parallel --num_runs 5

# 比较不同算法
python main.py --method ILS --instance M_15_30_2.16
python main.py --method MSGA --instance M_15_30_2.16
```

#### 可视化

```bash
# 生成路径可视化图
python visualize_results.py
```

### 对比算法

本仓库实现了论文中使用的对比算法，用于验证DEGA算法的性能：

| 算法 | 全称 | 说明 |
|------|------|------|
| **DEGA** | Dual-Encoding Genetic Algorithm | 本文提出的双编码遗传算法 |
| **ILS** | Iterated Local Search | 迭代局部搜索算法 |
| **MSGA** | Multi-objective Genetic Algorithm | 多目标遗传算法 |
| **CACS** | Cooperative Ant Colony System | 协作蚁群系统 |
| **MSDE_SPEA2** | Multi-objective Differential Evolution with SPEA2 | 基于SPEA2的多目标差分进化算法 |

**注意**: ACACO（Adaptive Cooperative Ant Colony Optimization）算法的官方实现由原论文作者提供，本仓库未包含该算法的实现代码。如需使用ACACO算法进行对比实验，请参考其原始论文获取官方代码。

### 测试实例

本仓库包含50余个不同规模的测试实例，用于算法性能评估：

- **S_**: 小规模实例（任务数≤30）
- **M_**: 中规模实例（任务数30-50）
- **L_**: 大规模实例（任务数>50）

实例文件命名格式: `{规模}_{无人机数}_{任务数}_{难度系数}.txt`

### 参数说明

#### 算法选择

- `--method`: 选择算法 (`DEGA`, `ILS`, `MSGA`, `CACS`, `MSDE_SPEA2`)

#### 实例选择

- `--instance`: 指定单个实例 (如 `S_5_4_0.39`)
- `--scale`: 选择规模 (`small`, `medium`, `large`, `all`)

#### 算法参数

- `--generations`: 进化代数 (默认: 200)
- `--pop_size`: 种群大小 (默认: 100)
- `--cross_rate`: 交叉概率 (默认: 0.9)
- `--mutate_rate`: 变异概率 (默认: 0.1)

#### 执行控制

- `--num_runs`: 每个实例运行次数 (默认: 1)
- `--parallel`: 启用并行处理
- `--seed`: 随机种子 (默认: 123)

### 论文引用

本仓库包含的DEGA.pdf为论文预览版，可能存在错误。正式发表版本请访问：[https://ieeexplore.ieee.org/abstract/document/11043008](https://ieeexplore.ieee.org/abstract/document/11043008)

如果您在研究中使用了本代码，请引用我们的论文：

```bibtex
@inproceedings{gao2025dual,
  title={A Dual-Encoding-based Genetic Algorithm for Multi-Objective Multi-UAV Scheduling in Firefighting Scenarios},
  author={Gao, M. and Liu, X. and Zhan, Z. and Zhang, J.},
  booktitle={2025 IEEE Congress on Evolutionary Computation (CEC)},
  pages={1--4},
  year={2025},
  address={Hangzhou, China},
  doi={10.1109/CEC65147.2025.11043008}
}
```

### 贡献

我们欢迎贡献！请随时提交问题和拉取请求。

1. Fork 本仓库
2. 创建特性分支: `git checkout -b feature/new-feature`
3. 提交更改: `git commit -m 'Add new feature'`
4. 推送到分支: `git push origin feature/new-feature`
5. 提交拉取请求

### 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件。

### 联系方式

- **作者**: 高猛 (Gao Meng)
- **邮箱**: [gaom@mail.nankai.edu.cn](mailto:gaom@mail.nankai.edu.cn)
- **GitHub**: [https://github.com/gaomn/DEGA](https://github.com/gaomn/DEGA)

---

如果本项目对您的研究有所帮助，欢迎给予星标支持。
