#!/usr/bin/env python3
# chat_with_tools.py —— 第三个 Agent（带"工具"）
#
# 对照你视频里的架构看：本文件分两大块
#   【TOOL 工具】   = 模型的手（Python 函数，真正去干活的）
#   【HARNESS 调度层】= 夹在"模型"和"外界"中间的循环（传话、记历史、执行工具）
# 模型本身只是个"裸大脑"（输入文字→输出文字），其余全是 HARNESS 在管。

import urllib.request
import urllib.error
import json
import os

API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
API_KEY = os.getenv("DASHSCOPE_API_KEY")


# ============================================================
# 【TOOL 工具】—— Agent 的"手"，一个普通 Python 函数
# 模型碰不了文件，是 HARNESS 调用它、把结果拿去喂给模型
# ============================================================
def read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()[:4000]   # 最多读 4000 字，避免太长
    except Exception as e:
        return f"读文件失败：{e}"


# 把工具"说明书"告诉模型：名字、干嘛用、要什么参数
# （模型靠这段描述决定"什么时候该点名调用这个工具"）
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取本地文本文件的内容，用于回答用户关于该文件的问题",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件路径，例如 notes.txt"}
                },
                "required": ["path"],
            },
        },
    }
]


# ============================================================
# 【HARNESS 调度层】—— 负责"发请求给模型 / 收模型的回复"
# 这一层不含智能，只负责搬运：把 messages 打包发给模型，把回复拆回来
# ============================================================
def call_model(messages: list, use_tools: bool = False) -> dict:
    payload = {"model": "qwen-plus", "messages": messages, "temperature": 0.7}
    if use_tools:
        payload["tools"] = TOOLS
        payload["tool_choice"] = "auto"   # 让模型自己决定要不要调用工具
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
        return json.loads(resp.read().decode("utf-8"))


# ============================================================
# 【HARNESS 调度层】—— 主循环：模型 ↔ 工具 的交互就发生在这里
#   ① 把用户的话 + 历史塞进 messages，发给模型
#   ② 模型回包里若带 tool_calls（"我要调工具"），HARNESS 就去执行
#   ③ 把工具结果以 role:"tool" 塞回 messages，再问模型一次 → 最终答案
# ============================================================
def main():
    if not API_KEY:
        print("⚠️ 没找到密钥。请先设置环境变量 DASHSCOPE_API_KEY（看 README.md）。")
        return

    # 记忆：用一个列表存所有回合（系统提示 + 每轮对话），每次都整段发给模型
    messages = [
        {"role": "system",
         "content": "你是一个乐于助人的中文助手。当用户问到文件内容时，请调用 read_file 工具读取后再回答。"}
    ]

    print("🤖 带工具的 Agent（输入 exit 退出；试试问：notes.txt 里写了什么？）")
    while True:                              # ← HARNESS 主循环：反复"问模型→看回复"
        try:
            q = input("你> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if q.lower() == "exit":
            break
        if not q:
            continue

        messages.append({"role": "user", "content": q})   # 记忆：用户这句入栈

        # ① 第一轮问模型（带上工具说明书，允许它调工具）
        resp = call_model(messages, use_tools=True)
        msg = resp["choices"][0]["message"]

        # ② "听到"：模型回包里有没有 tool_calls 字段？有 = 它要调工具
        if msg.get("tool_calls"):
            messages.append(msg)   # 把模型的"调用意图"也记进历史（必需）
            for tc in msg["tool_calls"]:
                fn = tc["function"]
                args = json.loads(fn["arguments"])
                result = read_file(args.get("path", ""))   # ← 真正执行【TOOL 工具】
                # 把工具执行结果塞回对话，role 必须是 "tool"，模型下一轮才看得到
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result,
                })
            # ③ 第二轮：带着工具结果再问模型，它才给出最终答案
            resp = call_model(messages, use_tools=False)
            answer = resp["choices"][0]["message"]["content"]
        else:
            answer = msg["content"]   # 没调工具，直接拿模型的普通回答

        messages.append({"role": "assistant", "content": answer})   # 记忆：回答入栈
        print("Agent>", answer, "\n")


if __name__ == "__main__":
    main()
