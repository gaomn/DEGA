# DEGA: A Dual-Encoding-based Genetic Algorithm for Multi-UAV Scheduling

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![IEEE CEC 2025](https://img.shields.io/badge/IEEE%20CEC-2025-green.svg)](https://ieeexplore.ieee.org/abstract/document/11043008)

English | [中文](./README.md)

---

## 📖 Overview

This repository is the official implementation of the paper **"A Dual-Encoding-based Genetic Algorithm for Multi-Objective Multi-UAV Scheduling in Firefighting Scenarios"**.

The algorithm addresses the multi-UAV multi-task scheduling problem in firefighting scenarios by proposing a Dual-Encoding-based Genetic Algorithm (DEGA). The algorithm decouples task sequence encoding (R-encoding) and task allocation encoding (X-encoding) to effectively solve complex scheduling problems with multiple conflicting objectives.

### 🎯 Key Features

- **Dual-Encoding Strategy**:
  - **R-encoding**: Permutation encoding for global task execution order
  - **X-encoding**: Binary matrix encoding for UAV-task assignments

- **Multi-Objective Optimization**: Simultaneously optimizes task completion time (makespan) and total flight distance

- **Discrete Event Simulation**: Accurately simulates fire growth and firefighting processes

- **NSGA-II Framework**: Solution evaluation and selection based on Pareto dominance relations

## 📁 Repository Structure

```text
DEGA/
├── main.py                           # Main program entry
├── visualize_results.py              # Visualization tool
├── requirements.txt                  # Python dependencies
├── README.md                         # Chinese documentation
├── README_EN.md                      # English documentation
├── LICENSE                           # MIT License
├── DEGA.pdf                          # Paper preview
├── AllInstance/                      # Test instances (50 instances)
│   ├── S_*.txt                      # Small-scale (23 instances)
│   ├── M_*.txt                      # Medium-scale (10 instances)
│   └── L_*.txt                      # Large-scale (17 instances)
├── DEGA/                            # DEGA algorithm
│   ├── run.py                       # Main algorithm logic
│   └── utils.py                     # Evaluation functions
├── ILS/                             # ILS comparison algorithm
│   ├── run.py
│   └── evalute.py
├── MSGA/                            # MSGA comparison algorithm
│   └── run.py
├── CACS/                            # CACS comparison algorithm
│   ├── run.py
│   └── utils.py
└── utils/                           # Common utilities
    ├── mpdaInstance.py              # Instance loader
    ├── readcfg.py                   # Config reader
    └── read_task.py                 # Task data reader
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Dependencies: `numpy`, `matplotlib`, `pandas`, `deap`, `pymoo`, `tqdm`

### Installation

```bash
git clone https://github.com/gaomn/DEGA.git
cd DEGA
pip install -r requirements.txt
```

### Basic Usage

```bash
# Run DEGA on a single instance
python main.py --method DEGA --instance S_5_4_0.39

# Run on all small-scale instances
python main.py --method DEGA --scale small

# Enable parallel processing with 5 runs
python main.py --method DEGA --scale medium --parallel --num_runs 5

# Compare with other algorithms
python main.py --method ILS --instance M_15_30_2.16
python main.py --method MSGA --instance M_15_30_2.16
python main.py --method CACS --instance M_15_30_2.16
```

### Visualization

```bash
# Generate UAV path visualization
python visualize_results.py --results_dir ./results --output_dir ./figures
```

## 🔬 Algorithm Implementation

### Main Algorithm: DEGA

**DEGA (Dual-Encoding-based Genetic Algorithm)** is the proposed algorithm with the following innovations:

- **Dual-Encoding Representation**: R-encoding (task sequence) + X-encoding (task allocation matrix)
- **Diversified Crossover Operators**: 18 crossover strategy combinations
- **Two-Level Local Search**: Independent local search for R-encoding and X-encoding
- **NSGA-II Selection**: Environmental selection based on non-dominated sorting

### Comparison Algorithms

To validate DEGA's performance, this repository implements the following comparison algorithms:

| Algorithm | Full Name | Type | Description |
|-----------|-----------|------|-------------|
| **DEGA** | Dual-Encoding-based Genetic Algorithm | Genetic Algorithm | Proposed algorithm |
| **ILS** | Iterated Local Search | Local Search | Classic iterated local search |
| **MSGA** | Multi-Strategy Genetic Algorithm | Genetic Algorithm | Multi-strategy GA |
| **CACS** | Cooperative Ant Colony System | Ant Colony | Cooperative ACO |

## 📊 Test Instances

This repository contains **50** test instances of different scales for algorithm evaluation:

| Scale | Prefix | Count | UAVs | Tasks | Description |
|-------|--------|-------|------|-------|-------------|
| Small | `S_` | 23 | 3-30 | 4-40 | Quick testing |
| Medium | `M_` | 10 | 15-40 | 10-30 | Moderate difficulty |
| Large | `L_` | 17 | 20-120 | 15-120 | High difficulty |

**Naming Format**: `{Scale}_{UAVs}_{Tasks}_{Difficulty}.txt`

**Example**: `S_5_4_0.39` represents a small-scale instance with 5 UAVs, 4 tasks, and difficulty coefficient 0.39

## ⚙️ Parameters

### Command-Line Arguments

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--method` | str | `DEGA` | Algorithm: `DEGA`, `ILS`, `MSGA`, `CACS` |
| `--instance` | str | None | Single instance, e.g., `S_5_4_0.39` |
| `--scale` | str | `small` | Batch scale: `small`, `medium`, `large`, `all` |
| `--generations` | int | 200 | Number of generations |
| `--pop_size` | int | 100 | Population size |
| `--cross_rate` | float | 0.9 | Crossover probability |
| `--mutate_rate` | float | 0.1 | Mutation probability |
| `--num_runs` | int | 1 | Runs per instance |
| `--parallel` | flag | False | Enable multiprocessing |
| `--seed` | int | 123 | Random seed |
| `--output_dir` | str | `./results` | Output directory |
| `--instance_dir` | str | `./AllInstance` | Instance directory |

### Usage Examples

```bash
# Basic run
python main.py --method DEGA --instance S_5_4_0.39

# Custom parameters
python main.py --method DEGA --instance M_20_20_0.58 \
    --generations 300 --pop_size 150 --cross_rate 0.85

# Batch run with parallel processing
python main.py --method DEGA --scale all --parallel --num_runs 10

# Compare different algorithms
for method in DEGA ILS MSGA CACS; do
    python main.py --method $method --scale small
done
```

## 📝 Citation

This repository is the official implementation of the following paper:

> **Gao, M., Liu, X., Zhan, Z., & Zhang, J.** (2025). A Dual-Encoding-based Genetic Algorithm for Multi-Objective Multi-UAV Scheduling in Firefighting Scenarios. *2025 IEEE Congress on Evolutionary Computation (CEC)*, 1-4. Hangzhou, China.
> DOI: [10.1109/CEC65147.2025.11043008](https://doi.org/10.1109/CEC65147.2025.11043008)

**Note**: The `DEGA.pdf` included in this repository is a preview version. For the official version, please visit [IEEE Xplore](https://ieeexplore.ieee.org/abstract/document/11043008).

### BibTeX

If you use this code in your research, please cite our paper:

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

## 🤝 Contributing

We welcome all forms of contributions, including but not limited to:

- 🐛 Bug reports
- 💡 Feature suggestions
- 📝 Documentation improvements
- 🔧 Code fixes

### Contribution Workflow

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/AmazingFeature`
3. Commit your changes: `git commit -m 'Add some AmazingFeature'`
4. Push to the branch: `git push origin feature/AmazingFeature`
5. Submit a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

- **Author**: Gao Meng (高猛)
- **Affiliation**: Nankai University (南开大学)
- **Email**: [gaom@mail.nankai.edu.cn](mailto:gaom@mail.nankai.edu.cn)
- **GitHub**: [@gaomn](https://github.com/gaomn)

---

<div align="center">

**If this project helps your research, please consider giving it a ⭐ Star!**

**[⬆ Back to Top](#dega-a-dual-encoding-based-genetic-algorithm-for-multi-uav-scheduling)**

Made with ❤️ by [Gao Meng](https://github.com/gaomn)

</div>
