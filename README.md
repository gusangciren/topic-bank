# 存入选题库

> 把他人的好文章存进你的选题库

把一篇文章（标题 + 正文）存入本地 Markdown 文件，支持自定义触发词和存放路径。

---

## ⚙️ 可配置项

```json
{
  "trigger_words": ["存入选题库", "存入我的素材库"],
  "target_dir": "~/Desktop/定时发布/",
  "filename_date_prefix": true
}
```

- **`trigger_words`**：触发词列表，说任何一个都会激活本 skill，支持多个
- **`target_dir`**：文章存入的文件夹路径（自动创建）
- **`filename_date_prefix`**：true = 文件名以日期开头，false = 以标题开头

---

## 使用方法

在对话中发送 **触发词** + **文章内容**：

```
存入选题库

标题：文章标题
正文：这里是文章正文...
```

或者一行搞定：

```
存入选题库
标题：文章标题
正文：这里是文章正文...
```

**注意**：正文是必填项，只发标题不发正文会提示补全。

---

## 安装方式

### 方式一：Git clone（推荐）

```bash
git clone https://github.com/gusangciren/topic-bank.git \
  ~/.qclaw/skills/topic-bank
```

### 方式二：手动下载

1. 下载本仓库 ZIP
2. 解压到 `~/.qclaw/skills/topic-bank/` 目录

### 安装后

1. 编辑 `SKILL.md` 中的 `⚙️ 可配置项` 区，设置你的触发词和存放路径
2. 重启 AI assistant（或刷新 skill）

---

## 文件说明

| 文件 | 作用 |
|------|------|
| `SKILL.md` | Skill 说明文件（可配置触发词） |
| `save_article.py` | 核心脚本（零依赖） |
| `config.json` | 配置文件（可改存放目录） |

---

## 存入的文章格式

```markdown
# 文章标题

> 来源：微信公众号/网站/书籍等
> 存入时间：2026-04-27

正文内容...

---

- 标签：
```

---

## 安全说明

- 脚本仅做文件写入，不访问网络
- 文件名自动处理特殊字符
- 重名自动加 `-2.md` 序号，不覆盖已有文件
- 零外部依赖，Python 3.6+ 内置库即可运行

---

## 许可证

MIT License · 欢迎 fork 和定制
