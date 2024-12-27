## 评估次数计算公式

```markdown
$$\text{总评估次数} = 100 \times T \times R \left(1 + 0.2 \times T \times localSearchIndNum\right)$$

\text{循环评估次数} = 100 \times T \times R

\text{局部搜索评估次数} = 100 \times T \times R \times 0.2 \times T \times localSearchIndNum


```

## 评估次数计算公式的markdown公式写法


$$ N_{total} = 100 \times T \times R \left(1 + 0.2 \times T \times localSearchIndNum\right) $$
$$N_{loop} = 100 \times T \times R$$
$$N_{localSearch} = 100 \times T \times R \times 0.2 \times T \times localSearchIndNum$$


## 评估次数计算

### 基本公式
- N_total = 100 * T * R * (1 + 0.2 * T * localSearchIndNum)
- N_loop = 100 * T * R
- N_localSearch = 100 * T * R * 0.2 * (T * localSearchIndNum)

### 参数设置 
- T: 任务数量，不定
- R: 机器人数量，不定
- Generations: 进化代数，100
- p_local_search: 局部搜索概率，0.2
- localSearchIndNum: 局部搜索个体数量，1

### 计算公式

- N_total = 100 * T * R * (1 + 0.2 * T * localSearchIndNum) = 100 * T * R * (1 + 0.2 * T)
- N_loop = 100 * T * R = 100 * T * R
- N_localSearch = 100 * T * R * 0.2 * (T * localSearchIndNum) = 100 * T * R * 0.2 * T * localSearchIndNum = 100 * T * R * 0.2 * T

### 计算示例

- T = 10
- R = 5

1. 对每一代
 - N_t0 = 10 * 5 * (1 + 0.2 * 10 * 1) = 10 * 5 * 1.2 = 60
 - N_l0 = 10 * 5 = 50
 - N_ls0 = 10 * 5 * 0.2 * 10 * 1 = 10 * 5 * 0.2 * 10 = 10


2. 100代总计
 - N_t1 = 100 * 10 * 5 * (1 + 0.2 * 10 * 1) = 100 * 10 * 5 * 1.2 = 6000
 - N_l1 = 100 * 10 * 5 = 5000
 - N_ls1 = 100 * 10 * 5 * 0.2 * 10 * 1 = 100 * 10 * 5 * 0.2 * 10 = 1000



