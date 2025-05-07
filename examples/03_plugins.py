"""
03_外掛系統 - 擴展代理功能
03_plugins - Extending agent capabilities with plugins

這個範例示範如何:
- 創建自定義外掛 (Plugins)
- 讓代理使用外掛提供的功能
- 結合內置和自定義函數

This example demonstrates how to:
- Create custom plugins
- Enable agents to use functionality from plugins
- Combine native and custom functions
"""

import asyncio
import random
from typing import Annotated
from datetime import datetime

from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import kernel_function

from utils.common import create_openai_client, create_chat_service, print_agent_response


class WeatherPlugin:
    """天氣插件：提供天氣資訊相關功能。

    這個插件展示了如何創建能夠被代理使用的外部功能。
    天氣資料是模擬的，僅用於演示目的。
    """

    def __init__(self):
        # 模擬城市和天氣狀況
        self.cities = ["台北", "高雄", "台中", "花蓮", "嘉義", "新竹"]
        self.conditions = ["晴天", "多雲", "雨天", "大雨", "雷陣雨", "陰天"]
        self.temperatures = {
            "晴天": (25, 35),
            "多雲": (22, 30),
            "雨天": (20, 27),
            "大雨": (18, 25),
            "雷陣雨": (22, 28),
            "陰天": (20, 28),
        }

    @kernel_function(description="獲取指定城市的當前天氣狀況")
    def get_current_weather(self, city: Annotated[str, "要查詢的城市名稱"]) -> str:
        """獲取指定城市的當前天氣狀況，包括溫度和天氣情況。"""
        if city not in self.cities:
            return f"抱歉，我們沒有 {city} 的天氣資訊。可用的城市有: {', '.join(self.cities)}"

        condition = random.choice(self.conditions)
        temp_range = self.temperatures[condition]
        temperature = random.randint(temp_range[0], temp_range[1])

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        return f"{city}的當前天氣（{current_time}）：{condition}，溫度{temperature}°C"

    @kernel_function(description="獲取指定城市的天氣預報")
    def get_weather_forecast(self, city: Annotated[str, "要查詢的城市名稱"]) -> str:
        """獲取指定城市未來三天的天氣預報。"""
        if city not in self.cities:
            return f"抱歉，我們沒有 {city} 的天氣資訊。可用的城市有: {', '.join(self.cities)}"

        forecast = []
        for i in range(3):
            condition = random.choice(self.conditions)
            temp_range = self.temperatures[condition]
            high = random.randint(temp_range[0], temp_range[1])
            low = high - random.randint(3, 8)
            day = (datetime.now().day + i) % 30 + 1
            month = datetime.now().month
            forecast.append(f"{month}月{day}日: {condition}，{low}°C - {high}°C")

        return f"{city}的天氣預報：\n" + "\n".join(forecast)


