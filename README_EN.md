# DEGA: Dual-Encoding Genetic Algorithm for Multi-UAV Task Assignment

English | [中文](./README.md)

---

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

```text
DEGA/
├── main.py                           # Main program entry point
├── visualize_results.py              # Result visualization tool
├── requirements.txt                  # Python dependencies
├── README.md                         # Chinese documentation
├── README_EN.md                      # This file (English)
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
python main.py --method DEGA --instance S_5_4_0.39

# Run on all small-scale instances
python main.py --method DEGA --scale small

# Enable parallel processing
python main.py --method DEGA --scale medium --parallel --num_runs 5

# Compare different algorithms
python main.py --method ILS --instance M_15_30_2.16
python main.py --method MSGA --instance M_15_30_2.16
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

- `--generations`: Number of generations (default: 200)
- `--pop_size`: Population size (default: 100)
- `--cross_rate`: Crossover probability (default: 0.9)
- `--mutate_rate`: Mutation probability (default: 0.1)

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

- **Author**: Gao Meng (高猛)
- **Email**: [gaom@mail.nankai.edu.cn](mailto:gaom@mail.nankai.edu.cn)
- **GitHub**: [https://github.com/gaomn/DEGA](https://github.com/gaomn/DEGA)

---

**⭐ If this project helps you, please give us a star!**
