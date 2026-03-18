# AI Content Automation System

AI-powered platform for generating complete articles with automatic web research and social media content creation.

## Table of Contents

1. [Requirements](#requirements)
2. [Installation](#installation)
3. [API Keys Configuration](#api-keys-configuration)
4. [Usage](#usage)
5. [Project Structure](#project-structure)
6. [How It Works](#how-it-works)
7. [Features](#features)
8. [Troubleshooting](#troubleshooting)

---

## Requirements

### Software

| Software | Min Version | Description |
|----------|-------------|-------------|
| Python | 3.8+ | Programming language |
| Git | 2.0+ | Version control |
| pip | 21.0+ | Python package manager |

### Verify Installation

```bash
python --version
pip --version
git --version
```

---

## Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/BobiptusITE/ai-content-generator.git
cd ai-content-generator
```

### Step 2: Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate
```

**Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Linux / MacOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## API Keys Configuration

### Important

**Each user must create their own `.env` file with personal API keys.** The `.env` file contains private keys and **should NOT** be committed to git.

### Step 1: Copy Example File

**Windows:**
```bash
copy .env.example .env
```

**Linux / MacOS:**
```bash
cp .env.example .env
```

### Step 2: Get API Keys

#### GROQ_API_KEY (Required)

Groq offers free access to high-quality LLM models.

1. Go to https://console.groq.com
2. Create account or sign in
3. Go to "API Keys"
4. Create new API Key
5. Copy and paste to `.env`

```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxx
```

#### TAVILY_API_KEY (Required for web research)

Tavily offers 1000 searches/month free.

1. Go to https://tavily.com
2. Create account or sign in
3. Go to your profile or API section
4. Copy your API Key
5. Paste to `.env`

```
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxx
```

#### GOOGLE_API_KEY (Optional)

Only needed if you want to use Google Gemini as an alternative provider.

1. Go to https://aistudio.google.com/app/apikey
2. Create new API Key
3. Copy and paste to `.env`

```
GOOGLE_API_KEY=AIzaxxxxxxxxxxxxxxxx
```

---

## Usage

### Run the Program

```bash
python generate_article.py
```

### Command Line Options

```bash
python generate_article.py --topic "Your Topic" --tone profesional --research
```

Options:
- `--topic`, `-t`: Article topic
- `--tone`: profesional, casual, tecnico
- `--research`, `-r`: Enable web research

### Interactive Mode

The program will guide you through:
1. Enter article topic
2. Choose web research (recommended)
3. Select tone (professional, casual, technical)

### Output

Generated articles are saved to:
- `outputs/article_[topic]_[date].md` (Markdown)
- `outputs/article_[topic]_[date].txt` (Plain text)
- `outputs/social_posts_[topic]_[date].txt` (Social media posts)

---

## Project Structure

```
ai-content-generator/
├── .env                    # Environment variables (DO NOT commit)
├── .env.example            # Configuration template
├── .gitignore             # Git ignore rules
├── README.md              # This file
├── requirements.txt        # Python dependencies
├── generate_article.py    # Main script
├── src/
│   ├── agents/
│   │   ├── research_agent.py        # Web research agent
│   │   ├── orchestrator.py         # Agent orchestrator
│   │   ├── content_generator.py    # Article generator
│   │   ├── qa_agent.py             # Quality assurance
│   │   ├── social_media_agent.py   # Social media posts
│   │   └── image_agent.py          # Image generation (pending)
│   └── services/
│       └── cache_service.py        # 24-hour cache
└── outputs/                       # Generated content
    ├── article_*.md
    ├── article_*.txt
    └── social_posts_*.txt
```

---

## How It Works

### Execution Flow

```
User Input (topic, tone)
         │
         ▼
ResearchAgent ──▶ Tavily API (1000/mo free)
         │
         ▼
Orchestrator (specialized agents)
         │
         ▼
QA Agent (validation + security)
         │
         ▼
Article + Social Posts (output)
```

### Features

| Feature | Description |
|---------|-------------|
| **Web Research** | Automatic information gathering with Tavily API |
| **24h Cache** | Results cached for 24 hours |
| **Multi-agent** | Specialized agents for each task |
| **Quality Assurance** | Built-in validation and scoring |
| **Social Media** | Auto-generates posts for Twitter, LinkedIn, Instagram, Facebook |
| **Security Scan** | Detects sensitive content |

### Supported LLM Providers

| Provider | Model | Status |
|----------|-------|--------|
| Groq | Llama 3.3 70B | ✅ Default (free) |
| Google | Gemini 2.5 Flash | ✅ Optional |

---

## Troubleshooting

### Error: "No module named 'dotenv'"

**Solution:**
```bash
pip install python-dotenv
```

### Error: "GROQ_API_KEY not found"

Verify `.env` file exists and contains your API key.

### Error: "Rate limit exceeded"

- Wait 1 minute for Groq
- For Tavily: wait until next month (1000 free searches/month)

---

## Update Project

```bash
git pull origin main
```

---

## License

MIT

---

## For Resume

**AI Content Automation System** - Python platform that generates articles with AI using multi-agent architecture (research, QA, social media). Integrates Tavily API for web research and creates posts for Twitter, LinkedIn, Instagram, and Facebook.
