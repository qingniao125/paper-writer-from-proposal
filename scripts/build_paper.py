#!/usr/bin/env python3
"""
论文构建脚本
从申报书生成学术论文框架

用法:
    python3 build_paper.py --proposal 申报书.pdf --template 模板.docx --output 论文.md
"""
import argparse
import os
import re
import subprocess
import sys
from datetime import date
from typing import Dict, List, Optional, Tuple


class PaperBuilder:
    """论文构建器"""

    def __init__(self):
        self.content = {}
        self.references = []
        self.structure = []

    def extract_from_proposal(self, proposal_path: str) -> Dict:
        """
        从申报书提取关键信息

        Args:
            proposal_path: 申报书文件路径

        Returns:
            提取的信息字典
        """
        # 尝试提取文本
        if proposal_path.endswith('.pdf'):
            text = self._extract_pdf_text(proposal_path)
        elif proposal_path.endswith('.txt'):
            with open(proposal_path, 'r', encoding='utf-8') as f:
                text = f.read()
        elif proposal_path.endswith('.docx'):
            text = self._extract_docx_text(proposal_path)
        else:
            raise ValueError(f"不支持的文件格式: {proposal_path}")

        # 提取关键信息
        info = {
            'title': self._extract_title(text),
            'authors': self._extract_authors(text),
            'keywords': self._extract_keywords(text),
            'abstract': self._extract_abstract(text),
            'references': self._extract_references(text),
            'research_content': self._extract_research_content(text),
            'innovation': self._extract_innovation(text),
        }

        return info

    def _extract_pdf_text(self, path: str) -> str:
        """提取PDF文本"""
        try:
            result = subprocess.run(
                ['gs', '-dNOPAUSE', '-dBATCH', '-sDEVICE=txtwrite',
                 '-sOutputFile=-', path],
                capture_output=True, text=True
            )
            return result.stdout
        except FileNotFoundError:
            # 尝试pdftotext
            try:
                result = subprocess.run(
                    ['pdftotext', '-layout', path, '-'],
                    capture_output=True, text=True
                )
                return result.stdout
            except FileNotFoundError:
                raise ValueError("需要安装Ghostscript或pdftotext来读取PDF")

    def _extract_docx_text(self, path: str) -> str:
        """提取DOCX文本"""
        try:
            result = subprocess.run(
                ['textutil', '-convert', 'txt', '-stdout', path],
                capture_output=True, text=True
            )
            return result.stdout
        except FileNotFoundError:
            raise ValueError("需要安装textutil来读取DOCX")

    def _extract_title(self, text: str) -> str:
        """提取标题"""
        patterns = [
            r'项目名称[：:]\s*(.+?)(?:\n|$)',
            r'项目名称[：:]\s*(.+?)$',
            r'（.+?）\s*[\n\r](.+?)$',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                return match.group(1).strip()
        return "待定标题"

    def _extract_authors(self, text: str) -> List[str]:
        """提取作者"""
        patterns = [
            r'项目负责人[：:]\s*(.+?)(?:\n|$)',
            r'申请人[：:]\s*(.+?)(?:\n|$)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return [m.strip() for m in match.group(1).split(',')]
        return []

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        patterns = [
            r'中文关键词[：:]\s*(.+?)(?:\n|$)',
            r'关键词[：:]\s*(.+?)(?:\n|$)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                keywords = match.group(1)
                # 去除序号和分隔符
                keywords = re.sub(r'^\d+[.、]', '', keywords)
                return [k.strip() for k in re.split(r'[、；;，,]', keywords) if k.strip()]
        return []

    def _extract_abstract(self, text: str) -> str:
        """提取摘要"""
        patterns = [
            r'中文摘要[：:\n](.+?)(?=英文摘要|Abstract|$)',
            r'摘要[：:\n](.+?)(?=关键词|$)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return match.group(1).strip()
        return ""

    def _extract_references(self, text: str) -> List[Dict]:
        """提取参考文献"""
        refs = []

        # 匹配常见参考文献格式
        # [1] 作者. 标题[J]. 期刊, 年, 卷(期): 页码.
        # [1] Author. Title[J]. Journal, Year, Vol(Issue): Pages.

        patterns = [
            # 中文格式
            r'\[\d+\]\s*([^[]+?)\.(.+?)\[([A-Z])\]\.?\s*([^,]+?),?\s*(\d{4}),?\s*(\d+)?\s*[\(（]?(\d+)?[\)）]?:?\s*(\d+-\d+)?\.?',
            # 英文格式
            r'\[\d+\]\s*([A-Z][^,]+?),?\s*([A-Z][^.]+?)\.\s*"([^"]+?)"\s*\[J\]\.?\s*([^,]+?),?\s*(\d{4}),?\s*(\d+)?\s*[\(（]?(\d+)?[\)）]?:?\s*(\d+-\d+)?\.?',
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                groups = match.groups()
                if len(groups) >= 3:
                    ref = {
                        'rid': f'ref{len(refs) + 1:02d}',
                        'authors': groups[0].strip() if groups[0] else '',
                        'title': groups[2].strip() if len(groups) > 2 else groups[1].strip(),
                        'type': groups[2].upper() if len(groups) > 2 and groups[2] else 'J',
                    }
                    if len(groups) > 3:
                        ref['journal'] = groups[3].strip()
                    if len(groups) > 4:
                        ref['year'] = groups[4].strip()
                    if len(groups) > 5:
                        ref['volume'] = groups[5].strip()
                    refs.append(ref)

        return refs

    def _extract_research_content(self, text: str) -> str:
        """提取研究内容"""
        patterns = [
            r'二[一-龥]*研究内容[一-龥]*\n(.+?)(?=三|$)',
            r'研究内容[：:\n](.+?)(?=研究目标|$)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return match.group(1).strip()[:2000]  # 限制长度
        return ""

    def _extract_innovation(self, text: str) -> str:
        """提取创新点"""
        patterns = [
            r'四[一-龥]*特色与创新[一-龥]*\n(.+?)(?=五|$)',
            r'创新之处[：:\n](.+?)(?=年度计划|$)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return match.group(1).strip()
        return ""

    def build_paper_structure(self, info: Dict, structure: str) -> str:
        """
        构建论文结构

        Args:
            info: 从申报书提取的信息
            structure: 结构类型，如"问题提出-文献基础-方案展开-应用验证-结语"

        Returns:
            Markdown格式论文
        """
        sections = structure.split('-')
        paper = []

        # 标题
        paper.append(f"# {info.get('title', '研究标题')}\n")

        # 摘要
        if info.get('abstract'):
            paper.append(f"**摘要：** {info['abstract']}\n")
            paper.append(f"\n**关键词：** {'；'.join(info.get('keywords', []))}\n")

        # 各章节
        for section in sections:
            section = section.strip()
            if section == '问题提出':
                paper.extend(self._build_problem_section(info))
            elif section == '文献基础':
                paper.extend(self._build_literature_section(info))
            elif section == '方案展开':
                paper.extend(self._build_method_section(info))
            elif section == '可验证应用场景' or section == '应用验证':
                paper.extend(self._build_application_section(info))
            elif section == '结语':
                paper.extend(self._build_conclusion_section(info))

        # 注释
        paper.extend(self._build_references_section(info))

        return '\n'.join(paper)

    def _build_problem_section(self, info: Dict) -> List[str]:
        """构建问题提出章节"""
        return [
            "\n## 一、问题提出\n",
            f"本研究聚焦{info.get('title', '该研究领域')}的相关问题。",
            "\n### （一）研究背景\n",
            "在这一背景下，...",
            "\n### （二）研究问题\n",
            "基于上述背景，本研究提出以下问题：",
            "\n### （三）研究意义\n",
            "本研究的理论意义在于...，实践意义在于...",
        ]

    def _build_literature_section(self, info: Dict) -> List[str]:
        """构建文献基础章节"""
        refs = info.get('references', [])
        refs_text = []
        for i, ref in enumerate(refs[:10], 1):
            refs_text.append(f"{i} {ref.get('authors', '作者')}. {ref.get('title', '标题')}")

        return [
            "\n## 二、文献基础\n",
            "### （一）理论框架\n",
            "相关理论主要包括...",
            "\n### （二）国内外研究现状\n",
            "在相关领域，已有多项研究取得重要进展：\n",
            "\n".join(f"- {r}" for r in refs_text[:5]),
            "\n### （三）研究述评\n",
            "综上所述，现有研究在以下方面存在不足：",
        ]

    def _build_method_section(self, info: Dict) -> List[str]:
        """构建方案展开章节"""
        return [
            "\n## 三、方案展开\n",
            "### （一）研究框架\n",
            "本研究提出以下研究框架：",
            "\n### （二）技术路线\n",
            "具体技术路线包括：",
            "\n### （三）关键创新点\n",
            f"{info.get('innovation', '本研究的创新点包括...')}",
        ]

    def _build_application_section(self, info: Dict) -> List[str]:
        """构建应用验证章节"""
        return [
            "\n## 四、可验证应用场景\n",
            "### 场景一：xxx\n",
            "在这一应用场景中，...",
            "\n### 场景二：xxx\n",
            "在另一个应用场景中，...",
            "\n### 场景三：xxx\n",
            "此外，...",
        ]

    def _build_conclusion_section(self, info: Dict) -> List[str]:
        """构建结语章节"""
        return [
            "\n## 五、结语\n",
            "### （一）研究结论\n",
            "本研究得出以下主要结论：",
            "\n### （二）研究局限与展望\n",
            "本研究存在一定局限：",
            "\n---\n",
            f"\n**基金项目：** {info.get('title', '研究项目')}",
        ]

    def _build_references_section(self, info: Dict) -> List[str]:
        """构建注释章节"""
        refs = info.get('references', [])
        if not refs:
            return []

        lines = [
            "\n**注释：**\n",
        ]

        for i, ref in enumerate(refs[:30], 1):
            # 生成上标序号
            superscript = self._to_superscript(i)

            # 格式化引用
            authors = ref.get('authors', '作者')
            title = ref.get('title', '标题')
            journal = ref.get('journal', '')
            year = ref.get('year', '')
            volume = ref.get('volume', '')
            pages = ref.get('pages', '')

            if journal:
                citation = f"{authors}. {title}[J]. {journal}, {year}"
                if volume:
                    citation += f", {volume}"
                if pages:
                    citation += f": {pages}"
            else:
                citation = f"{authors}. {title}"

            lines.append(f"{superscript} {citation}.\n")

        return lines

    def _to_superscript(self, n: int) -> str:
        """数字转上标"""
        superscripts = {
            '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
            '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'
        }
        return ''.join(superscripts.get(c, c) for c in str(n))

    def save_paper(self, content: str, output_path: str):
        """保存论文"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"论文已保存到: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='学术论文构建工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    %(prog)s --proposal 申报书.pdf --output 论文.md
    %(prog)s --proposal 申报书.txt --structure "问题提出-文献基础-方案展开-结语"
        """
    )

    parser.add_argument(
        '-p', '--proposal',
        required=True,
        help='申报书文件路径 (PDF/TXT/DOCX)'
    )
    parser.add_argument(
        '-t', '--template',
        help='模板文件路径 (DOCX)'
    )
    parser.add_argument(
        '-o', '--output',
        default=f'论文_{date.today().isoformat()}.md',
        help='输出文件路径'
    )
    parser.add_argument(
        '-s', '--structure',
        default='问题提出-文献基础-方案展开-可验证应用场景-结语',
        help='论文结构，用横杠分隔'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示详细信息'
    )

    args = parser.parse_args()

    if args.verbose:
        print(f"申报书: {args.proposal}")
        print(f"输出: {args.output}")
        print(f"结构: {args.structure}")

    # 检查文件
    if not os.path.exists(args.proposal):
        print(f"Error: 文件不存在: {args.proposal}")
        sys.exit(1)

    # 构建论文
    try:
        builder = PaperBuilder()

        if args.verbose:
            print("正在提取申报书信息...")

        info = builder.extract_from_proposal(args.proposal)

        if args.verbose:
            print(f"标题: {info.get('title', 'N/A')}")
            print(f"关键词: {info.get('keywords', [])}")
            print(f"参考文献: {len(info.get('references', []))}条")

        if args.verbose:
            print("正在构建论文...")

        paper = builder.build_paper_structure(info, args.structure)
        builder.save_paper(paper, args.output)

        print(f"\n✅ 论文构建完成！")
        print(f"输出文件: {args.output}")

        # 提示可以转换为Word
        print("\n可选：将Markdown转换为Word")
        print(f"  pandoc {args.output} -o output.docx --reference-doc={args.template or '模板.docx'}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()