# DEGA: Dual-Encoding Genetic Algorithm for Multi-UAV Task Assignment

[English](#english) | [中文](#中文)

---

## English

### 📖 Overview

This repository contains the implementation of **DEGA (Dual-Encoding Genetic Algorithm)**, a novel multi-objective optimization algorithm designed for multi-UAV task assignment in firefighting scenarios. The algorithm employs a dual-encoding strategy that separates route planning and task allocation to efficiently solve complex multi-objective optimization problems.

### 🎯 Key Features

- **🚁 Multi-UAV Coordination**: Supports coordinated operations of multiple unmanned aerial vehicles
- **🎯 Multi-Task Assignment**: Intelligent allocation and scheduling of multiple tasks
- **🎯 Multi-Objective Optimization**: Simultaneously optimizes execution time and flight distance
- **🧬 Dual-Encoding Strategy**: Separates route encoding (R) and allocation encoding (X)
- **🔄 Multiple Algorithms**: Supports DEGA, ILS, MSGA, and other optimization algorithms
- **📊 Visualization**: Comprehensive result visualization and analysis tools

### 🏗️ Repository Structure

```
DEGA/
├── main.py                           # Main program entry point
├── visualize_results.py              # Result visualization tool
├── requirements.txt                  # Python dependencies
├── README.md                         # This file
├── A_Dual-Encoding-based_...pdf      # Research paper
├── AllInstance/                      # Test instance dataset
│   ├── S_*.txt                      # Small-scale instances (≤30 tasks)
│   ├── M_*.txt                      # Medium-scale instances (30-50 tasks)
│   └── L_*.txt                      # Large-scale instances (>50 tasks)
├── DEGA/                            # Dual-Encoding Genetic Algorithm
├── ILS/                             # Iterated Local Search
├── MSGA/                            # Multi-objective Genetic Algorithm
├── CACS/                            # Cooperative Ant Colony System
├── MSDE_SPEA2/                      # Multi-objective Differential Evolution
└── utils/                           # Utility modules
```

### 🚀 Quick Start

#### Prerequisites
- Python 3.8+
- Required packages: numpy, matplotlib, pandas, deap, pymoo, tqdm

#### Installation
```bash
git clone https://github.com/gaomn/DEGA.git
cd DEGA
pip install -r requirements.txt
```

#### Basic Usage
```bash
# Run with default DEGA algorithm on a small instance
python main.py --method DEGA --instance S_5_4_0.39 --generations 100

# Run on all small-scale instances
python main.py --method DEGA --scale small --generations 200

# Enable parallel processing
python main.py --method DEGA --scale medium --parallel --num_runs 5

# Compare different algorithms
python main.py --method ILS --instance M_15_30_2.16 --generations 200
python main.py --method MSGA --instance M_15_30_2.16 --generations 200
```

#### Visualization
```bash
# Generate path visualization plots
python visualize_results.py
```

### 📊 Algorithm Comparison

| Algorithm | Type | Features | Use Case |
|-----------|------|----------|----------|
| **DEGA** | Genetic Algorithm | Dual-encoding, multi-objective | Main algorithm (recommended) |
| **ILS** | Local Search | Fast convergence | Quick solutions |
| **MSGA** | Genetic Algorithm | Traditional multi-objective GA | Baseline comparison |
| **CACS** | Ant Colony | Cooperative mechanism | Research comparison |
| **MSDE_SPEA2** | Differential Evolution | SPEA2 selection | High-quality solutions |

### 📈 Test Instances

The repository includes 50+ benchmark instances with different scales:

- **S_**: Small-scale (≤30 tasks) - Quick testing and algorithm validation
- **M_**: Medium-scale (30-50 tasks) - Standard testing scenarios  
- **L_**: Large-scale (>50 tasks) - Performance stress testing

Instance naming format: `{Scale}_{UAVs}_{Tasks}_{Difficulty}.txt`

### 🎛️ Parameters

#### Algorithm Selection
- `--method`: Choose algorithm (`DEGA`, `ILS`, `MSGA`, `CACS`, `MSDE_SPEA2`)

#### Instance Selection  
- `--instance`: Specify single instance (e.g., `S_5_4_0.39`)
- `--scale`: Choose scale (`small`, `medium`, `large`, `all`)

#### Algorithm Parameters
- `--generations`: Number of generations (default: 50)
- `--pop_size`: Population size (default: 50)
- `--cross_rate`: Crossover probability (default: 0.8)
- `--mutate_rate`: Mutation probability (default: 0.05)

#### Execution Control
- `--num_runs`: Number of runs per instance (default: 1)
- `--parallel`: Enable parallel processing
- `--seed`: Random seed (default: 123)

### 📚 Citation

If you use this code in your research, please cite our paper:

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

### 🤝 Contributing

We welcome contributions! Please feel free to submit issues and pull requests.

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/new-feature`
3. Commit your changes: `git commit -m 'Add new feature'`
4. Push to the branch: `git push origin feature/new-feature`
5. Submit a pull request

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### 📧 Contact

- **Author**: Gao Mingnan
- **Email**: gaom@mail.nankai.edu.cn
- **GitHub**: https://github.com/gaomn/DEGA.git

---

## 中文

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

```
DEGA/
├── main.py                           # 主程序入口
├── visualize_results.py              # 结果可视化工具
├── requirements.txt                  # Python依赖包
├── README.md                         # 本文件
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
python main.py --method DEGA --instance S_5_4_0.39 --generations 100

# 运行所有小规模实例
python main.py --method DEGA --scale small --generations 200

# 启用并行处理
python main.py --method DEGA --scale medium --parallel --num_runs 5

# 比较不同算法
python main.py --method ILS --instance M_15_30_2.16 --generations 200
python main.py --method MSGA --instance M_15_30_2.16 --generations 200
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
- `--generations`: 进化代数 (默认: 50)
- `--pop_size`: 种群大小 (默认: 50)
- `--cross_rate`: 交叉概率 (默认: 0.8)
- `--mutate_rate`: 变异概率 (默认: 0.05)

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

- **作者**: 高明南
- **邮箱**: gaom@mail.nankai.edu.cn
- **GitHub**: https://github.com/gaomn/DEGA.git

---

**⭐ 如果这个项目对您有帮助，请给我们一个星标！**