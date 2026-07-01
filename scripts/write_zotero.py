#!/usr/bin/env python3
"""
Zotero文献写入脚本
将参考文献批量写入Zotero文献库

用法:
    python3 write_zotero.py --input references.json
    python3 write_zotero.py --interactive

环境变量:
    ZOTERO_LIBRARY_ID: Zotero用户/组ID
    ZOTERO_LIBRARY_TYPE: "user" 或 "group"
    ZOTERO_API_KEY: Zotero API密钥
"""
import argparse
import json
import os
import re
import sys
from datetime import date
from typing import Dict, List, Optional

# 检查pyzotero
try:
    from pyzotero import zotero
    HAS_PYZOTERO = True
except ImportError:
    HAS_PYZOTERO = False
    print("Warning: pyzotero未安装，请运行: pip install pyzotero")


class ZoteroWriter:
    """Zotero文献写入器"""

    def __init__(self, library_id: str, library_type: str, api_key: str):
        """初始化Zotero连接"""
        if not HAS_PYZOTERO:
            raise ImportError("需要安装pyzotero: pip install pyzotero")

        self.zot = zotero.Zotero(library_id, library_type, api_key)
        self.library_id = library_id
        self.library_type = library_type
        self.collection_key = None

    def get_or_create_collection(self, name: str) -> str:
        """
        获取或创建Zotero集合

        Args:
            name: 集合名称

        Returns:
            集合键
        """
        # 查找现有集合
        for collection in self.zot.everything(self.zot.collections()):
            if collection["data"].get("name") == name:
                print(f"找到现有集合: {name}")
                return collection["key"]

        # 创建新集合
        result = self.zot.create_collections([{"name": name}])
        key = result["success"]["0"]
        print(f"创建新集合: {name} -> {key}")
        return key

    def search_existing_item(self, title: str) -> Optional[Dict]:
        """
        在Zotero中搜索已存在的文献

        Args:
            title: 文献标题

        Returns:
            已存在的文献条目或None
        """
        normalized_title = self._normalize_title(title)

        for item in self.zot.items(q=title, limit=20):
            item_title = item.get("data", {}).get("title", "")
            if self._normalize_title(item_title) == normalized_title:
                return item
        return None

    def _normalize_title(self, title: str) -> str:
        """标准化标题用于比对"""
        return re.sub(r"\s+", "", title or "").lower()

    def create_or_update_item(self, ref: Dict, collection_key: str) -> Dict:
        """
        创建或更新Zotero条目

        Args:
            ref: 文献信息字典
            collection_key: 集合键

        Returns:
            操作结果 {'status': 'created'|'reused'|'updated', 'key': str}
        """
        rid = ref.get("rid", "")

        # 检查是否已存在
        existing = self.search_existing_item(ref.get("title", ""))
        if existing:
            # 如果不在目标集合，添加到集合
            data = existing["data"]
            if collection_key not in data.get("collections", []):
                data.setdefault("collections", []).append(collection_key)
                self.zot.update_item(existing)
                return {"status": "updated", "key": existing["key"], "title": ref.get("title", "")[:30]}
            return {"status": "reused", "key": existing["key"], "title": ref.get("title", "")[:30]}

        # 创建新条目
        try:
            template = self.zot.item_template(ref.get("itemType", "journalArticle"))

            # 复制字段
            for key, value in ref.items():
                if key == "rid":
                    continue
                if key in template or key in {"creators", "extra"}:
                    template[key] = value

            template["collections"] = [collection_key]

            # 验证
            self.zot.check_items([template])

            # 创建
            response = self.zot.create_items([template])
            new_key = response["success"]["0"]

            return {"status": "created", "key": new_key, "title": ref.get("title", "")[:30]}

        except Exception as e:
            return {"status": "error", "error": str(e), "title": ref.get("title", "")[:30]}

    def write_references(self, references: List[Dict], collection_name: str) -> Dict:
        """
        批量写入参考文献

        Args:
            references: 文献列表
            collection_name: 集合名称

        Returns:
            操作结果统计
        """
        # 获取或创建集合
        self.collection_key = self.get_or_create_collection(collection_name)
        print(f"集合Key: {self.collection_key}")

        results = []
        created = 0
        reused = 0
        updated = 0
        errors = 0

        for ref in references:
            result = self.create_or_update_item(ref, self.collection_key)
            results.append(result)

            status = result.get("status", "unknown")
            if status == "created":
                created += 1
                print(f"创建: {ref.get('rid', 'unknown')} -> {result.get('key', '')[:8]}...")
            elif status == "reused":
                reused += 1
                print(f"复用: {ref.get('rid', 'unknown')} -> {result.get('key', '')[:8]}...")
            elif status == "updated":
                updated += 1
                print(f"更新: {ref.get('rid', 'unknown')} -> {result.get('key', '')[:8]}...")
            else:
                errors += 1
                print(f"错误: {ref.get('rid', 'unknown')} -> {result.get('error', 'unknown error')}")

        return {
            "collection": collection_name,
            "collection_key": self.collection_key,
            "total": len(references),
            "created": created,
            "reused": reused,
            "updated": updated,
            "errors": errors,
            "results": results
        }

    def save_results(self, results: Dict, output: str):
        """保存操作结果"""
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存到: {output}")

        # 打印统计
        print(f"\n=== 统计 ===")
        print(f"总计: {results['total']}")
        print(f"创建: {results['created']}")
        print(f"复用: {results['reused']}")
        print(f"更新: {results['updated']}")
        print(f"错误: {results['errors']}")


