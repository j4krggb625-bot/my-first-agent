#!/usr/bin/env python3
# chat_with_memory.py —— 第二个 Agent（带"记忆"）
# 在第一个 chat.py 基础上，加了一样东西：对话历史。
#
# 核心原理（必懂）：
#   大模型 API 本身是"金鱼脑"——每次调用都忘了上一句。
#   所谓"记忆"，是【你的代码】把聊过的每一轮攒进 messages 列表，
#   每次发请求时把【整段历史】一起发给模型，它才"显得"记得。
#
# 对比 chat.py：
#   chat.py  → 每次只发 [system, 当前这一句]      → 上一句转头就忘
#   本脚本   → 每次发 [system, 第1句, 回答1, 第2句, 回答2, ...] → 记得上下文

import urllib.request
import urllib.error
import json
import os

API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
API_KEY = os.getenv("DASHSCOPE_API_KEY")


def ask(messages: list) -> str:
    """把【完整对话历史】发给模型，返回这次的回答。"""
    payload = {
        "model": "qwen-plus",
        "messages": messages,   # 注意：这里传的是"整个历史"，不是单句
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
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    return result["choices"][0]["message"]["content"]


def main():
    if not API_KEY:
        print("⚠️ 没找到密钥。请先设置环境变量 DASHSCOPE_API_KEY（看 README.md）。")
        return

    # ★ 记忆的核心：用一个列表，把每一轮对话都存下来
    messages = [
        {"role": "system", "content": "你是一个乐于助人的中文助手，请记住用户前面说过的话。"}
    ]

    print("🤖 带记忆的 Agent（输入 exit 退出）")
    while True:
        try:
            q = input("你> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if q.lower() == "exit":
            break
        if not q:
            continue

        # 1) 把用户这句，追加进历史
        messages.append({"role": "user", "content": q})
        try:
            # 2) 把【带着历史】的整段发给模型
            answer = ask(messages)
            # 3) 把模型的回答也追加进历史——这样下一轮它才看得到
            messages.append({"role": "assistant", "content": answer})
            print("Agent>", answer, "\n")
        except urllib.error.HTTPError as e:
            print("调用失败：", e.read().decode("utf-8", "ignore"))


if __name__ == "__main__":
    main()
