"""
06_聊天代理 - 創建對話式 AI 體驗
06_chat_agent - Creating conversational AI experiences

這個範例示範如何:
- 建立進階的對話式代理
- 管理聊天歷史和上下文
- 處理複雜的多回合對話

This example demonstrates how to:
- Build advanced conversational agents 
- Manage chat history and context
- Handle complex multi-turn conversations
"""

import asyncio
from typing import Dict, List, Optional
import re

from semantic_kernel.agents import ChatCompletionAgent, ChatHistoryAgentThread
from semantic_kernel.contents import (
    StreamingTextContent, TextContent, 
    FunctionCallContent, FunctionResultContent
)
from semantic_kernel.functions import kernel_function

from utils.common import create_openai_client, create_chat_service


class PersonalAssistant:
    """個人助理類 - 實現具有對話式功能的智能助手"""
    
    def __init__(self, chat_service):
        """初始化個人助理及其功能"""
        self.chat_service = chat_service
        
        # 創建個人助理代理
        self.agent = ChatCompletionAgent(
            service=self.chat_service,
            name="助理",
            description="一個有用的個人助理代理，可以聊天和執行任務",
            instructions="""
            你是一個友好且有能力的個人助理。你可以幫助用戶進行對話，回答問題，並協助各種任務。
            
            請遵循以下指南:
            1. 保持尊重和專業的態度
            2. 提供有用且準確的信息
            3. 使用適當的工具來回應用戶請求
            4. 在不確定時，坦率承認並提出澄清問題
            5. 記住對話上下文，避免不必要地重複信息
            
            你有幫助用戶設置提醒、計算數學表達式、查找信息等能力。
            使用你可用的函數來提供最佳幫助。
            """,
            plugins=[self]  # 將自身作為插件，提供功能給代理使用
        )
        
        # 儲存當前的對話線程
        self.thread: Optional[ChatHistoryAgentThread] = None
        
        # 模擬的提醒列表
        self.reminders: List[Dict[str, str]] = []
    
    @kernel_function(description="設置一個新的提醒")
    def set_reminder(
        self, 
        task: str, 
        time: str
    ) -> str:
        """設置一個在特定時間提醒用戶做某事的提醒。"""
        # 在實際應用中，這會與日曆或提醒系統集成
        reminder_id = len(self.reminders) + 1
        self.reminders.append({
            "id": str(reminder_id),
            "task": task,
            "time": time
        })
        return f"已設置提醒：在 {time} 提醒你 {task}。提醒 ID: {reminder_id}"
    
    @kernel_function(description="獲取所有當前提醒")
    def list_reminders(self) -> str:
        """列出所有已設置的提醒。"""
        if not self.reminders:
            return "目前沒有設置任何提醒。"
        
        result = "當前提醒列表:\n"
        for i, reminder in enumerate(self.reminders, 1):
            result += f"{i}. 在 {reminder['time']} 提醒：{reminder['task']}\n"
        return result
    
    @kernel_function(description="刪除指定 ID 的提醒")
    def delete_reminder(self, id: str) -> str:
        """刪除指定 ID 的提醒。"""
        id_to_delete = id.strip()
        
        # 處理删除全部的情况
        if id_to_delete.lower() in ["all", "全部"]:
            count = len(self.reminders)
            self.reminders = []
            return f"已刪除所有 {count} 個提醒。"
        
        # 嘗試將輸入轉換為數字
        try:
            id_num = int(id_to_delete)
            if 1 <= id_num <= len(self.reminders):
                deleted = self.reminders.pop(id_num - 1)
                return f"已刪除提醒：在 {deleted['time']} 提醒 {deleted['task']}"
            else:
                return f"找不到 ID 為 {id_to_delete} 的提醒。"
        except ValueError:
            return f"無效的提醒 ID: {id_to_delete}。請提供有效的數字 ID。"
    
    @kernel_function(description="計算數學表達式")
    def calculate(self, expression: str) -> str:
        """計算數學表達式並返回結果。支援基本算術運算。"""
        # 清理表達式，僅保留允許的字符
        cleaned_expr = re.sub(r'[^0-9+\-*/().%\s]', '', expression)
        
        try:
            # 使用 Python eval 計算表達式 (在生產環境中應該使用更安全的方法)
            result = eval(cleaned_expr)
            return f"計算結果: {expression} = {result}"
        except Exception as e:
            return f"計算錯誤: {str(e)}"
    
    async def chat(self, user_message: str) -> None:
        """處理用戶消息並顯示代理響應"""
        print(f"\n👤 用戶: {user_message}\n")
        print(f"🤖 助理: ", end="")
        
        # 追踪是否正在處理函數調用
        is_function_call = False
        function_name = None
        function_args = {}
        
        # 與代理互動
        async for response in self.agent.invoke_stream(
            messages=user_message,
            thread=self.thread
        ):
            # 更新線程
            self.thread = response.thread
            
            # 處理不同類型的內容
            for item in response.items:
                # 處理文本內容
                if isinstance(item, (TextContent, StreamingTextContent)) and hasattr(item, "text"):
                    print(item.text, end="", flush=True)
                
                # 處理函數調用
                elif isinstance(item, FunctionCallContent):
                    is_function_call = True
                    if item.function_name:
                        function_name = item.function_name
                    
                    if isinstance(item.arguments, str) and item.arguments.strip():
                        # 簡單起見，假設參數是 JSON 格式的字串
                        try:
                            for k, v in eval(f"dict({item.arguments})").items():
                                function_args[k] = v
                        except:
                            # 非標準格式的參數，直接添加
                            function_args = {"raw_args": item.arguments}
                
                # 處理函數結果
                elif isinstance(item, FunctionResultContent) and is_function_call and function_name:
                    # 重置函數調用標記
                    is_function_call = False
                    function_name = None
                    function_args = {}
        
        print("\n" + "-" * 50)


async def main():
    """主函數 - 展示聊天代理功能"""
    print("🚀 聊天代理範例")
    print("-" * 50)
    
    # 步驟 1: 設置客戶端和服務
    print("步驟 1: 設置 OpenAI 客戶端和聊天服務")
    client = create_openai_client()
    chat_service = create_chat_service(client, model="gpt-3.5-turbo")
    
    # 步驟 2: 創建個人助理
    print("步驟 2: 創建個人助理")
    assistant = PersonalAssistant(chat_service)
    
    # 步驟 3: 演示多回合對話
    print("\n步驟 3: 開始與助理對話\n")
    
    # 模擬用戶與助理的多回合對話
    conversation = [
        "你好，你能做什麼？",
        "請幫我設置一個提醒，明天早上9點提醒我參加會議",
        "列出我所有的提醒",
        "計算 (15 * 24) + 7",
        "刪除第一個提醒",
        "列出所有提醒",
        "謝謝你的幫助!"
    ]
    
    for message in conversation:
        await assistant.chat(message)
        # 暫停一下，讓用戶有時間閱讀回應
        await asyncio.sleep(1)
    
    print("\n✅ 聊天代理範例完成!")
    print("-" * 50)
    print("這個範例展示了如何創建對話式代理，維護對話上下文，")
    print("並實現功能工具使用，例如設置提醒和計算表達式。")
    print("在實際應用中，你可以擴展這些功能，例如連接到真實的日曆系統或其他API。")


if __name__ == "__main__":
    asyncio.run(main())
