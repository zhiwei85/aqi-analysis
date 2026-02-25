#!/usr/bin/env python3
"""
空間距離分析程式
計算每個測站到台北車站的距離
"""

import os
import math
import pandas as pd
from datetime import datetime
from moenv_aqi_api import MOENVAQIAPI

# 設定API金鑰
os.environ['MOENV_API_KEY'] = 'aeeee00c-6e01-4e17-b8dc-7ceee42facce'

class DistanceAnalyzer:
    """距離分析器"""
    
    def __init__(self):
        """初始化分析器"""
        self.aqi_api = MOENVAQIAPI()
        self.taipei_station = {
            'name': '台北車站',
            'latitude': 25.0478,
            'longitude': 121.5170
        }
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        使用Haversine公式計算兩點間的距離
        
        Args:
            lat1, lon1: 第一點的緯度、經度
            lat2, lon2: 第二點的緯度、經度
        
        Returns:
            距離（公里）
        """
        # 地球半徑（公里）
        R = 6371.0
        
        # 將角度轉為弧度
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine公式
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = (math.sin(dlat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(dlon/2)**2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        distance = R * c
        
        return distance
    
    def analyze_distances(self) -> pd.DataFrame:
        """
        分析所有測站到台北車站的距離
        
        Returns:
            包含距離資訊的DataFrame
        """
        print("正在獲取AQI數據...")
        df = self.aqi_api.get_aqi_dataframe()
        
        if df.empty:
            raise ValueError("無法獲取AQI數據")
        
        print(f"獲取到 {len(df)} 個測站數據")
        
        # 過濾有效座標的測站
        valid_df = df[(df['latitude'].notna()) & 
                     (df['longitude'].notna()) & 
                     (df['latitude'] != 0) & 
                     (df['longitude'] != 0)].copy()
        
        print(f"有效座標測站: {len(valid_df)} 個")
        
        # 計算距離
        print("計算到台北車站的距離...")
        
        distances = []
        for idx, row in valid_df.iterrows():
            try:
                distance = self.calculate_distance(
                    row['latitude'], row['longitude'],
                    self.taipei_station['latitude'], self.taipei_station['longitude']
                )
                
                distance_info = {
                    'site_id': row.get('site_id', ''),
                    'site_name': row.get('site_name', ''),
                    'county': row.get('county', ''),
                    'latitude': row['latitude'],
                    'longitude': row['longitude'],
                    'aqi': row.get('aqi', None),
                    'pm25': row.get('pm25', None),
                    'status': row.get('status', ''),
                    'distance_to_taipei': distance,
                    'distance_category': self._get_distance_category(distance)
                }
                
                distances.append(distance_info)
                
            except Exception as e:
                print(f"計算距離時發生錯誤: {e}")
                continue
        
        result_df = pd.DataFrame(distances)
        
        # 按距離排序
        result_df = result_df.sort_values('distance_to_taipei')
        
        return result_df
    
    def _get_distance_category(self, distance: float) -> str:
        """
        根據距離分類
        
        Args:
            distance: 距離（公里）
        
        Returns:
            距離分類
        """
        if distance <= 10:
            return '台北市區'
        elif distance <= 30:
            return '北北基桃'
        elif distance <= 100:
            return '北部地區'
        elif distance <= 200:
            return '中部地區'
        else:
            return '南部地區'
    
    def get_distance_statistics(self, df: pd.DataFrame) -> dict:
        """
        獲取距離統計資訊
        
        Args:
            df: 距離DataFrame
        
        Returns:
            統計資訊字典
        """
        if df.empty:
            return {}
        
        stats = {
            'total_stations': len(df),
            'min_distance': df['distance_to_taipei'].min(),
            'max_distance': df['distance_to_taipei'].max(),
            'mean_distance': df['distance_to_taipei'].mean(),
            'median_distance': df['distance_to_taipei'].median()
        }
        
        # 距離分類統計
        category_stats = df['distance_category'].value_counts().to_dict()
        stats['categories'] = category_stats
        
        # 最近和最遠的測站
        nearest = df.iloc[0]
        farthest = df.iloc[-1]
        
        stats['nearest_station'] = {
            'name': nearest['site_name'],
            'county': nearest['county'],
            'distance': nearest['distance_to_taipei']
        }
        
        stats['farthest_station'] = {
            'name': farthest['site_name'],
            'county': farthest['county'],
            'distance': farthest['distance_to_taipei']
        }
        
        return stats
    
    def save_distance_data(self, df: pd.DataFrame) -> str:
        """
        保存距離數據到CSV檔案
        
        Args:
            df: 距離DataFrame
        
        Returns:
            保存的檔案路徑
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"aqi_distance_analysis_{timestamp}.csv"
        filepath = os.path.join("..", "outputs", filename)
        
        # 確保輸出目錄存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 保存檔案
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"距離分析數據已保存至: {filepath}")
        
        return filepath

def main():
    """主函數"""
    print("=== AQI測站距離分析 ===")
    
    try:
        # 初始化分析器
        analyzer = DistanceAnalyzer()
        
        # 分析距離
        print("\n開始距離分析...")
        df = analyzer.analyze_distances()
        
        if df.empty:
            print("沒有有效數據")
            return
        
        # 獲取統計資訊
        stats = analyzer.get_distance_statistics(df)
        
        # 顯示結果
        print(f"\n=== 距離分析結果 ===")
        print(f"總測站數: {stats.get('total_stations', 0)}")
        print(f"最近距離: {stats.get('min_distance', 0):.2f} 公里")
        print(f"最遠距離: {stats.get('max_distance', 0):.2f} 公里")
        print(f"平均距離: {stats.get('mean_distance', 0):.2f} 公里")
        print(f"中位數距離: {stats.get('median_distance', 0):.2f} 公里")
        
        print(f"\n最近測站: {stats['nearest_station']['name']} "
              f"({stats['nearest_station']['county']}) - "
              f"{stats['nearest_station']['distance']:.2f} 公里")
        
        print(f"最遠測站: {stats['farthest_station']['name']} "
              f"({stats['farthest_station']['county']}) - "
              f"{stats['farthest_station']['distance']:.2f} 公里")
        
        print(f"\n=== 距離分類分布 ===")
        if 'categories' in stats:
            for category, count in stats['categories'].items():
                print(f"{category}: {count} 個測站")
        
        # 顯示前10個最近的測站
        print(f"\n=== 距離台北車站最近的10個測站 ===")
        display_columns = ['site_name', 'county', 'aqi', 'distance_to_taipei', 'distance_category']
        available_columns = [col for col in display_columns if col in df.columns]
        
        top_10 = df.head(10)[available_columns]
        print(top_10.to_string(index=False))
        
        # 保存數據
        output_file = analyzer.save_distance_data(df)
        
        print(f"\n=== 完成 ===")
        print(f"分析結果已保存至: {output_file}")
        
    except Exception as e:
        print(f"執行錯誤: {e}")

if __name__ == "__main__":
    main()
