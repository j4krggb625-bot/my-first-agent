# my-first-agent

我的第一个 Agent 雏形：一个能在命令行里和大模型对话的 Python 脚本。

## 它做了什么

你输入一句话 → 脚本把这句话发给大模型 API → 模型返回回答，打印出来。
这就是你学过的 **输入 → 处理 → 输出**，只不过这次你看得见代码。

## 你需要准备

1. **Python 3.8+**（你电脑一般自带，命令行输入 `python3 --version` 检查）
2. **一个大模型 API Key**（推荐 DeepSeek，便宜，国内可达）

### 怎么拿到 DeepSeek Key

1. 打开 https://platform.deepseek.com 注册登录
2. 右上角 →「API Keys」→ 创建 Key（形如 `sk-xxxx`）
3. 首次充值约 ¥1–10 就能跑很多次（按 token 计费，很便宜）

> 想用 Kimi / 通义 / OpenAI 也行，接口都兼容，只改 `chat.py` 里的 `API_URL` 和密钥名。

## 怎么运行

先把密钥放进环境变量（Mac/Linux 终端）：

```bash
export DEEPSEEK_API_KEY="sk-你的key"
python3 chat.py
```

Windows（PowerShell）：

```powershell
$env:DEEPSEEK_API_KEY="sk-你的key"
python3 chat.py
```

然后就能对话了，输入 `exit` 退出。

## 怎么连到 GitHub（这周第 ① 件事）

1. 去 https://github.com 注册，新建一个空仓库，名字就叫 `my-first-agent`
2. 在本文件夹里执行：

```bash
git init
git add .
git commit -m "my first agent: 调用大模型 API 的对话脚本"
git branch -M main
git remote add origin https://github.com/你的用户名/my-first-agent.git
git push -u origin main
```

推上去之后，这个仓库就是你的**第一个作品集项目**——面试时能给人看"我会调 API、会写 Agent、会用 Git"。

## 进阶方向（学完基础后）

- 让 Agent 能「调用工具」（查天气、读文件）→ Function Calling
- 给它一个文档，让它基于文档回答 → RAG
- 把它做成网页或接口 → FastAPI + 部署
