"""
02_簡單代理 - 創建基本的 AI 代理
02_simple_agent - Creating a basic AI agent

這個範例示範如何:
- 創建一個基本的 AI 代理
- 設定代理的指示和目標
- 與代理進行交互

This example demonstrates how to:
- Create a basic AI agent
- Set agent instructions and goals
- Interact with the agent
"""

import asyncio
from semantic_kernel.agents import ChatCompletionAgent

from utils.common import create_openai_client, create_chat_service, print_agent_response

#  設置客戶端和服務
client = create_openai_client()
chat_service = create_chat_service(client)

# 創建一個簡單的代理
agent = ChatCompletionAgent(
    service=chat_service,
    name="assistant",
    description="一個樂於助人的助手，能夠回答用戶問題並提供幫助。",
    instructions="""
    你是一個友好且樂於助人的 AI 助手。
    請遵循以下指南:
    
    1. 提供簡潔明了的回答
    2. 如果不確定答案，請說你不知道
    3. 對敏感話題保持中立
    4. 優先考慮用戶的安全和隱私
    5. 使用友好、專業的語氣
    """
)

async def main():
    
    # 與代理交互
    
    # 第一個問題
    thread = await print_agent_response(
        agent,
        "你能告訴我 Semantic Kernel 是什麼嗎？"
    )
    
    # 第二個問題 (使用相同的對話線程)
    thread = await print_agent_response(
        agent,
        "它與其他 AI 框架有什麼不同？",
        thread
    )
    
    # 第三個問題 (使用相同的對話線程)
    await print_agent_response(
        agent,
        "給我一個簡單的例子說明它如何工作",
        thread
    )
    
    print("\n✅ 簡單代理範例完成!")


if __name__ == "__main__":
    asyncio.run(main())
