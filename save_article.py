#!/usr/bin/env python3
"""
topic-bank: 选题库保存工具
用法: python3 save_article.py --title "标题" --body "正文" [--tags "#标签1 #标签2"]

优先读取 skill.json（可被 git pull 更新覆盖），若无则读 config.json。
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

ILLEGAL_CHARS = r'[\\/:*?"<>|]'
TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
DATE_ONLY = datetime.now().strftime("%Y-%m-%d")


def load_config(skill_json: str = "skill.json", config_json: str = "config.json") -> dict:
    """优先读 skill.json，无则读 config.json"""
    for path in [skill_json, config_json]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                # 统一映射
                return {
                    "storage_dir": cfg.get("target_dir", "~/Desktop/定时发布/"),
                    "filename_prefix": cfg.get("filename_date_prefix", True),
                }
    # 兜底默认
    return {"storage_dir": "~/Desktop/定时发布/", "filename_prefix": True}


def sanitize_filename(title: str) -> str:
    """标题中的非法文件名字符替换为短横线"""
    title = title.strip()
    sanitized = re.sub(ILLEGAL_CHARS, "-", title)
    sanitized = re.sub(r"-+", "-", sanitized).strip("-")
    return sanitized if sanitized else "untitled"


def resolve_path(storage_dir: str) -> Path:
    """展开 ~ 和环境变量，返回绝对路径"""
    return Path(os.path.expanduser(os.path.expandvars(storage_dir))).resolve()


def generate_filename(title: str, storage_dir: Path, use_date_prefix: bool) -> Path:
    """生成文件名，处理重名冲突"""
    safe_title = sanitize_filename(title)
    if use_date_prefix:
        raw = f"{DATE_ONLY}-{safe_title}.md"
    else:
        raw = f"{safe_title}.md"
    target = storage_dir / raw

    if not target.exists():
        return target

    # 文件已存在，加序号
    counter = 2
    while True:
        if use_date_prefix:
            new_name = f"{DATE_ONLY}-{safe_title}-{counter}.md"
        else:
            new_name = f"{safe_title}-{counter}.md"
        candidate = storage_dir / new_name
        if not candidate.exists():
            return candidate
        counter += 1


def build_content(title: str, body: str, tags: list) -> str:
    """组装 Markdown 文件内容"""
    body = body.strip()
    tag_line = ""
    if tags:
        tag_line = "\n".join(f"- 标签：{t}" for t in tags)
    return f"# {title.strip()}\n\n{body}\n\n---\n来源：选题库\n存入时间：{TIMESTAMP}\n{tag_line}\n"


def save(title: str, body: str, tags: list, config: dict) -> dict:
    """执行保存，返回结果字典"""
    try:
        storage_dir = resolve_path(config["storage_dir"])
        storage_dir.mkdir(parents=True, exist_ok=True)

        filename = generate_filename(title, storage_dir, config["filename_prefix"])
        content = build_content(title, body, tags)

        with open(filename, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)

        return {
            "status": "ok",
            "path": str(filename),
            "filename": filename.name,
            "size": len(content),
            "tags": tags,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def main():
    parser = argparse.ArgumentParser(
        description="选题库保存工具 — 将文章存入 Markdown 文件"
    )
    parser.add_argument("--title", "-t", required=True, help="文章标题")
    parser.add_argument("--body", "-b", required=True, help="文章正文（支持多行）")
    parser.add_argument("--tags", help="标签，多个用空格分隔，如：#创业 #写作")
    parser.add_argument("--dir", "-d", help="直接指定输出目录（覆盖配置）")
    parser.add_argument(
        "--skill-json",
        default="skill.json",
        help="skill.json 路径（默认 skill.json）"
    )
    parser.add_argument(
        "--config",
        default="config.json",
        help="config.json 路径（无 skill.json 时备用，默认 config.json）"
    )
    args = parser.parse_args()

    # 解析标签
    tags = []
    if args.tags:
        tags = [t.strip() for t in args.tags.split() if t.strip()]

    config = load_config(args.skill_json, args.config)
    if args.dir:
        config["storage_dir"] = args.dir

    result = save(args.title, args.body, tags, config)

    if result["status"] == "ok":
        print(f"✅ 已存入：{result['filename']}")
        if tags:
            print(f"🏷️  标签：{' '.join(tags)}")
        print(f"📁 {result['path']}")
    else:
        print(f"❌ 保存失败：{result['message']}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
