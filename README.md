#  AI 看图生成工厂：已集成上不上AI评分系统、XX日记生成器）

[![en](https://img.shields.io/badge/language-English-blue.svg)](./README.en.md)

**无需编写一行代码，只需修改 YAML 配置文件，即可轻松构建属于你自己的 上不上评分器、XX日记生成器！**

本项目是一个基于 Flask + Vue 的轻量级框架，旨在让任何人都能快速创建自定义的 AI 工具。目前已内置一个 AI 故事生成器示例、上不上AI 评分系统和XX日记生成器。

**🚀 在线体验 / Live Demo: [www.nepfuns.xyz](http://www.nepfuns.xyz)**

---

### ✨ 主要特性 (Features)

* **⚡️ 无代码定制**：通过简单的 YAML 文件定义输入、输出和提示词，无需修改任何后端或前端代码。
* **🎨 动态 UI 生成**：前端界面会根据你的配置文件自动生成对应的输入表单和输出展示卡片。
* **🔧 高度可扩展**：轻松添加任意多个不同的 AI 生成器，为每个生成器自定义输入与展示项。
* **🔌 可插拔 AI 模型**：目前已集成 Gemini API，未来计划支持更多 LLM API和本地模型。
* **📦 开箱即用**：提供清晰的部署指南和示例，让你在几分钟内就能运行自己的实例。

### 核心理念：YAML轻松配置

创建一套全新的 AI 生成器，你只需要关心四份 YAML 配置文件。它们共同定义了一个完整应用的全部流程：

1.  `input-format.yaml`：定义**用户需要输入什么**（例如：故事主角、地点）。
2.  `output-format.yaml`：定义**你希望 AI 输出什么**（例如：故事标题、内容、评分）。
3.  `preset_prompt.yaml`：定义**系统级提示词**（这是你给 AI 的核心指令，每次都会发送）。
4.  `user_prompt.yaml`：定义**用户最终的提示词**（它会把用户的输入整合进一个完整的指令中）。

通过这个设计，你可以像搭乐高一样，自由组合出无限可能。

### 🚀 快速开始 (Getting Started)

#### 前端部署

```bash
# 进入前端项目目录
cd /path/to/vue-app

# 安装依赖
npm install

# (可选) 本地开发启动
npm run serve

# 构建生产环境包 (文件将生成在 dist 目录下)
npm run build
```

#### 后端部署

**环境要求**: Python 3.10+

```bash
# 1. 安装依赖
pip install Flask Flask-Cors Flask-limiter Flask-redis redis google-genai requests Pillow python-dotenv pyyaml gunicorn

# 2. 启动服务 (开发环境)
# python app.py

# 3. 启动服务 (生产环境)
# 使用 gunicorn 以 4 个工作进程启动，监听本地 5000 端口
nohup gunicorn -w 4 -b 127.0.0.1:5000 app:app &
```

---

### 🛠️ 如何构建你的专属生成器 (Tutorial)

假设我们要创建一个“小故事生成器”，它需要用户上传一张图片，输入`姓名(name)`和`地点(place)`，然后生成一个包含`标题(title)`和`内容(story)`的故事。

**第1步: 定义输出格式 (`output-format.yaml`)**

告诉系统你希望 AI 返回的数据结构。

```yaml
story_generator: # 生成器的唯一 ID
  fields:
    title:
      label-zh: "故事标题"
      type: str
      sort: 1
    story:
      label-zh: "故事内容"
      type: str
      sort: 2
```

**第2步: 定义输入格式 (`input-format.yaml`)**

定义用户在网页上需要填写的表单。

```yaml
story_generator: # 同样的唯一 ID
  label-zh: "动态故事生成器"
  label-en: "Dynamic Story Generator"
  fields:
    name:
      label-zh: "主角姓名"
      label-en: "Name"
      type: str
      sort: 1
    place:
      label-zh: "故事地点"
      label-en: "Place"
      type: str
      sort: 2
```

**第3步: 定义系统提示词 (`preset_prompt.yaml`)**

给 AI 一个基础的角色设定或指令。

```yaml
story_generator: # 同样的唯一 ID
  zh: "你是一个富有想象力的故事作家。"
  en: "You are an imaginative storyteller."
```

**第4步: 定义用户提示词 (`user_prompt.yaml`)**

这是最关键的一步，将用户的输入（用 `{}` 包裹的变量）整合到最终的指令中。

```yaml
story_generator: # 同样的唯一 ID
  zh: "请创作一个主角叫`{name}`，发生在`{place}`的短篇故事。"
  en: "Please write a short story about a character named `{name}` that takes place in `{place}`."
```

完成！无需重启后端服务，刷新后你的网站上就会自动出现一个新的“动态故事生成器”。

### 🗺️ 未来规划 (Roadmap)

* [ ] 支持 OpenAI API
* [ ] 支持调用本地模型
* [ ] 历史记录保存

### ❤️ 如何贡献 (Contributing)

欢迎提交 Pull Request 或创建 Issue 来报告 Bug 或提出新功能建议