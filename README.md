# topic-bank 选题库

> 把你读到的有价值的文章，一句话存进选题库。等需要写作的时候，打开文件夹，所有素材一目了然。

## 快速开始

### 第一步：安装

```bash
git clone https://github.com/gusangciren/topic-bank.git
cd topic-bank
```

### 第二步：配置（可选）

编辑 `config.json`：

```json
{
  "storage_dir": "~/Desktop/定时发布/",
  "filename_template": "{date}-{title}.md"
}
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `storage_dir` | 文章存放目录 | `~/Desktop/定时发布/` |
| `filename_template` | 文件名模板，支持 `{date}` 和 `{title}` | `{date}-{title}.md` |

### 第三步：保存文章

```bash
python3 save_article.py --title "你的标题" --body "文章正文"
```

也可以通过 **OpenClaw** 直接说：

> 存入选题库，标题：xxx，正文：xxx

---

## 使用场景

- 读公众号时发现好文章 → 存进选题库
- 刷微博时看到金句 → 存进选题库
- 写内容时缺素材 → 打开文件夹找灵感

---

## 文件格式

存入的文件长这样：

```markdown
# 文章标题

文章正文内容，
可以多行。

---
来源：选题库
存入时间：2026-04-27 19:55:00
```

---

## CLI 参数

```
python3 save_article.py [选项]

必填：
  --title, -t    文章标题
  --body, -b     文章正文（支持多行）

可选：
  --config, -c   配置文件路径（默认 config.json）
  --output, -o   直接指定输出目录（覆盖配置）
```

---

## 项目结构

```
topic-bank/
├── save_article.py    # 核心脚本
├── config.json        # 用户配置
├── README.md          # 本文档
├── requirements.txt   # 依赖（无外部依赖，Python 内置库即可）
└── .gitignore
```

---

## 与 OpenClaw 配合

OpenClaw 用户可以在对话中直接说「存入选题库」并附上文章，AI 会自动调用本工具存入指定目录。

触发词：**存入选题库**

---

## License

MIT
