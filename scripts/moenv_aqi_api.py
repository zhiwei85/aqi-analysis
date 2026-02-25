#!/usr/bin/env python3
"""
環境部空氣品質API客戶端
串接aqx_p_432 API獲取全台即時AQI數據
"""

import os
import requests
import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Optional

# 直接設定API金鑰
os.environ['MOENV_API_KEY'] = 'aeeee00c-6e01-4e17-b8dc-7ceee42facce'

class MOENVAQIAPI:
    """環境部空氣品質API客戶端"""
    
    def __init__(self):
        """初始化API客戶端"""
        self.api_key = self._load_api_key()
        self.base_url = "https://data.moenv.gov.tw/api/v2"
        self.dataset_id = "aqx_p_432"
    
    def _load_api_key(self) -> str:
        """從環境變數讀取MOENV API Key"""
        api_key = os.getenv('MOENV_API_KEY')
        if not api_key:
            raise ValueError("MOENV_API_KEY not found in environment variables")
        return api_key
    
    def fetch_aqi_data(self, limit: Optional[int] = None) -> Dict:
        """
        獲取空氣品質數據
        
        Args:
            limit: 可選的數據筆數限制
        
        Returns:
            API 回應的 JSON 數據
        """
        url = f"{self.base_url}/{self.dataset_id}"
        params = {
            'api_key': self.api_key,
            'format': 'JSON'
        }
        
        if limit:
            params['limit'] = limit
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API 請求失敗: {e}")
    
    def extract_aqi_data(self, aqi_data: Dict) -> List[Dict]:
        """
        從 API 回應中提取AQI數據
        
        Args:
            aqi_data: API 回應的 JSON 數據
        
        Returns:
            包含AQI資訊的字典列表
        """
        aqi_records = []
        
        # MOENV API直接返回列表
        records = aqi_data if isinstance(aqi_data, list) else aqi_data.get('records', [])
        
        for record in records:
            try:
                station_info = {
                    'site_id': record.get('siteid', ''),
                    'site_name': record.get('sitename', ''),
                    'county': record.get('county', ''),
                    'aqi': self._parse_numeric(record.get('aqi')),
                    'pm25': self._parse_numeric(record.get('pm2.5')),
                    'pm10': self._parse_numeric(record.get('pm10')),
                    'o3': self._parse_numeric(record.get('o3')),
                    'co': self._parse_numeric(record.get('co')),
                    'no2': self._parse_numeric(record.get('no2')),
                    'so2': self._parse_numeric(record.get('so2')),
                    'status': record.get('status', ''),
                    'pollutant': record.get('pollutant', ''),
                    'latitude': self._parse_numeric(record.get('latitude')),
                    'longitude': self._parse_numeric(record.get('longitude')),
                    'publish_time': record.get('publishtime', ''),
                    'wind_speed': self._parse_numeric(record.get('wind_speed')),
                    'wind_direction': self._parse_numeric(record.get('wind_direc'))
                }
                
                aqi_records.append(station_info)
                
            except (ValueError, KeyError, TypeError) as e:
                print(f"處理測站數據時發生錯誤: {e}")
                continue
        
        return aqi_records
    
    def _parse_numeric(self, value: str) -> Optional[float]:
        """解析數值"""
        if value is None or value == '' or value == '-':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def get_aqi_dataframe(self, limit: Optional[int] = None) -> pd.DataFrame:
        """
        獲取AQI數據的DataFrame
        
        Args:
            limit: 可選的數據筆數限制
        
        Returns:
            包含AQI數據的DataFrame
        """
        aqi_data = self.fetch_aqi_data(limit)
        aqi_records = self.extract_aqi_data(aqi_data)
        
        df = pd.DataFrame(aqi_records)
        
        if not df.empty:
            # 轉換時間欄位
            if 'publish_time' in df.columns:
                df['publish_time'] = pd.to_datetime(df['publish_time'], errors='coerce')
            
            # 排序
            df = df.sort_values(['county', 'site_name'])
        
        return df
    
    def save_aqi_data(self, limit: Optional[int] = None) -> str:
        """
        保存AQI數據到CSV檔案
        
        Args:
            limit: 可選的數據筆數限制
        
        Returns:
            保存的檔案路徑
        """
        df = self.get_aqi_dataframe(limit)
        
        if df.empty:
            raise ValueError("無法獲取AQI數據")
        
        # 生成檔案名稱
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"aqi_data_{timestamp}.csv"
        filepath = os.path.join("..", "outputs", filename)
        
        # 確保輸出目錄存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 保存檔案
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"AQI數據已保存至: {filepath}")
        
        return filepath
    
    def get_aqi_statistics(self, df: pd.DataFrame) -> Dict:
        """
        獲取AQI統計資訊
        
        Args:
            df: AQI DataFrame
        
        Returns:
            統計資訊字典
        """
        if df.empty or 'aqi' not in df.columns:
            return {}
        
        valid_aqi = df['aqi'].dropna()
        
        if valid_aqi.empty:
            return {}
        
        stats = {
            'total_stations': len(df),
            'stations_with_data': len(valid_aqi),
            'aqi_mean': valid_aqi.mean(),
            'aqi_max': valid_aqi.max(),
            'aqi_min': valid_aqi.min(),
            'aqi_std': valid_aqi.std()
        }
        
        # AQI分級統計
        aqi_categories = {
            '良好': (0, 50),
            '普通': (51, 100),
            '對敏感族群不健康': (101, 150),
            '對所有族群不健康': (151, 200),
            '非常不健康': (201, 300),
            '危險': (301, 500)
        }
        
        category_stats = {}
        for category, (min_val, max_val) in aqi_categories.items():
            count = ((valid_aqi >= min_val) & (valid_aqi <= max_val)).sum()
            category_stats[category] = count
        
        stats['categories'] = category_stats
        
        return stats

def main():
    """主函數 - 示範如何使用MOENV AQI API"""
    try:
        # 初始化API客戶端
        aqi_api = MOENVAQIAPI()
        
        # 獲取全台AQI數據
        print("正在獲取全台空氣品質數據...")
        df = aqi_api.get_aqi_dataframe()
        
        # 顯示基本統計信息
        print(f"\n成功獲取 {len(df)} 個測站數據")
        
        if not df.empty and 'aqi' in df.columns:
            valid_aqi = df['aqi'].dropna()
            if not valid_aqi.empty:
                print(f"AQI範圍: {valid_aqi.min():.1f} ~ {valid_aqi.max():.1f}")
                print(f"平均AQI: {valid_aqi.mean():.1f}")
        
        # 顯示前10個測站的AQI數據
        print("\n前10個測站AQI數據:")
        display_columns = ['site_name', 'county', 'aqi', 'pm25', 'status', 'publish_time']
        available_columns = [col for col in display_columns if col in df.columns]
        print(df[available_columns].head(10).to_string(index=False))
        
        # 保存數據
        output_file = aqi_api.save_aqi_data()
        
        # 獲取統計資訊
        stats = aqi_api.get_aqi_statistics(df)
        if stats:
            print(f"\n=== AQI統計資訊 ===")
            print(f"總測站數: {stats.get('total_stations', 0)}")
            print(f"有效數據測站: {stats.get('stations_with_data', 0)}")
            
            if 'categories' in stats:
                print("\nAQI分級分布:")
                for category, count in stats['categories'].items():
                    print(f"{category}: {count} 個測站")
        
    except Exception as e:
        print(f"執行錯誤: {e}")

if __name__ == "__main__":
    main()
