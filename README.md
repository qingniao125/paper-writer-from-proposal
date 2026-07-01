# Paper Writer From Proposal

**从科研申报书到学术论文的完整工作流**

将自科/社科申报书转化为符合以下目标的学术论文：
- 🎓 博士生课程结课论文
- 📊 自科/社科项目结项报告
- 📰 省级/核心期刊发表

## 核心功能

1. **文献调研** - 在CNKI/Google Scholar检索参考文献
2. **Zotero写入** - 将文献自动写入Zotero文献库
3. **论文撰写** - 按照模板生成结构化论文
4. **Word排版** - 输出符合期刊格式的Word文档

## 工作流程

```
申报书分析 → 文献调研 → 文献写入Zotero → 论文撰写 → Word排版
    ↓            ↓            ↓              ↓           ↓
  提取关键词   知网检索    PyZotero API    结构调整    Pandoc转换
  确定结构     核验文献    批量创建/复用   格式规范    模板样式
```

## 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install pyzotero requests python-docx

# 设置Zotero环境变量
export ZOTERO_LIBRARY_ID="你的用户ID"
export ZOTERO_LIBRARY_TYPE="user"
export ZOTERO_API_KEY="你的API密钥"
```

### 2. 运行完整流程

```bash
# 进入项目目录
cd ~/Desktop/你的文件夹

# 运行文献检索与Zotero写入
python3 search_cnki.py "关键词1" "关键词2" "关键词3"

# 生成论文
python3 build_paper.py 申报书.pdf 模板.docx output.md
```

## 脚本说明

### `scripts/search_cnki.py`

在CNKI检索文献并生成结构化引用。

```bash
python3 scripts/search_cnki.py \
  "多模态知识图谱" \
  "叙事可视化" \
  "非物质文化遗产" \
  --years 2015-2025 \
  --output references.json
```

### `scripts/write_zotero.py`

将文献批量写入Zotero。

```bash
# 交互式模式
python3 scripts/write_zotero.py

# 配置文件模式
python3 scripts/write_zotero.py --config references.json
```

### `scripts/build_paper.py`

从申报书生成论文框架。

```bash
python3 scripts/build_paper.py \
  --proposal 申报书.pdf \
  --template 模板.docx \
  --structure "问题提出-文献基础-方案展开-应用验证-结语" \
  --output 论文.md
```

## 论文结构模板

```
一、问题提出
   ├── 研究背景
   ├── 研究问题
   └── 研究意义

二、文献基础
   ├── 理论框架
   ├── 国内外研究现状
   └── 研究述评

三、方案展开
   ├── 研究框架
   ├── 技术路线
   └── 创新点

四、可验证应用场景
   ├── 场景一：xxx
   ├── 场景二：xxx
   └── 场景三：xxx

五、结语
   ├── 研究结论
   ├── 局限与展望
   └── 基金致谢
```

## 格式规范

### 注释格式（GB/T 7714-2015）

```markdown
¹ 作者. 题名[J]. 期刊名, 年, 卷(期): 页码.
² 作者1, 作者2. 题名[M]. 出版地: 出版社, 年.
³ 作者. 题名[EB/OL]. URL. (日期)[访问日期].
```

### Word排版要求

| 项目 | 要求 |
|------|------|
| 正文字体 | 宋体小四/12pt |
| 标题层级 | 一级黑体三号，二级黑体四号 |
| 行距 | 1.5倍或固定18pt |
| 页下注 | 序号用圈码，注文小五 |
| 引用 | 上标序号 |

## 论文字数控制

| 目标 | 正文字数 | 注释字数 |
|------|---------|---------|
| 课程论文 | 5000-8000 | 2000-3000 |
| 项目结项 | 8000-12000 | 3000-5000 |
| 期刊发表 | 6000-10000 | 2000-4000 |

## Zotero集合命名规范

```
{学科}-{主题}-核心文献-{日期}
示例：数字人文-纸影叙事可视化核心文献-2026-07-01
```

## 常见问题

### Q: Zotero API报错
A: 检查环境变量是否正确设置，API密钥是否有写入权限

### Q: 文献检索不到
A: 尝试使用同义词、近义词组合检索

### Q: 格式不符合要求
A: 使用模板.docx作为参考，或在Word中手动调整样式

## 目录结构

```
paper-writer-from-proposal/
├── README.md                    # 本文档
├── scripts/
│   ├── search_cnki.py          # CNKI文献检索
│   ├── write_zotero.py         # Zotero写入
│   └── build_paper.py          # 论文构建
├── templates/
│   └── paper_structure.md       # 论文结构模板
└── examples/
    └── sample_output.md        # 输出示例
```

## 扩展阅读

- [Zotero API文档](https://www.zotero.org/api/)
- [GB/T 7714-2015参考文献著录规则](http://www.nlsg.net.cn/?list_5/414.html)
- [Pandoc Markdown转Word](https://pandoc.org/MANUAL.html#options-for-docx-output)

---

**适用场景**：科研人员、高校教师、博士生撰写学术论文
**技术栈**：Python + Zotero API + Pandoc
**作者**：Claude Code Assistant
