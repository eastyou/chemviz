# chemviz

[![CI](https://github.com/eastyou/chemviz/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/chemviz/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-brightgreen.svg)](pyproject.toml)

给初中化学课做的可视化工具：一条命令生成元素周期表、原子结构示意图和常见分子模型，还能算相对分子质量、自动配平化学方程式。**零依赖，单文件 HTML，数据只在本机，不需要联网。**

课本上的原子结构、分子模型大多是静态插图，学生很难把「核电荷数」「电子层」「化学式」联系起来。`chemviz` 把它们放到同一页里，元素、原子、分子、化学式互相对照，也方便老师投屏或打印。

## 特性

- **元素周期表**：前 20 号元素按周期和族排布，另附初中常见的 Mn、Fe、Cu、Zn、Ag、I、Ba、Hg
- **原子结构示意图**：前 20 号元素的原子核与各层电子，纯 SVG 绘制
- **常见分子模型**：H₂、O₂、N₂、H₂O、CO₂、CH₄、NH₃、HCl、NaCl，含单键、双键、三键与离子化合物示意
- **相对分子质量**：支持括号，例如 `Ca(OH)2`、`Fe2(SO4)3`
- **方程式配平**：输入 `Fe + O2 = Fe3O4`，自动给出 `3Fe + 2O2 = Fe3O4`
- **打印友好**：A4 横向排版；单文件、无外部资源，拷到 U 盘也能打开
- **64 个单元测试**：元素数据、化学式解析、线性方程组配平、SVG 输出与命令行

## 安装

```bash
pip install "git+https://github.com/eastyou/chemviz.git"
```

或者不安装，直接运行：

```bash
git clone https://github.com/eastyou/chemviz.git
cd chemviz
python3 -m chemviz --help
```

## 快速开始

生成可视化页面：

```console
$ chemviz html -o 化学可视化.html
已生成 化学可视化.html
```

用浏览器打开，即可看到元素周期表、原子结构和分子模型。打印时选择 **A4 横向** 效果最好。

查看元素资料与原子结构：

```console
$ chemviz element Na
Na 钠：原子序数 11，相对原子质量 23，金属元素
电子排布：2、8、1

$ chemviz atom 17
Cl 氯 的原子结构：核电荷数 +17，各层电子数 2、8、7
```

计算相对分子质量：

```console
$ chemviz mass Ca(OH)2
Ca(OH)2 的相对分子质量 = 74
元素组成：Ca:1、H:2、O:2
```

配平方程式（`=`、`->`、`→` 都可以）：

```console
$ chemviz balance "Fe + O2 = Fe3O4"
3Fe + 2O2 = Fe3O4

$ chemviz balance "CH4 + O2 = CO2 + H2O"
CH4 + 2O2 = CO2 + 2H2O
```

## 参数

| 命令 | 说明 |
| --- | --- |
| `chemviz html [-o 文件] [--title 标题]` | 生成可视化页面，默认 `chemviz.html` |
| `chemviz element 符号/序数` | 查看元素资料 |
| `chemviz atom 符号/序数` | 查看各层电子数 |
| `chemviz mass 化学式` | 计算相对分子质量 |
| `chemviz balance "方程式"` | 自动配平 |

### 退出码

| 退出码 | 含义 |
| --- | --- |
| `0` | 成功 |
| `1` | 页面写入失败 |
| `2` | 元素、化学式或方程式有误 |

## 说明与边界

- 相对原子质量采用初中教材常用值，例如 Cl 取 35.5、Cu 取 64、Zn 取 65
- 原子结构示意图只覆盖前 20 号元素；Fe、Cu 等只提供元素资料
- 分子模型用于理解原子的连接方式，不表示真实键长和空间比例；CH₄ 为平面示意
- 配平暂时只支持「一种配平方式」的方程式；遇到 `H2 + O2 = H2O + H2O2` 这类多解情况会明确提示，不会随便给一个答案
- 配平不处理离子电荷与结晶水，适合初中阶段的普通化学方程式

## 常见问题

**需要联网吗？**
不需要。程序没有任何联网代码，生成的 HTML 也不引用外部 JS/CSS。

**可以改元素数据吗？**
可以，编辑 `chemviz/elements.py` 中的元素表即可，测试会帮助你检查数据是否自洽。

**为什么不能输入系数？**
配平工具会自己计算系数；手动输入系数容易和计算结果冲突，所以直接拒绝并提示。

## 开发与测试

```bash
python3 -m unittest discover -s tests -v
```

CI 覆盖 Python 3.9 ~ 3.13 与 Linux/macOS/Windows。

## License

[MIT](LICENSE) © 2026 eastyou
