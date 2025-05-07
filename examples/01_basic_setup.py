"""
01_基本設置 - Semantic Kernel 入門範例
01_basic_setup - Getting started with Semantic Kernel

這個範例示範如何:
- 設置 Semantic Kernel 環境
- 創建一個基本的 AI 服務連接
- 執行一個簡單的內容生成請求

This example demonstrates how to:
- Set up the Semantic Kernel environment
- Create a basic AI service connection
- Execute a simple content generation request
"""

import asyncio
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import (
    OpenAIChatCompletion,
    OpenAIChatPromptExecutionSettings,
)
from semantic_kernel.contents import ChatHistory
from semantic_kernel.functions import KernelArguments

from utils.common import create_openai_client

# 設置環境和 OpenAI 客戶端
client = create_openai_client()

# 創建 Kernel (Semantic Kernel 的核心組件)
kernel = Kernel()

# 添加 AI 服務到 Kernel
chat_service = OpenAIChatCompletion(
    ai_model_id="openai/gpt-4.1-mini", async_client=client
)
request_settings = OpenAIChatPromptExecutionSettings(
    service_id="chat_completion", max_tokens=2000, temperature=0.7, top_p=0.8
)

kernel.add_service(chat_service)


# 設置聊天歷史
system_message = "你是一個樂於助人的助手，能夠回答用戶問題並提供幫助。"
chat_history = ChatHistory(system_message=system_message)

chat_function = kernel.add_function(
    plugin_name="ChatBot",
    function_name="Chat",
    prompt="解釋 Semantic Kernel 是什麼，以及它對於 AI 應用開發的價值，請用 3-5 個簡短段落回答。",
    template_format="semantic-kernel",
)

async def chat():
    try:
        user_input = input("User:> ")
    except KeyboardInterrupt:
        print("\n\nExiting chat...")
        return False
    except EOFError:
        print("\n\nExiting chat...")
        return False

    if user_input == "exit":
        print("\n\nExiting chat...")
        return False

    # Get the chat message content from the chat completion service.
    kernel_arguments = KernelArguments(
        settings=request_settings,
        # Use keyword arguments to pass the chat history and user input to the kernel function.
        chat_history=chat_history,
        user_input=user_input,
    )

    answer = await kernel.invoke(plugin_name="ChatBot", function_name="Chat", arguments=kernel_arguments)
    if answer:
        print(f"Mosscap:> {answer}")
        # Since the user_input is rendered by the template, it is not yet part of the chat history, so we add it here.
        chat_history.add_user_message(user_input)
        # Add the chat message to the chat history to keep track of the conversation.
        chat_history.add_message(answer.value[0])

    return True

async def main():
    chatting = True
    while chatting:
        chatting = await chat()


if __name__ == "__main__":
    asyncio.run(main())
