# DEGA: Dual-Encoding Genetic Algorithm for Multi-UAV Task Assignment

English | [中文](./README.md)

---

### Overview

This repository contains the implementation of DEGA (Dual-Encoding Genetic Algorithm), a multi-objective optimization algorithm for multi-UAV multi-task scheduling in firefighting scenarios. The algorithm employs a dual-encoding strategy that decouples route planning encoding (R-encoding) and task allocation encoding (X-encoding) to effectively solve complex scheduling problems with multiple conflicting objectives.

### Algorithm Features

The algorithm addresses the multi-UAV task assignment problem in firefighting scenarios, simultaneously optimizing two objectives: task completion time and flight distance. The algorithm is based on a dual-encoding genetic algorithm framework, where:

- Route Encoding (R): Uses permutation encoding to represent task execution order
- Allocation Encoding (X): Uses binary matrix encoding to represent UAV-task assignments
- Dual-Encoding Strategy: Decouples route planning and task allocation to improve search efficiency
- Multi-Objective Optimization: Evaluates and selects solutions based on Pareto dominance relations

### Repository Structure

```text
DEGA/
├── main.py                           # Main program entry point
├── visualize_results.py              # Result visualization tool
├── requirements.txt                  # Python dependencies
├── README.md                         # Chinese documentation
├── README_EN.md                      # This file (English)
├── DEGA.pdf                          # Research paper (preview version)
├── AllInstance/                      # Test instance dataset
│   ├── S_*.txt                      # Small-scale instances
│   ├── M_*.txt                      # Medium-scale instances
│   └── L_*.txt                      # Large-scale instances
├── DEGA/                            # DEGA implementation
├── ILS/                             # ILS implementation
├── MSGA/                            # MSGA implementation
├── CACS/                            # CACS implementation
├── MSDE_SPEA2/                      # MSDE_SPEA2 implementation
└── utils/                           # Utility modules
```

### Quick Start

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

### Comparison Algorithms

This repository implements the comparison algorithms used in the paper to validate the performance of DEGA:

| Algorithm | Full Name | Description |
|-----------|-----------|-------------|
| **DEGA** | Dual-Encoding Genetic Algorithm | The proposed dual-encoding genetic algorithm |
| **ILS** | Iterated Local Search | Iterated local search algorithm |
| **MSGA** | Multi-objective Genetic Algorithm | Multi-objective genetic algorithm |
| **CACS** | Cooperative Ant Colony System | Cooperative ant colony system |
| **MSDE_SPEA2** | Multi-objective Differential Evolution with SPEA2 | Multi-objective differential evolution with SPEA2 |

**Note**: The official implementation of ACACO (Adaptive Cooperative Ant Colony Optimization) is provided by the original paper authors and is not included in this repository. For comparison experiments with ACACO, please refer to the original paper for the official code.

### Test Instances

This repository contains over 50 test instances of different scales for algorithm performance evaluation:

- **S_**: Small-scale instances (tasks ≤ 30)
- **M_**: Medium-scale instances (tasks 30-50)
- **L_**: Large-scale instances (tasks > 50)

Instance file naming format: `{Scale}_{UAVs}_{Tasks}_{Difficulty}.txt`

### Parameters

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

### Citation

The DEGA.pdf included in this repository is a preview version and may contain errors. For the official published version, please visit: [https://ieeexplore.ieee.org/abstract/document/11043008](https://ieeexplore.ieee.org/abstract/document/11043008)

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

### Contributing

We welcome contributions! Please feel free to submit issues and pull requests.

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/new-feature`
3. Commit your changes: `git commit -m 'Add new feature'`
4. Push to the branch: `git push origin feature/new-feature`
5. Submit a pull request

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Contact

- **Author**: Gao Meng (高猛)
- **Email**: [gaom@mail.nankai.edu.cn](mailto:gaom@mail.nankai.edu.cn)
- **GitHub**: [https://github.com/gaomn/DEGA](https://github.com/gaomn/DEGA)

---

If this project is helpful for your research, please consider giving it a star.
