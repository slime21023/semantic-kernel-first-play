"""
05_代理協作 - 多代理系統協同工作
05_orchestration - Multiple agents working together

這個範例示範如何:
- 創建多個專門的代理
- 設計代理之間的協作流程
- 實現一個簡單的多代理系統

This example demonstrates how to:
- Create multiple specialized agents
- Design collaboration workflow between agents
- Implement a simple multi-agent system
"""

import asyncio
import json
from typing import Dict, List, Any
from dataclasses import dataclass
from semantic_kernel.agents import ChatCompletionAgent

from utils.common import create_openai_client, create_chat_service


@dataclass
class TravelPlan:
    """旅行計劃數據類"""
    destination: str
    start_date: str
    end_date: str
    activities: List[str]
    accommodation: str
    transportation: str
    budget_estimate: str
    notes: str = ""


class AgentOrchestrator:
    """代理協作協調器 - 管理多個代理之間的協作"""
    
    def __init__(self, chat_service):
        """初始化協調器並創建專門的代理"""
        self.chat_service = chat_service
        
        # 創建研究代理 - 負責收集目的地資訊
        self.research_agent = ChatCompletionAgent(
            service=self.chat_service,
            name="researcher",
            description="一個專門收集和分析旅遊目的地資訊的代理",
            instructions="""
            你是一位旅遊研究專家，負責提供關於旅遊目的地的詳細資訊。
            
            你的主要職責包括:
            1. 提供有關目的地的重要資訊（如文化、天氣、最佳旅遊季節等）
            2. 推薦值得訪問的景點和活動
            3. 提供當地交通選項的資訊
            4. 分析適合不同類型旅客的選項
            
            請提供詳細、準確且實用的資訊，以便旅行規劃師可以制定具體的旅行計劃。
            """
        )
        
        # 創建行程規劃代理 - 負責制定詳細行程
        self.planning_agent = ChatCompletionAgent(
            service=self.chat_service,
            name="planner",
            description="一個專門設計詳細旅行行程的代理",
            instructions="""
            你是一位專業的旅行行程規劃師，負責根據研究資料制定詳細的旅行計劃。
            
            你的主要職責包括:
            1. 創建日程安排，包括每天的活動和時間表
            2. 根據旅客偏好和預算推薦住宿選項
            3. 建議合適的交通方式
            4. 估算旅行預算
            
            根據提供的研究資訊和旅客需求，制定一個結構清晰、時間合理的行程。
            """
        )
        
        # 創建優化代理 - 負責根據用戶偏好優化行程
        self.optimization_agent = ChatCompletionAgent(
            service=self.chat_service,
            name="optimizer",
            description="一個專門根據用戶偏好優化旅行體驗的代理",
            instructions="""
            你是一位旅行體驗優化師，負責根據用戶的具體偏好定制和改進旅行計劃。
            
            你的主要職責包括:
            1. 根據用戶的興趣、飲食偏好和活動喜好調整行程
            2. 提出個性化建議以提升旅行體驗
            3. 確保行程在時間安排上合理且不會太匆忙
            4. 根據特殊要求（如家庭友好、無障礙需求等）進行調整
            
            請確保最終計劃符合用戶的具體需求和期望。
            """
        )
    
    async def create_travel_plan(self, destination: str, dates: str, preferences: Dict[str, Any]) -> TravelPlan:
        """協調多個代理創建完整的旅行計劃"""
        print(f"\n🔍 研究代理正在收集關於 {destination} 的資訊...\n")
        
        # 步驟 1: 研究代理收集目的地資訊
        research_prompt = f"""
        請提供關於 {destination} 作為旅遊目的地的詳細資訊，包括:
        1. 主要景點和活動
        2. 當地交通選項
        3. 氣候和最佳旅遊季節（考慮到旅行日期: {dates}）
        4. 當地美食和特色
        5. 實用提示（語言、貨幣、文化禁忌等）
        
        以結構化且信息豐富的方式提供這些資訊。
        """
        
        research_response = ""
        async for response in self.research_agent.invoke_stream(messages=research_prompt):
            for item in response.items:
                if hasattr(item, "text"):
                    print(item.text, end="", flush=True)
                    research_response += item.text
        
        print("\n\n📝 行程規劃代理正在制定旅行計劃...\n")
        
        # 步驟 2: 將研究結果傳遞給行程規劃代理
        preferences_str = json.dumps(preferences, ensure_ascii=False)
        planning_prompt = f"""
        基於以下關於 {destination} 的研究資訊:
        
        {research_response}
        
        以及用戶的以下偏好:
        {preferences_str}
        
        請制定一個詳細的旅行計劃，包括:
        1. 從 {dates} 的每日行程安排
        2. 推薦的住宿選項
        3. 建議的交通方式
        4. 預算估算
        
        請以結構化格式提供行程，包括時間表和具體活動。
        """
        
        planning_response = ""
        async for response in self.planning_agent.invoke_stream(messages=planning_prompt):
            for item in response.items:
                if hasattr(item, "text"):
                    print(item.text, end="", flush=True)
                    planning_response += item.text
        
        print("\n\n✨ 體驗優化代理正在根據用戶偏好優化行程...\n")
        
        # 步驟 3: 將初步計劃傳遞給優化代理進行個性化調整
        preferences_details = "\n".join([f"- {k}: {v}" for k, v in preferences.items()])
        optimization_prompt = f"""
        以下是為前往 {destination} 在 {dates} 期間制定的初步旅行計劃:
        
        {planning_response}
        
        用戶有以下具體偏好:
        {preferences_details}
        
        請根據用戶偏好優化此行程。考慮:
        1. 活動是否符合用戶興趣
        2. 餐廳選擇是否符合飲食偏好
        3. 行程節奏是否適合用戶風格（輕鬆/緊湊）
        4. 預算是否符合用戶期望
        
        提供最終優化後的完整行程計劃。以 JSON 格式輸出最終計劃，包含以下欄位:
        destination, start_date, end_date, activities (列表), accommodation, transportation, budget_estimate, notes
        """
        
        optimization_response = ""
        async for response in self.optimization_agent.invoke_stream(messages=optimization_prompt):
            for item in response.items:
                if hasattr(item, "text"):
                    print(item.text, end="", flush=True)
                    optimization_response += item.text
        
        # 嘗試解析優化代理的 JSON 響應
        try:
            # 嘗試從響應中提取 JSON 部分
            json_start = optimization_response.find('{')
            json_end = optimization_response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = optimization_response[json_start:json_end]
                plan_data = json.loads(json_str)
                
                # 創建並返回 TravelPlan 對象
                return TravelPlan(
                    destination=plan_data.get("destination", destination),
                    start_date=plan_data.get("start_date", ""),
                    end_date=plan_data.get("end_date", ""),
                    activities=plan_data.get("activities", []),
                    accommodation=plan_data.get("accommodation", ""),
                    transportation=plan_data.get("transportation", ""),
                    budget_estimate=plan_data.get("budget_estimate", ""),
                    notes=plan_data.get("notes", "")
                )
            else:
                # 如果無法找到有效的 JSON，則返回含有完整響應的計劃
                return TravelPlan(
                    destination=destination,
                    start_date=dates.split("至")[0].strip() if "至" in dates else dates,
                    end_date=dates.split("至")[1].strip() if "至" in dates else "",
                    activities=["請參閱詳細響應"],
                    accommodation="請參閱詳細響應",
                    transportation="請參閱詳細響應",
                    budget_estimate="請參閱詳細響應",
                    notes=optimization_response
                )
        except Exception as e:
            print(f"\n⚠️ 無法解析 JSON 響應: {e}")
            # 如果解析失敗，則返回含有完整響應的計劃
            return TravelPlan(
                destination=destination,
                start_date=dates.split("至")[0].strip() if "至" in dates else dates,
                end_date=dates.split("至")[1].strip() if "至" in dates else "",
                activities=["請參閱詳細響應"],
                accommodation="請參閱詳細響應",
                transportation="請參閱詳細響應",
                budget_estimate="請參閱詳細響應",
                notes=optimization_response
            )