class TravelInfoPlugin:
    """旅遊資訊插件：提供旅遊相關資訊。

    這個插件提供城市景點和交通方式等旅遊資訊。
    資訊是靜態的，僅用於演示目的。
    """

    def __init__(self):
        # 景點資料庫（簡化版）
        self.attractions = {
            "台北": [
                "台北101",
                "國立故宮博物院",
                "西門町",
                "饒河夜市",
                "陽明山國家公園",
            ],
            "高雄": ["愛河", "六合夜市", "駁二藝術特區", "旗津海岸", "蓮池潭"],
            "台中": ["臺中國家歌劇院", "高美濕地", "逢甲夜市", "彩虹眷村", "東海大學"],
            "花蓮": ["太魯閣國家公園", "七星潭", "清水斷崖", "花蓮夜市", "瑞穗牧場"],
            "嘉義": ["阿里山國家風景區", "嘉義公園", "文化路夜市", "奮起湖", "蘭潭"],
            "新竹": [
                "新竹科學園區",
                "新竹市立動物園",
                "青草湖",
                "新竹城隍廟",
                "十八尖山",
            ],
        }

        # 交通資訊
        self.transportation = {
            "台北": "捷運系統、公車、YouBike、計程車",
            "高雄": "捷運系統、公車、輕軌、渡輪、計程車",
            "台中": "公車、計程車、YouBike",
            "花蓮": "公車、計程車、租車",
            "嘉義": "公車、計程車、租車",
            "新竹": "公車、計程車、YouBike",
        }

    @kernel_function(description="獲取指定城市的熱門景點")
    def get_attractions(self, city: Annotated[str, "要查詢的城市名稱"]) -> str:
        """獲取指定城市的熱門旅遊景點列表。"""
        if city not in self.attractions:
            return f"抱歉，我們沒有 {city} 的景點資訊。可用的城市有: {', '.join(self.attractions.keys())}"

        attractions_list = self.attractions[city]
        return f"{city}的熱門景點：\n- " + "\n- ".join(attractions_list)

    @kernel_function(description="獲取指定城市的交通資訊")
    def get_transportation_info(self, city: Annotated[str, "要查詢的城市名稱"]) -> str:
        """獲取指定城市的主要交通方式。"""
        if city not in self.transportation:
            return f"抱歉，我們沒有 {city} 的交通資訊。可用的城市有: {', '.join(self.transportation.keys())}"

        return f"{city}的主要交通方式：{self.transportation[city]}"


class LanguageHelper:
    """語言助手：提供語言翻譯和格式化功能。

    這個插件展示了較簡單的純文字處理功能。
    """

    @kernel_function(description="將英文翻譯成中文")
    def translate_to_chinese(
        self, english_text: Annotated[str, "要翻譯的英文文本"]
    ) -> str:
        """這只是一個模擬翻譯功能，真實應用中應使用翻譯 API。"""
        # 注意：在實際應用中，這裡會調用專業的翻譯 API
        # 此處僅作示範，返回文本說明
        return f'這是一個翻譯示例。在實際應用中，"{english_text}"將被翻譯成中文。'

    @kernel_function(description="格式化文本為大寫")
    def format_uppercase(self, text: Annotated[str, "要格式化的文本"]) -> str:
        """將文本轉換為大寫。"""
        return text.upper()


# 設置客戶端和服務
client = create_openai_client()
chat_service = create_chat_service(client)

# 創建插件實例
weather_plugin = WeatherPlugin()
travel_plugin = TravelInfoPlugin()
language_helper = LanguageHelper()

# 創建代理並添加插件
agent = ChatCompletionAgent(
    service=chat_service,
    name="Travel_Consultant",
    description="一個能夠提供天氣和旅遊資訊的 AI 助手",
    instructions="""
        你是一個專業的旅遊顧問，可以提供台灣各城市的天氣和旅遊資訊。
        請使用提供給你的工具來回答關於:
        - 特定城市的天氣狀況和預報
        - 城市景點推薦
        - 當地交通選項
        
        當被問及這些相關問題時，請利用可用的函數來獲取最新資訊。
        提供友好、信息豐富的回答，並根據天氣狀況提供適當的活動建議。
        """,
    plugins=[weather_plugin, travel_plugin, language_helper],
)


async def main():
    # 第一個問題 - 測試天氣插件
    thread = await print_agent_response(agent, "台北現在天氣怎麼樣？")

    # 第二個問題 - 測試旅遊插件
    thread = await print_agent_response(agent, "台中有哪些值得去的景點？", thread)

    # 第三個問題 - 綜合使用多個插件
    await print_agent_response(
        agent, "我想去高雄玩兩天，請給我一些建議，包括景點、交通和天氣預報。", thread
    )

    print("\n✅ 外掛系統範例完成!")
    print("-" * 50)
    print("這個範例展示了如何創建自定義插件並讓代理使用它們來獲取外部資訊。")
    print("你可以根據自己的需求擴展這些插件，例如連接真實的 API、資料庫或其他服務。")


if __name__ == "__main__":
    asyncio.run(main())
