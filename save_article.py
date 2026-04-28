#!/usr/bin/env python3
"""
topic-bank: 选题库保存工具
用法:
  新建文章: python3 save_article.py --title "标题" --body "正文" [--tags "#标签1"]
  追加内容: python3 save_article.py --append-to "标题关键词" --body "追加内容"

优先读取 skill.json（可被 git pull 更新覆盖），若无则读 config.json。
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# 确保从脚本所在目录读取配置文件
_SCRIPT_DIR = Path(__file__).parent.resolve()

ILLEGAL_CHARS = r'[\\/:*?"<>|]'
TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
DATE_ONLY = datetime.now().strftime("%Y-%m-%d")


def _default_config() -> dict:
    return {
        "storage_dir": str(Path.home() / "Desktop" / "定时发布"),
        "filename_prefix": True,
    }


def load_config(skill_json: str = "skill.json", config_json: str = "config.json") -> dict:
    """优先读 skill.json，无则读 config.json"""
    for cfg_name in [skill_json, config_json]:
        p = _SCRIPT_DIR / cfg_name
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                return {
                    "storage_dir": cfg.get("target_dir", "~/Desktop/定时发布/"),
                    "filename_prefix": cfg.get("filename_date_prefix", True),
                }
        if os.path.exists(cfg_name):
            with open(cfg_name, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                return {
                    "storage_dir": cfg.get("target_dir", "~/Desktop/定时发布/"),
                    "filename_prefix": cfg.get("filename_date_prefix", True),
                }
    return _default_config()


def sanitize_filename(title: str) -> str:
    title = title.strip()
    sanitized = re.sub(ILLEGAL_CHARS, "-", title)
    sanitized = re.sub(r"-+", "-", sanitized).strip("-")
    return sanitized if sanitized else "untitled"


def resolve_path(storage_dir: str) -> Path:
    return Path(os.path.expanduser(os.path.expandvars(storage_dir))).resolve()


def find_file_by_keyword(keyword: str, storage_dir: Path) -> Optional[Path]:
    """模糊匹配文件名：去除日期前缀后匹配关键词（不含扩展名）"""
    keyword_lower = keyword.lower().strip()
    candidates = []
    for f in storage_dir.iterdir():
        if not f.is_file() or f.suffix != ".md":
            continue
        # 去掉日期前缀再匹配，如 "2026-04-27-写作就是思考.md" → "写作就是思考"
        name_without_date = re.sub(r"^\d{4}-\d{2}-\d{2}(-\d+)?-", "", f.stem)
        if keyword_lower in name_without_date.lower():
            candidates.append((len(keyword_lower) / max(len(name_without_date), 1), f))
    if not candidates:
        return None
    # 优先匹配度最高的
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


def generate_filename(title: str, storage_dir: Path, use_date_prefix: bool) -> Path:
    safe_title = sanitize_filename(title)
    if use_date_prefix:
        raw = f"{DATE_ONLY}-{safe_title}.md"
    else:
        raw = f"{safe_title}.md"
    target = storage_dir / raw

    if not target.exists():
        return target

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
    body = body.strip()
    tag_line = ""
    if tags:
        tag_line = "\n".join(f"- 标签：{t}" for t in tags)
    return f"# {title.strip()}\n\n{body}\n\n---\n来源：选题库\n存入时间：{TIMESTAMP}\n{tag_line}\n"


def save_new(title: str, body: str, tags: list, config: dict) -> dict:
    try:
        storage_dir = resolve_path(config["storage_dir"])
        storage_dir.mkdir(parents=True, exist_ok=True)

        filename = generate_filename(title, storage_dir, config["filename_prefix"])
        content = build_content(title, body, tags)

        with open(filename, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)

        return {
            "status": "ok",
            "action": "created",
            "path": str(filename),
            "filename": filename.name,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def append_to(keyword: str, new_body: str, config: dict) -> dict:
    """追加内容到已有的 Markdown 文件"""
    try:
        storage_dir = resolve_path(config["storage_dir"])
        target = find_file_by_keyword(keyword, storage_dir)

        if not target:
            return {
                "status": "error",
                "message": f"未找到包含「{keyword}」的已有文件，请确认文件名后再试",
            }

        # 读取原文件内容，移除末尾的来源/时间/标签行
        with open(target, "r", encoding="utf-8") as f:
            original = f.read()

        # 去掉末尾的「---来源：选题库...」行和空行
        cleaned = re.sub(r"\n+---\n+来源：.*?\n存入时间：.*?(\n|$)", "", original, flags=re.DOTALL).rstrip()

        # 追加新内容 + 更新来源时间
        updated = f"{cleaned}\n\n{new_body.strip()}\n\n---\n来源：选题库（追加）\n存入时间：{TIMESTAMP}\n"

        with open(target, "w", encoding="utf-8", newline="\n") as f:
            f.write(updated)

        return {
            "status": "ok",
            "action": "appended",
            "path": str(target),
            "filename": target.name,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def main():
    parser = argparse.ArgumentParser(
        description="选题库保存工具 — 新建文章或追加到已有文件"
    )
    parser.add_argument("--title", "-t", help="文章标题（新建时必填）")
    parser.add_argument("--body", "-b", help="文章正文（必填）")
    parser.add_argument("--tags", help="标签，多个用空格分隔，如：#创业 #写作")
    parser.add_argument(
        "--append-to", help="追加模式：填写目标文件的关键词（模糊匹配）"
    )
    parser.add_argument("--dir", "-d", help="直接指定输出目录（覆盖配置）")
    parser.add_argument(
        "--skill-json",
        default=str(_SCRIPT_DIR / "skill.json"),
        help="skill.json 路径",
    )
    parser.add_argument(
        "--config",
        default=str(_SCRIPT_DIR / "config.json"),
        help="config.json 路径",
    )
    args = parser.parse_args()

    if not args.body:
        print("❌ body 参数必填（--body 或 -b）", file=sys.stderr)
        sys.exit(1)

    tags = []
    if args.tags:
        tags = [t.strip() for t in args.tags.split() if t.strip()]

    config = load_config(args.skill_json, args.config)
    if args.dir:
        config["storage_dir"] = args.dir

    # 追加模式
    if args.append_to:
        keyword = args.append_to.strip()
        result = append_to(keyword, args.body, config)
    else:
        if not args.title:
            print("❌ 新建模式需要 --title 参数", file=sys.stderr)
            sys.exit(1)
        result = save_new(args.title, args.body, tags, config)

    if result["status"] == "ok":
        action_emoji = "📝" if result["action"] == "created" else "✏️"
        print(f"✅ {action_emoji} {result['filename']}")
        print(f"📁 {result['path']}")
    else:
        print(f"❌ {result['message']}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
