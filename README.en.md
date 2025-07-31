# AI Image Generation Factory: Integrated with Fxxk or Not AI rating system and XX diary generator)

[![zh](https://img.shields.io/badge/language-简体中文-blue.svg)](./README.md)

**Effortlessly build your own custom AI content generators, scorers, translators, and more—all without writing a single line of code. Just edit YAML files!**

This project provides a lightweight framework using Flask + Vue, designed to empower anyone to quickly create bespoke AI tools. It comes with a pre-built AI Story Generator and an AI Scoring System as examples to get you started.

**🚀 Live Demo: [www.nepfuns.xyz](http://www.nepfuns.xyz)**

---

### ✨ Features

* **⚡️ No-Code Customization**: Define your inputs, outputs, and prompts in simple YAML files. No need to touch the backend or frontend code.
* **🎨 Dynamic UI Generation**: The frontend interface automatically renders input forms and output cards based on your configurations.
* **🔧 Highly Extensible**: Easily add as many different AI generators as you want, each with its own unique UI and logic.
* **🔌 Pluggable AI Models**: Currently integrated with the Gemini API, with planned support for more LLM APIs (like OpenAI) and local models.
* **📦 Out-of-the-Box**: Comes with clear deployment guides and examples to get your own instance running in minutes.

### The Core Concept: Everything is Configurable

To create a new AI generator, you only need to focus on four YAML configuration files. Together, they define the entire workflow of your application:

1.  `input-format.yaml`: Defines **what the user needs to provide** (e.g., a character's name, a location).
2.  `output-format.yaml`: Defines **what you want the AI to return** (e.g., a story title, content, a score).
3.  `preset_prompt.yaml`: Defines the **system-level prompt** (the core instruction or persona for the AI, sent with every request).
4.  `user_prompt.yaml`: Defines the **final user prompt**, which dynamically injects the user's input into a complete instruction.

With this design, you can build and experiment with new ideas as easily as stacking LEGO bricks.

### 🚀 Getting Started

#### Frontend Deployment

```bash
# Navigate to the frontend project directory
cd /path/to/vue-app

# Install dependencies
npm install

# (Optional) Run for local development
npm run serve

# Build for production (files will be in the dist/ directory)
npm run build
```

#### Backend Deployment

**Prerequisites**: Python 3.10+

```bash
# 1. Install dependencies
pip install Flask Flask-Cors Flask-limiter Flask-redis redis google-genai requests Pillow python-dotenv pyyaml gunicorn

# 2. Run the server (for development)
# python app.py

# 3. Run the server (for production)
# Use Gunicorn with 4 worker processes, listening on localhost:5000
nohup gunicorn -w 4 -b 127.0.0.1:5000 app:app &
```

---

### 🛠️ How to Build Your Own Generator (Tutorial)

Let's create a "Short Story Generator." It will ask the user for a `name` and a `place`, and then generate a story with a `title` and `story` content.

**Step 1: Define the Output Format (`output-format.yaml`)**

Tell the system the data structure you expect back from the AI.

```yaml
story_generator: # A unique ID for your generator
  fields:
    title:
      label-en: "Story Title"
      type: str
      sort: 1
    story:
      label-en: "Story Content"
      type: str
      sort: 2
```

**Step 2: Define the Input Format (`input-format.yaml`)**

Define the web form that the user will fill out.

```yaml
story_generator: # Use the same unique ID
  label-zh: "动态故事生成器"
  label-en: "Dynamic Story Generator"
  fields:
    name:
      label-zh: "主角姓名"
      label-en: "Character Name"
      type: str
      sort: 1
    place:
      label-zh: "故事地点"
      label-en: "Location"
      type: str
      sort: 2
```

**Step 3: Define the System Prompt (`preset_prompt.yaml`)**

Give the AI a base role or instruction.

```yaml
story_generator: # Use the same unique ID
  zh: "你是一个富有想象力的故事作家。"
  en: "You are an imaginative storyteller."
```

**Step 4: Define the User Prompt (`user_prompt.yaml`)**

This is the key step. It merges the user's input (variables wrapped in `{}`) into the final command for the AI.

```yaml
story_generator: # Use the same unique ID
  zh: "请创作一个主角叫`{name}`，发生在`{place}`的短篇故事。"
  en: "Please write a short story about a character named `{name}` that takes place in `{place}`."
```

That's it! No need to restart your backend server, just refresh and the new "Dynamic Story Generator" will automatically appear on your site.

### 🗺️ Roadmap

* [ ] Support for the OpenAI API
* [ ] Support for local models
* [ ] User authentication and history

### ❤️ Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change. We appreciate every contribution from the community.