async def main():
    """主函數 - 展示多代理協作系統"""
    print("🚀 代理協作範例")
    print("-" * 50)
    
    # 步驟 1: 設置客戶端和服務
    print("步驟 1: 設置 OpenAI 客戶端和聊天服務")
    client = create_openai_client()
    chat_service = create_chat_service(client, model="gpt-3.5-turbo")
    
    # 步驟 2: 創建代理協調器
    print("步驟 2: 創建代理協調器")
    orchestrator = AgentOrchestrator(chat_service)
    
    # 步驟 3: 設置旅行計劃請求
    print("步驟 3: 設置旅行計劃請求")
    destination = "京都"
    dates = "2025年3月15日至3月20日"
    preferences = {
        "興趣": ["歷史文化", "傳統美食", "自然風景"],
        "活動風格": "中等強度，每天不超過3個主要景點",
        "預算": "中等（每天約6000-10000新台幣）",
        "飲食偏好": "喜歡嘗試當地料理，尤其是傳統美食",
        "住宿喜好": "乾淨舒適的中檔酒店或傳統旅館",
        "特殊要求": "希望體驗一次茶道和和服體驗"
    }
    
    # 步驟 4: 執行多代理協作流程創建旅行計劃
    print(f"\n步驟 4: 為 {destination} 創建旅行計劃")
    travel_plan = await orchestrator.create_travel_plan(destination, dates, preferences)
    
    # 步驟 5: 顯示最終結果
    print("\n\n🏁 最終旅行計劃:")
    print("-" * 50)
    print(f"🌍 目的地: {travel_plan.destination}")
    print(f"📅 日期: {travel_plan.start_date} 至 {travel_plan.end_date}")
    print(f"🏨 住宿: {travel_plan.accommodation}")
    print(f"🚗 交通: {travel_plan.transportation}")
    print(f"💰 預算: {travel_plan.budget_estimate}")
    print(f"📝 活動:")
    for activity in travel_plan.activities:
        print(f"  - {activity}")
    
    if travel_plan.notes and not travel_plan.notes.startswith("請參閱"):
        print(f"\n📌 備註: {travel_plan.notes}")
    
    print("\n✅ 代理協作範例完成!")
    print("-" * 50)
    print("這個範例展示了如何設計多個專門代理協同工作，每個代理負責特定任務。")
    print("透過協調流程，多個代理可以協作處理複雜任務，產生綜合性的結果。")


if __name__ == "__main__":
    asyncio.run(main())
