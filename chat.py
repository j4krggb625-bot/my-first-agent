#!/usr/bin/env python3
# chat.py —— 你的第一个 Agent 雏形
# 功能：从命令行读你输入的问题，发给大模型 API，打印它返回的回答
#
# 对应你学到的三层：
#   输入  → 你在终端打的问题（user message）
#   处理  → 请求发给大模型 API，模型在云端"思考"
#   输出  → 模型返回的文字，打印出来
#
# 注意：密钥从环境变量读，不要写进代码里（好习惯从第一天养成）

import urllib.request
import urllib.error
import json
import os

# DeepSeek 兼容 OpenAI 接口；想换 Kimi / 通义 / OpenAI，只改这一行 URL 和对应的密钥名
API_URL = "https://api.deepseek.com/chat/completions"
API_KEY = os.getenv("DEEPSEEK_API_KEY")


def ask(question: str) -> str:
    """把问题发给模型，返回模型的回答（这就是一次 输入→处理→输出）。"""
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一个乐于助人的中文助手。"},
            {"role": "user", "content": question},
        ],
        "temperature": 0.7,
    }

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        },
        method="POST",
    )

    # 发送请求：这一步模型在"处理"
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    # 取出模型的"输出"
    return result["choices"][0]["message"]["content"]


def main():
    if not API_KEY:
        print("⚠️ 没找到密钥。请先设置环境变量 DEEPSEEK_API_KEY（看 README.md）。")
        return

    print("🤖 我的第一个 Agent（输入 exit 退出）")
    while True:
        try:
            q = input("你> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if q.lower() == "exit":
            break
        if not q:
            continue
        try:
            answer = ask(q)
            print("Agent>", answer, "\n")
        except urllib.error.HTTPError as e:
            print("调用失败：", e.read().decode("utf-8", "ignore"))


if __name__ == "__main__":
    main()
