#!/usr/bin/env python3
"""
調試環境部AQI API結構
"""

import os
import requests
import json

# 設定API金鑰
os.environ['MOENV_API_KEY'] = 'aeeee00c-6e01-4e17-b8dc-7ceee42facce'

def debug_moenv_api():
    """調試MOENV API"""
    api_key = os.getenv('MOENV_API_KEY')
    url = "https://data.moenv.gov.tw/api/v2/aqx_p_432"
    
    params = {
        'api_key': api_key,
        'format': 'JSON',
        'limit': 5  # 只獲取5筆資料測試
    }
    
    print(f"API URL: {url}")
    print(f"API Key: {api_key}")
    print(f"Params: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")
            
            if isinstance(data, dict):
                if 'records' in data:
                    records = data['records']
                    print(f"Records type: {type(records)}")
                    print(f"Records length: {len(records) if isinstance(records, list) else 'N/A'}")
                    
                    if isinstance(records, list) and len(records) > 0:
                        print(f"First record keys: {list(records[0].keys()) if isinstance(records[0], dict) else type(records[0])}")
                        print(f"First record: {json.dumps(records[0], ensure_ascii=False, indent=2)}")
                else:
                    print("No 'records' key found")
                    print(f"Full response: {json.dumps(data, ensure_ascii=False, indent=2)}")
            else:
                print(f"Response is not dict: {type(data)}")
                print(f"Response content: {str(data)[:500]}...")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_moenv_api()
