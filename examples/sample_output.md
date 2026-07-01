# 示例输出

## 输入

```bash
# 1. 文献检索
python3 scripts/search_cnki.py "多模态知识图谱" "叙事可视化" "非物质文化遗产"

# 2. 写入Zotero
python3 scripts/write_zotero.py --input references.json --collection "数字人文-纸影研究-2026-07-01"

# 3. 生成论文
python3 scripts/build_paper.py \
  --proposal 申报书.pdf \
  --structure "问题提出-文献基础-方案展开-可验证应用场景-结语" \
  --output 论文.md

# 4. 转换为Word
pandoc 论文.md -o 论文.docx --reference-doc=模板.docx
```

## 输出示例

### 论文Markdown格式

```markdown
# 多模态知识图谱驱动的纸影博物馆叙事可视化研究

**摘要：** 本文针对中小型非遗博物馆"重展示、轻叙事"的困境，提出...

**关键词：** 多模态知识图谱；叙事可视化；纸影艺术；博物馆数字化

## 一、问题提出

非物质文化遗产的数字化保护已从单纯的资料抢救阶段进入知识组织与传播深化阶段¹...

## 二、文献基础

### （一）叙事可视化理论演进

Segel与Heer系统梳理了这一领域的理论框架²...

## 三、方案展开

### （一）研究框架

本研究提出"数据—语义—叙事—交互"一体化框架...

## 四、可验证应用场景

### 场景一：升平轩纸影博物馆展陈升级

...

## 五、结语

本研究针对中小型非遗博物馆...

---

**基金项目：** 湖南省自然科学基金面上项目...

**注释：**

¹ Segel E, Heer J. Narrative Visualization: Telling Stories with Data[J]. IEEE Transactions on Visualization and Computer Graphics, 2010, 16(6): 1139-1148.
```

### Zotero写入结果

```json
{
  "collection": "数字人文-纸影研究-2026-07-01",
  "collection_key": "X4HKDD2I",
  "total": 39,
  "created": 11,
  "reused": 28,
  "updated": 0,
  "errors": 0,
  "results": [
    {"status": "created", "key": "EKBVIQSZ", "title": "国务院关于公布第一批国家级..."},
    {"status": "reused", "key": "H53CWCH3", "title": "民间艺人的身份认同..."},
    ...
  ]
}
```

## 论文字数统计

| 部分 | 字数 | 比例 |
|------|------|------|
| 摘要+关键词 | ~300 | 5% |
| 一、问题提出 | ~800 | 13% |
| 二、文献基础 | ~2000 | 33% |
| 三、方案展开 | ~1500 | 25% |
| 四、可验证应用场景 | ~1200 | 20% |
| 五、结语 | ~300 | 5% |
| **总计** | ~6100 | 100% |

## 参考文献统计

| 类型 | 数量 |
|------|------|
| 外文期刊 | 7 |
| 中文核心期刊 | 20 |
| 学位论文 | 4 |
| 专著 | 4 |
| 网络资源 | 1 |
| **总计** | 36 |