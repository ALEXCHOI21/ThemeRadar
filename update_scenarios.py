import os
import sys
import json
import time
import requests
import yfinance as yf
import pandas as pd
from dotenv import load_dotenv

# Load configuration
load_dotenv()

def run_ai_scenario_generation():
    """
    Fetch live market data for key sector leaders and invoke Gemini 2.0 Flash
    to generate data-driven next-sector rotation scenarios.
    """
    print("[AI Strategist] Gathering market intelligence...")
    leaders = {
        "NVDA": "GenAI Hardware",
        "AVGO": "Silicon Photonics/ASIC",
        "LLY": "Obesity/Diabetes",
        "NVO": "Obesity/Diabetes",
        "PLTR": "Defense/AI Software",
        "MSFT": "Hyperscaler/Cloud",
        "042700": "HBM Semiconductor",
        "257720": "K-Beauty Export",
        "012450": "K-Defense Export",
        "003670": "Secondary Battery Material"
    }
    
    market_context = []
    for sym, category in leaders.items():
        try:
            # KRX symbol auto-correction
            query_sym = sym
            if sym.isdigit() and len(sym) == 6:
                query_sym = f"{sym}.KS"
                
            ticker = yf.Ticker(query_sym)
            info = ticker.info
            if info:
                close = info.get("previousClose", 0.0)
                vol = info.get("volume", 0)
                market_cap = info.get("marketCap", 0)
                market_context.append(
                    f"- {sym} ({category}): Close Price {close}, Volume {vol}, Market Cap {market_cap}"
                )
        except Exception as e:
            print(f"[AI Strategist] Warning: Failed to query {sym} ({e})")

    context_str = "\n".join(market_context)
    
    # Acts as Chief Market Strategist at ChoiGPT Corp.
    prompt = f"""
당신은 'ChoiGPT Corp.'의 수석 시장 전략가(Chief Market Strategist)입니다.
현재 시장을 주도하고 있는 핵심 주도주들의 최신 거래 동향 및 수급 현황 데이터는 다음과 같습니다:

{context_str}

이 데이터를 바탕으로 대표님(Alex)의 거시적 투자 결정을 지원할 '초격차 다음 섹터 예측 시나리오(Sector Rotation Scenarios)' 3가지를 생성하십시오.

[작성 규칙]
1. 세련되고 전문적인 한국어 표기(전문 용어는 영어 병기)로 작성하십시오.
2. 찌라시와 시장 노이즈를 100% 배제하고, 현재 수급이 과열(Overheated)된 섹터의 물리적/공급망 병목 현상(Bottleneck) 분석을 통해 차기 수혜를 입을 섹터로의 순환매(Sector Rotation) 논리를 구체적으로 전개해야 합니다.
3. 핵심 수혜주 티커명(Predefined Tickers)을 정확하게 포함하십시오.
4. 반드시 아래 지정된 JSON 배열 구조로만 정확하게 반환해야 하며, 다른 텍스트 설명이나 코드 블록(```json 등)은 절대 출력하지 마십시오.

[JSON 출력 포맷]
[
  {{
    "title": "[시나리오 1] 시나리오 대제목 (예: AI 하드웨어 병목 ➡️ CPO 광통신 이동)",
    "description": "구체적 자금 순환매 논리 및 병목 현상 분석 내용",
    "stocks": "핵심 수혜주: 티커1, 티커2",
    "color": "#007aff"
  }},
  {{
    "title": "[시나리오 2] 시나리오 대제목",
    "description": "구체적 자금 순환매 논리 및 병목 현상 분석 내용",
    "stocks": "핵심 수혜주: 티커1, 티커2",
    "color": "#34c759"
  }},
  {{
    "title": "[시나리오 3] 시나리오 대제목",
    "description": "구체적 자금 순환매 논리 및 병목 현상 분석 내용",
    "stocks": "핵심 수혜주: 티커1, 티커2",
    "color": "#ff9500"
  }}
]
"""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[AI Strategist] Error: GEMINI_API_KEY is not configured. Falling back to default scenarios.")
        return False
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 1000
        }
    }
    
    for attempt in range(3):
        try:
            r = requests.post(url, json=payload, timeout=20)
            if r.status_code == 200:
                res_data = r.json()
                text_content = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                
                # Strip markdown code blocks if any exist
                if text_content.startswith("```"):
                    text_content = text_content.split("```")[1]
                    if text_content.startswith("json"):
                        text_content = text_content[4:]
                    text_content = text_content.strip()
                if text_content.endswith("```"):
                    text_content = text_content[:-3].strip()
                    
                parsed_json = json.loads(text_content)
                if isinstance(parsed_json, list) and len(parsed_json) == 3:
                    # Successfully parsed 3 scenarios
                    with open("scenarios.json", "w", encoding="utf-8") as f:
                        json.dump(parsed_json, f, ensure_ascii=False, indent=2)
                    print("[AI Strategist] Successfully updated scenarios.json with Gemini 2.0 Flash.")
                    return True
            else:
                print(f"[AI Strategist] API attempt {attempt+1} failed with status {r.status_code}: {r.text}")
        except Exception as e:
            print(f"[AI Strategist] Attempt {attempt+1} Error: {e}")
        time.sleep(2)
        
    print("[AI Strategist] Could not fetch AI generated scenarios. Retaining existing scenarios.")
    return False

if __name__ == "__main__":
    run_ai_scenario_generation()
