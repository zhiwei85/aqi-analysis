#!/usr/bin/env python3
"""
AQI地圖視覺化程式
使用folium在地圖上顯示全台空氣品質監測站數據
"""

import os
import folium
from folium import plugins
import branca.colormap as cm
from moenv_aqi_api import MOENVAQIAPI
from datetime import datetime
import pandas as pd

class AQIMapVisualizer:
    """AQI地圖視覺化器"""
    
    def __init__(self):
        """初始化視覺化器"""
        self.aqi_api = MOENVAQIAPI()
    
    def get_aqi_color(self, aqi_value: float) -> str:
        """
        根據AQI值返回對應顏色 (簡化三色分類)
        
        Args:
            aqi_value: AQI數值
        
        Returns:
            顏色代碼
        """
        if aqi_value is None:
            return '#808080'  # 灰色 - 無數據
        elif aqi_value <= 50:
            return '#00E400'  # 綠色 - 良好 (0-50)
        elif aqi_value <= 100:
            return '#FFFF00'  # 黃色 - 普通 (51-100)
        else:
            return '#FF0000'  # 紅色 - 不健康 (101+)
    
    def get_aqi_level(self, aqi_value: float) -> str:
        """
        根據AQI值返回等級 (簡化三色分類)
        
        Args:
            aqi_value: AQI數值
        
        Returns:
            AQI等級文字
        """
        if aqi_value is None:
            return '無數據'
        elif aqi_value <= 50:
            return '良好'
        elif aqi_value <= 100:
            return '普通'
        else:
            return '不健康'
    
    def create_aqi_map(self, center: list = [23.8, 120.9], zoom: int = 8) -> folium.Map:
        """
        創建AQI地圖
        
        Args:
            center: 地圖中心座標 [緯度, 經度]
            zoom: 縮放級別
            
        Returns:
            Folium地圖物件
        """
        # 獲取AQI數據
        print("正在獲取空氣品質數據...")
        df = self.aqi_api.get_aqi_dataframe()
        
        if df.empty:
            raise ValueError("無法獲取AQI數據")
        
        # 過濾有效座標的測站
        valid_df = df[(df['latitude'].notna()) & 
                     (df['longitude'].notna()) & 
                     (df['latitude'] != 0) & 
                     (df['longitude'] != 0)].copy()
        
        if valid_df.empty:
            raise ValueError("沒有有效的測站座標數據")
        
        print(f"找到 {len(valid_df)} 個有效測站")
        
        # 計算地圖中心（如果沒有指定）
        if center == [23.8, 120.9]:
            center_lat = valid_df['latitude'].mean()
            center_lon = valid_df['longitude'].mean()
            center = [center_lat, center_lon]
        
        # 創建地圖
        m = folium.Map(
            location=center,
            zoom_start=zoom,
            tiles='OpenStreetMap'
        )
        
        # 創建AQI色階圖例 (簡化三色)
        colormap = cm.LinearColormap(
            colors=['#00E400', '#FFFF00', '#FF0000'],
            vmin=0,
            vmax=150,
            caption='空氣品質指數 (AQI) - 綠色:0-50 良好, 黃色:51-100 普通, 紅色:101+ 不健康'
        )
        colormap.add_to(m)
        
        # 添加測站標記
        for idx, row in valid_df.iterrows():
            aqi = row.get('aqi')
            color = self.get_aqi_color(aqi)
            level = self.get_aqi_level(aqi)
            
            # 創建彈出視窗內容 (簡化版)
            aqi_display = f"{aqi:.0f}" if aqi is not None else 'N/A'
            
            popup_content = f"""
            <div style="font-family: Arial, sans-serif; width: 200px; text-align: center;">
                <h4 style="margin: 8px 0; color: {color}; font-size: 16px;">{row.get('site_name', '未知測站')}</h4>
                <p style="margin: 5px 0; font-size: 14px;"><b>所在地:</b> {row.get('county', 'N/A')}</p>
                <p style="margin: 5px 0; font-size: 16px;">
                    <b>即時AQI:</b> 
                    <span style="font-size: 20px; font-weight: bold; color: {color};">{aqi_display}</span>
                </p>
                <p style="margin: 5px 0; font-size: 12px; color: #666;">{level}</p>
            </div>
            """
            
            # 創建圓形標記
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=10 + (aqi / 20) if aqi is not None else 8,  # 根據AQI調整大小
                popup=folium.Popup(popup_content, max_width=300),
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.7,
                weight=2,
                tooltip=f"{row.get('site_name', '未知')}: AQI {aqi_display}" if aqi is not None else f"{row.get('site_name', '未知')}: 無數據"
            ).add_to(m)
            
            # 添加測站名稱標籤
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                icon=folium.DivIcon(
                    html=f'<div style="font-size: 10px; color: black; font-weight: bold; text-shadow: 1px 1px 2px white;">{row.get("site_name", "")}</div>',
                    icon_size=(80, 20),
                    icon_anchor=(40, -10)
                )
            ).add_to(m)
        
        # 添加統計信息面板
        stats_html = self._create_stats_html(valid_df)
        m.get_root().html.add_child(folium.Element(stats_html))
        
        return m
    
    def _create_stats_html(self, df: pd.DataFrame) -> str:
        """創建統計信息HTML"""
        stats = self.aqi_api.get_aqi_statistics(df)
        
        if not stats:
            return ""
        
        html = f"""
        <div style="position: fixed; 
                    top: 10px; right: 10px; 
                    width: 250px; 
                    background: white; 
                    border: 2px solid grey; 
                    padding: 10px; 
                    z-index: 9999; 
                    font-size: 12px;
                    border-radius: 5px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.3);">
            <h4 style="margin: 5px 0; color: #333;">空氣品質統計</h4>
            <p style="margin: 3px 0;"><b>總測站數:</b> {stats.get('total_stations', 0)}</p>
            <p style="margin: 3px 0;"><b>有效數據:</b> {stats.get('stations_with_data', 0)}</p>
            <p style="margin: 3px 0;"><b>平均AQI:</b> {stats.get('aqi_mean', 0):.1f}</p>
            <p style="margin: 3px 0;"><b>AQI範圍:</b> {stats.get('aqi_min', 0):.0f} - {stats.get('aqi_max', 0):.0f}</p>
            
            <h5 style="margin: 8px 0 3px 0; color: #333;">AQI分級分布</h5>
        """
        
        if 'categories' in stats:
            for category, count in stats['categories'].items():
                color = self.get_aqi_color(self._get_category_midpoint(category))
                html += f'<p style="margin: 2px 0;"><span style="color: {color};">●</span> {category}: {count}</p>'
        
        html += """
            <p style="margin: 8px 0 0 0; font-size: 10px; color: #666;">
                更新時間: """ + datetime.now().strftime("%Y-%m-%d %H:%M") + """
            </p>
        </div>
        """
        
        return html
    
    def _get_category_midpoint(self, category: str) -> float:
        """獲取AQI分級的中點值 (簡化三色)"""
        midpoints = {
            '良好': 25,
            '普通': 75,
            '不健康': 125
        }
        return midpoints.get(category, 50)
    
    def create_heatmap(self, center: list = [23.8, 120.9], zoom: int = 8) -> folium.Map:
        """
        創建AQI熱力圖
        
        Args:
            center: 地圖中心座標
            zoom: 縮放級別
            
        Returns:
            Folium地圖物件
        """
        # 獲取AQI數據
        df = self.aqi_api.get_aqi_dataframe()
        
        # 過濾有效數據
        valid_df = df[(df['latitude'].notna()) & 
                     (df['longitude'].notna()) & 
                     (df['aqi'].notna())].copy()
        
        if valid_df.empty:
            raise ValueError("沒有有效的AQI數據")
        
        # 計算地圖中心
        if center == [23.8, 120.9]:
            center_lat = valid_df['latitude'].mean()
            center_lon = valid_df['longitude'].mean()
            center = [center_lat, center_lon]
        
        # 創建地圖
        m = folium.Map(
            location=center,
            zoom_start=zoom,
            tiles='OpenStreetMap'
        )
        
        # 準備熱力圖數據
        heat_data = []
        for idx, row in valid_df.iterrows():
            if row['aqi'] is not None:
                heat_data.append([row['latitude'], row['longitude'], row['aqi']])
        
        # 添加熱力圖 (簡化三色漸層)
        plugins.HeatMap(
            heat_data,
            min_opacity=0.4,
            radius=25,
            blur=15,
            gradient={0.3: '#00E400', 0.6: '#FFFF00', 1.0: '#FF0000'}
        ).add_to(m)
        
        return m
    
    def save_map(self, map_obj: folium.Map, filename: str) -> str:
        """
        保存地圖到HTML檔案
        
        Args:
            map_obj: Folium地圖物件
            filename: 檔案名稱
        
        Returns:
            保存的檔案路徑
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        full_filename = f"{filename}_{timestamp}.html"
        filepath = os.path.join("..", "outputs", full_filename)
        
        # 確保輸出目錄存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 保存地圖
        map_obj.save(filepath)
        print(f"地圖已保存至: {filepath}")
        
        return filepath

def main():
    """主函數"""
    print("=== 環境部空氣品質地圖 ===")
    
    try:
        # 初始化視覺化器
        visualizer = AQIMapVisualizer()
        
        # 1. 創建全台AQI地圖
        print("\n1. 創建全台AQI地圖...")
        taiwan_map = visualizer.create_aqi_map()
        taiwan_file = visualizer.save_map(taiwan_map, "taiwan_aqi_map")
        
        # 2. 創建AQI熱力圖
        print("\n2. 創建AQI熱力圖...")
        heatmap = visualizer.create_heatmap()
        heatmap_file = visualizer.save_map(heatmap, "taiwan_aqi_heatmap")
        
        print(f"\n=== 完成 ===")
        print(f"地圖: {taiwan_file}")
        print(f"熱力圖: {heatmap_file}")
        print(f"請在瀏覽器中開啟HTML檔案查看地圖")
        
    except Exception as e:
        print(f"執行錯誤: {e}")

if __name__ == "__main__":
    main()
