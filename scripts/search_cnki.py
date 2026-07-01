#!/usr/bin/env python3
"""
CNKI文献检索脚本
用于从CNKI检索学术文献并生成结构化引用

用法:
    python3 search_cnki.py "关键词1" "关键词2" --years 2015-2025 --output references.json
"""
import argparse
import json
import re
import sys
from datetime import date
from typing import List, Dict, Optional

# 尝试导入requests
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("Warning: requests库未安装，将使用WebSearch替代")


class CNKISearcher:
    """CNKI文献检索器"""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.results = []

    def search(self, keywords: List[str], years: str = "2015-2025") -> List[Dict]:
        """
        搜索CNKI文献

        Args:
            keywords: 搜索关键词列表
            years: 年份范围，格式"2015-2025"

        Returns:
            文献列表
        """
        start_year, end_year = map(int, years.split('-'))

        # 模拟检索结果（实际应通过WebSearch或API获取）
        results = []

        for keyword in keywords:
            # 这里应该调用实际的CNKI搜索
            # 由于CNKI需要登录，这里返回空列表让用户手动补充
            print(f"请手动检索: {keyword}")

        return results

    def parse_cnki_result(self, text: str) -> Optional[Dict]:
        """解析CNKI搜索结果文本"""
        # 简单的文本解析
        patterns = {
            'title': r'题名[：:]\s*(.+?)(?=\n|$)',
            'author': r'作者[：:]\s*(.+?)(?=\n|$)',
            'journal': r'文献出处[：:]\s*(.+?)(?=\n|$)',
            'year': r'(\d{4})年',
            'pages': r'(\d+)-(\d+)',
        }

        result = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                if key == 'pages':
                    result['start_page'] = match.group(1)
                    result['end_page'] = match.group(2)
                elif key == 'year':
                    result['year'] = int(match.group(1))
                else:
                    result[key] = match.group(1).strip()

        return result if 'title' in result else None

    def format_reference(self, ref: Dict, style: str = "gb7714") -> str:
        """
        格式化参考文献

        Args:
            ref: 文献信息字典
            style: 格式样式，gb7714=国标格式

        Returns:
            格式化后的引用字符串
        """
        if style == "gb7714":
            parts = []

            # 作者
            if 'authors' in ref:
                authors = ref['authors']
                if len(authors) == 1:
                    parts.append(f"{authors[0]}.")
                elif len(authors) <= 3:
                    parts.append(','.join(authors) + '.')
                else:
                    parts.append(f"{authors[0]}等.")

            # 标题
            if 'title' in ref:
                parts.append(f"{ref['title']}.")

            # 文献类型标识
            doc_type = ref.get('type', 'J')
            type_map = {'J': 'J', 'M': 'M', 'D': 'D', 'C': 'C', 'EB': 'EB/OL'}
            parts[-1] = parts[-1].rstrip('.') + f'[{type_map.get(doc_type, 'J')}].'
            parts.append('')

            # 期刊/出版社
            if 'journal' in ref:
                parts.append(f"{ref['journal']},")
            elif 'publisher' in ref:
                parts.append(f"{ref['publisher']},")

            # 年份
            if 'year' in ref:
                parts.append(f"{ref['year']},")

            # 卷期页码
            if 'volume' in ref:
                parts.append(f"{ref['volume']},")
            if 'issue' in ref:
                parts.append(f"({ref['issue']}),")
            if 'start_page' in ref:
                if 'end_page' in ref:
                    parts.append(f"{ref['start_page']}-{ref['end_page']}.")
                else:
                    parts.append(f"{ref['start_page']}.")

            return ''.join(parts)

        return str(ref)

    def save_results(self, results: List[Dict], output: str):
        """保存检索结果"""
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到: {output}")


def main():
    parser = argparse.ArgumentParser(
        description='CNKI文献检索工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    %(prog)s "多模态知识图谱" "叙事可视化" --years 2020-2025
    %(prog)s "非物质文化遗产" "数字化保护" -o refs.json
        """
    )

    parser.add_argument(
        'keywords',
        nargs='+',
        help='搜索关键词（可多个）'
    )
    parser.add_argument(
        '-y', '--years',
        default='2015-2025',
        help='年份范围，格式: 2015-2025 (默认: 2015-2025)'
    )
    parser.add_argument(
        '-o', '--output',
        default=f'references_{date.today().isoformat()}.json',
        help='输出文件路径'
    )
    parser.add_argument(
        '-f', '--format',
        choices=['json', 'bibtex', 'gb7714'],
        default='json',
        help='输出格式'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示详细信息'
    )

    args = parser.parse_args()

    if args.verbose:
        print(f"关键词: {args.keywords}")
        print(f"年份范围: {args.years}")
        print(f"输出文件: {args.output}")

    searcher = CNKISearcher()
    results = searcher.search(args.keywords, args.years)

    if results:
        searcher.save_results(results, args.output)
        print(f"检索到 {len(results)} 条文献")
    else:
        print("未检索到文献，请手动搜索后补充。")
        print("\n建议手动搜索以下关键词:")
        for kw in args.keywords:
            print(f"  - {kw}")


if __name__ == '__main__':
    main()
