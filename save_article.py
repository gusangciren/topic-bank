#!/usr/bin/env python3
"""
topic-bank: 选题库保存工具
用法: python3 save_article.py --title "标题" --body "正文" [--config config.json]
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_CONFIG = {
    "storage_dir": "~/Desktop/定时发布/",
    "filename_template": "{date}-{title}.md"
}

ILLEGAL_CHARS = r'[\\/:*?"<>|]'
TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
DATE_ONLY = datetime.now().strftime("%Y-%m-%d")


def load_config(config_path: str) -> dict:
    """加载 JSON 配置文件，不存在则返回默认配置"""
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    return DEFAULT_CONFIG.copy()


def sanitize_filename(title: str) -> str:
    """把标题中的非法文件名字符替换为短横线"""
    # 先去掉首尾空格和换行
    title = title.strip()
    # 替换非法字符
    sanitized = re.sub(ILLEGAL_CHARS, "-", title)
    # 去掉连续短横线和首尾短横线
    sanitized = re.sub(r"-+", "-", sanitized).strip("-")
    return sanitized if sanitized else "untitled"


def resolve_path(storage_dir: str) -> Path:
    """展开 ~ 和环境变量，返回绝对路径"""
    return Path(os.path.expanduser(os.path.expandvars(storage_dir))).resolve()


def generate_filename(template: str, title: str, storage_dir: Path) -> Path:
    """生成文件名，处理重名冲突"""
    safe_title = sanitize_filename(title)
    raw = template.format(date=DATE_ONLY, title=safe_title)
    target = storage_dir / raw

    if not target.exists():
        return target

    # 文件已存在，加序号
    counter = 2
    while True:
        new_name = f"{DATE_ONLY}-{safe_title}-{counter}.md"
        candidate = storage_dir / new_name
        if not candidate.exists():
            return candidate
        counter += 1


def build_content(title: str, body: str) -> str:
    """组装 Markdown 文件内容"""
    body = body.strip()
    return f"# {title.strip()}\n\n{body}\n\n---\n来源：选题库\n存入时间：{TIMESTAMP}\n"


def save(title: str, body: str, config: dict) -> dict:
    """执行保存，返回结果字典"""
    try:
        storage_dir = resolve_path(config["storage_dir"])
        storage_dir.mkdir(parents=True, exist_ok=True)

        filename = generate_filename(config["filename_template"], title, storage_dir)
        content = build_content(title, body)

        with open(filename, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)

        return {
            "status": "ok",
            "path": str(filename),
            "filename": filename.name,
            "size": len(content)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def main():
    parser = argparse.ArgumentParser(
        description="选题库保存工具 — 将文章存入 Markdown 文件"
    )
    parser.add_argument("--title", "-t", required=True, help="文章标题")
    parser.add_argument("--body", "-b", required=True, help="文章正文（支持多行）")
    parser.add_argument(
        "--config", "-c",
        default="config.json",
        help="配置文件路径（默认 config.json）"
    )
    parser.add_argument(
        "--output", "-o",
        help="直接指定输出目录（覆盖 config 中的 storage_dir）"
    )
    args = parser.parse_args()

    config = load_config(args.config)
    if args.output:
        config["storage_dir"] = args.output

    result = save(args.title, args.body, config)

    if result["status"] == "ok":
        print(f"✅ 已存入：{result['filename']}")
        print(f"📁 {result['path']}")
    else:
        print(f"❌ 保存失败：{result['message']}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