def load_references_from_json(file_path: str) -> List[Dict]:
    """从JSON文件加载参考文献"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and 'references' in data:
        return data['references']
    else:
        raise ValueError(f"无法解析文件格式: {file_path}")


def interactive_mode() -> List[Dict]:
    """交互式输入参考文献"""
    references = []
    print("=== 交互式输入参考文献 ===")
    print("按Enter空行结束输入\n")

    while True:
        title = input("标题: ").strip()
        if not title:
            break

        ref = {
            "rid": f"ref{len(references) + 1:02d}",
            "itemType": input("类型 [journalArticle/book/thesis]: ").strip() or "journalArticle",
            "title": title,
            "creators": [],
        }

        # 作者
        authors_input = input("作者 (逗号分隔): ").strip()
        if authors_input:
            for author in authors_input.split(","):
                ref["creators"].append({
                    "creatorType": "author",
                    "name": author.strip()
                })

        # 其他字段
        for field in ["publicationTitle", "publisher", "date", "volume", "issue", "pages"]:
            value = input(f"{field}: ").strip()
            if value:
                ref[field] = value

        references.append(ref)
        print(f"已添加: {title[:40]}...")

    return references


def main():
    parser = argparse.ArgumentParser(
        description='Zotero文献写入工具',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '-i', '--input',
        help='输入JSON文件路径'
    )
    parser.add_argument(
        '-o', '--output',
        default=f'zotero_write_result_{date.today().isoformat()}.json',
        help='输出结果文件'
    )
    parser.add_argument(
        '-c', '--collection',
        default=f'学术论文参考文献-{date.today().isoformat()}',
        help='Zotero集合名称'
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='交互式输入文献'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示详细信息'
    )

    args = parser.parse_args()

    # 检查环境变量
    library_id = os.environ.get("ZOTERO_LIBRARY_ID")
    library_type = os.environ.get("ZOTERO_LIBRARY_TYPE", "user")
    api_key = os.environ.get("ZOTERO_API_KEY")

    if not all([library_id, api_key]):
        print("Error: 缺少必要的环境变量")
        print("请设置以下环境变量:")
        print("  ZOTERO_LIBRARY_ID")
        print("  ZOTERO_LIBRARY_TYPE (可选，默认为user)")
        print("  ZOTERO_API_KEY")
        sys.exit(1)

    # 获取参考文献
    if args.interactive:
        references = interactive_mode()
    elif args.input:
        references = load_references_from_json(args.input)
    else:
        print("Error: 请指定 --input 文件 或使用 --interactive 模式")
        sys.exit(1)

    if not references:
        print("没有参考文献需要写入")
        sys.exit(0)

    print(f"准备写入 {len(references)} 条文献到集合: {args.collection}")

    # 连接Zotero并写入
    try:
        writer = ZoteroWriter(library_id, library_type, api_key)
        results = writer.write_references(references, args.collection)
        writer.save_results(results, args.output)

    except ImportError as e:
        print(f"Error: {e}")
        print("\n请安装pyzotero:")
        print("  pip install pyzotero")
        sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
