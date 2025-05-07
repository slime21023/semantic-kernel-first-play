"""
共用工具函數 - 提供所有範例使用的公共函數
Common utility functions for Semantic Kernel examples
"""

import os
from typing import Optional, Dict
from dotenv import load_dotenv
from openai import AsyncOpenAI

from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.agents import ChatCompletionAgent, ChatHistoryAgentThread


def setup_env_vars() -> Dict[str, str]:
    """
    載入環境變數
    Load environment variables from .env file

    Returns:
        Dict[str, str]: 包含環境變數的字典
    """
    load_dotenv()
    return {"github_token": os.environ.get("GITHUB_TOKEN")}


def create_openai_client(
    api_key: Optional[str] = None, 
    base_url: Optional[str] = "https://models.github.ai/inference"
) -> AsyncOpenAI:
    """
    創建基本的 OpenAI API 客戶端
    Create a basic OpenAI API client

    Args:
        api_key (Optional[str], optional): OpenAI API 金鑰. 預設為 None，會從環境變數中獲取
        base_url (Optional[str], optional): API 基礎 URL. 預設為 None，使用 OpenAI 默認 URL

    Returns:
        AsyncOpenAI: 非同步的 OpenAI 客戶端
    """
    if api_key is None:
        env_vars = setup_env_vars()
        api_key = env_vars.get("github_token")

    # 使用標準 OpenAI API
    return AsyncOpenAI(api_key=api_key, base_url=base_url)


def create_chat_service(
    client: AsyncOpenAI, model: str = "openai/gpt-4.1-mini"
) -> OpenAIChatCompletion:
    """
    創建聊天完成服務
    Create a chat completion service

    Args:
        client (AsyncOpenAI): OpenAI 客戶端
        model (str, optional): 模型 ID. 預設為 "gpt-4o-mini"

    Returns:
        OpenAIChatCompletion: 聊天完成服務
    """
    return OpenAIChatCompletion(ai_model_id=model, async_client=client)


async def print_agent_response(
    agent: ChatCompletionAgent,
    messages: str,
    thread: Optional[ChatHistoryAgentThread] = None,
):
    """
    印出代理回應，用於簡單的示範
    Print agent response for simple demonstrations

    Args:
        agent (ChatCompletionAgent): 聊天代理
        messages (str): 用戶訊息
        thread (Optional[ChatHistoryAgentThread], optional): 聊天線程. 預設為 None

    Returns:
        ChatHistoryAgentThread: 更新後的聊天線程
    """
    print(f"\n👤 用戶: {messages}\n")

    response_parts = []

    async for response in agent.invoke_stream(messages=messages, thread=thread):
        thread = response.thread
        for item in response.items:
            if hasattr(item, "text"):
                print(f"{item.text}", end="", flush=True)
                response_parts.append(item.text)

    print("\n" + "-" * 50)
    return thread
