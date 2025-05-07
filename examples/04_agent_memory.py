"""
04_代理記憶 - 讓代理記住並使用資訊
04_agent_memory - Enable agents to remember and utilize information

這個範例示範如何:
- 設置代理的記憶功能
- 儲存和檢索資訊
- 讓代理使用上下文資訊提升回應品質

This example demonstrates how to:
- Set up memory capabilities for agents
- Store and retrieve information
- Enable agents to use contextual information to enhance responses
"""

import asyncio
from typing import Dict, Any
from semantic_kernel.agents import ChatCompletionAgent

from utils.common import create_openai_client, create_chat_service, print_agent_response


class UserProfile:
    """用戶個人資料類 - 模擬用戶數據存儲"""
    
    def __init__(self, user_id: str, name: str, preferences: Dict[str, Any]):
        self.user_id = user_id
        self.name = name
        self.preferences = preferences


class SimpleMemory:
    """簡單的記憶儲存系統 - 使用字典存儲資訊"""
    
    def __init__(self):
        self.collections = {}
    
    def create_collection(self, collection_name: str):
        """創建一個新的記憶集合"""
        if collection_name not in self.collections:
            self.collections[collection_name] = []
    
    async def save_information(self, collection: str, category: str, text: str):
        """儲存資訊到指定集合"""
        if collection not in self.collections:
            self.create_collection(collection)
        
        self.collections[collection].append({
            "category": category,
            "text": text
        })
    
    async def search(self, collection: str, query: str, limit: int = 3):
        """簡單地搜尋相關資訊（基於關鍵字匹配）"""
        if collection not in self.collections:
            return []
        
        # 將查詢拆分為關鍵詞
        keywords = query.lower().split()
        
        # 計算每個記憶項目與查詢的相關性分數
        scored_items = []
        for item in self.collections[collection]:
            score = 0
            text_lower = item["text"].lower()
            
            # 簡單評分：每個關鍵詞出現在文本中加一分
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
            
            if score > 0:  # 只返回至少匹配一個關鍵詞的項目
                scored_items.append((item, score))
        
        # 按分數排序並返回前 limit 個項目
        scored_items.sort(key=lambda x: x[1], reverse=True)
        return [item for item, _ in scored_items[:limit]]



async def setup_memory():
    """設置簡單的記憶系統並填充用戶資訊"""
    memory = SimpleMemory()
    collection_name = "user_preferences"
    
    # 儲存用戶偏好
    await memory.save_information(
        collection=collection_name,
        category="outdoor_activities",
        text="用戶偏好戶外活動，特別是登山和自行車。對自然風景較感興趣，而不是人造景點。"
    )
    
    await memory.save_information(
        collection=collection_name,
        category="food",
        text="用戶喜歡亞洲料理，特別是日本菜和泰國菜。對辛辣食物有較高接受度。偏好低碳水化合物的飲食方式。"
    )
    
    await memory.save_information(
        collection=collection_name,
        category="accommodation",
        text="用戶傾向於選擇中等價位的飯店，重視清潔度和位置便利性。通常不選擇豪華住宿，但希望有舒適的床鋪和私人浴室。"
    )
    
    return memory, collection_name





async def main():
    # 設置客戶端和記憶體
    client = create_openai_client()
    chat_service = create_chat_service(client)
    memory, collection_name = await setup_memory()
    
    
    # 創建用戶資料
    user = UserProfile(
        user_id="user1",
        name="王小明",
        preferences={
            "outdoor_activities": ["登山", "自行車"],
            "cuisine": ["日本菜", "泰國菜"],
            "accommodation": "中等價位，重視清潔和位置"
        }
    )
    
    # 創建帶有記憶功能的代理
    memory_agent = ChatCompletionAgent(
        service=chat_service,
        name="personal_travel_advisor",
        description="一個能夠記住用戶偏好並提供個性化建議的旅遊顧問",
        instructions=f"""
        你是 {user.name} 的個人旅遊顧問。
        
        在回答問題時，請考慮用戶的已知偏好和興趣。
        使用記憶功能來檢索與用戶問題相關的偏好資訊。
        
        提供個性化的、具體的建議，並解釋你的推薦與用戶偏好的關聯。
        保持友好且專業的語氣，就像一個了解用戶喜好的長期旅遊顧問。
        """
    )
    
    # 定義一個函數來查詢記憶並增強提示
    async def query_with_memory(query: str):
        """使用記憶功能增強查詢"""
        # 從記憶中檢索相關資訊
        results = await memory.search(
            collection=collection_name,
            query=query,
            limit=3
        )
        
        # 準備上下文資訊
        context = ""
        if results:
            context = "用戶資訊:\n"
            for result in results:
                context += f"- {result.text}\n"
        
        # 將上下文與原始查詢結合
        enhanced_query = f"{context}\n問題: {query}\n請基於以上用戶資訊，提供個性化回答:"
        return enhanced_query
    
    # 與帶有記憶功能的代理互動
    
    # 第一個問題 - 包含記憶上下文
    query1 = await query_with_memory("我週末想去戶外活動，有什麼推薦嗎？")
    thread = await print_agent_response(
        memory_agent,
        query1
    )
    
    # 第二個問題 - 包含記憶上下文
    query2 = await query_with_memory("我到台北旅遊，有什麼餐廳推薦？")
    thread = await print_agent_response(
        memory_agent,
        query2,
        thread
    )
    
    # 第三個問題 - 不使用記憶，直接詢問（對比效果）
    await print_agent_response(
        memory_agent,
        "請推薦台北的住宿選擇",
        thread
    )
    
    # 第四個問題 - 使用記憶（對比效果）
    query4 = await query_with_memory("請推薦台北的住宿選擇")
    await print_agent_response(
        memory_agent,
        query4,
        thread
    )
    
    print("\n✅ 代理記憶範例完成!")
    print("-" * 50)
    print("這個範例展示了如何使用記憶系統來增強代理的回應。")
    print("注意觀察代理如何根據用戶的已知偏好提供個性化建議。")


if __name__ == "__main__":
    asyncio.run(main())
