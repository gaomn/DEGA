# DEGA: 基于双编码的多无人机任务分配遗传算法

[English](./README_EN.md) | 中文

---

### 📖 项目简介

本仓库包含了**DEGA（双编码遗传算法）**的实现，这是一种专为消防场景下多无人机任务分配设计的新型多目标优化算法。该算法采用双编码策略，将路径规划和任务分配分离，以高效解决复杂的多目标优化问题。

### 🎯 核心特性

- **🚁 多无人机协调**: 支持多架无人机的协同作业
- **🎯 多任务分配**: 智能分配和调度多个任务
- **🎯 多目标优化**: 同时优化执行时间和飞行距离
- **🧬 双编码策略**: 分离路径编码(R)和分配编码(X)
- **🔄 多种算法**: 支持DEGA、ILS、MSGA等多种优化算法
- **📊 可视化**: 全面的结果可视化和分析工具

### 🏗️ 仓库结构

```text
DEGA/
├── main.py                           # 主程序入口
├── visualize_results.py              # 结果可视化工具
├── requirements.txt                  # Python依赖包
├── README.md                         # 本文件（中文）
├── README_EN.md                      # 英文文档
├── A_Dual-Encoding-based_...pdf      # 研究论文
├── AllInstance/                      # 测试实例数据集
│   ├── S_*.txt                      # 小规模实例 (≤30任务)
│   ├── M_*.txt                      # 中规模实例 (30-50任务)
│   └── L_*.txt                      # 大规模实例 (>50任务)
├── DEGA/                            # 双编码遗传算法
├── ILS/                             # 迭代局部搜索
├── MSGA/                            # 多目标遗传算法
├── CACS/                            # 协作蚁群系统
├── MSDE_SPEA2/                      # 多目标差分进化
└── utils/                           # 工具模块
```

### 🚀 快速开始

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

### 📊 算法对比

| 算法 | 类型 | 特点 | 适用场景 |
|------|------|------|----------|
| **DEGA** | 遗传算法 | 双编码，多目标 | 主要算法（推荐） |
| **ILS** | 局部搜索 | 快速收敛 | 快速求解 |
| **MSGA** | 遗传算法 | 传统多目标GA | 基准对比 |
| **CACS** | 蚁群算法 | 协作机制 | 研究对比 |
| **MSDE_SPEA2** | 差分进化 | SPEA2选择 | 高质量解 |

### 📈 测试实例

仓库包含50+个不同规模的基准测试实例：

- **S_**: 小规模 (≤30任务) - 快速测试和算法验证
- **M_**: 中规模 (30-50任务) - 标准测试场景
- **L_**: 大规模 (>50任务) - 性能压力测试

实例命名格式: `{规模}_{无人机数}_{任务数}_{难度系数}.txt`

### 🎛️ 参数说明

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

### 📚 引用

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

### 🤝 贡献

我们欢迎贡献！请随时提交问题和拉取请求。

1. Fork 本仓库
2. 创建特性分支: `git checkout -b feature/new-feature`
3. 提交更改: `git commit -m 'Add new feature'`
4. 推送到分支: `git push origin feature/new-feature`
5. 提交拉取请求

### 📄 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件。

### 📧 联系方式

- **作者**: 高猛 (Gao Meng)
- **邮箱**: [gaom@mail.nankai.edu.cn](mailto:gaom@mail.nankai.edu.cn)
- **GitHub**: [https://github.com/gaomn/DEGA](https://github.com/gaomn/DEGA)

---

**⭐ 如果这个项目对您有帮助，请给我们一个星标！**
