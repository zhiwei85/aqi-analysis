#!/usr/bin/env python3
"""
AQI空氣品質分析系統 - 主程式
遙測與空間資訊之分析與應用 課程作業

功能：
1. 串接環境部AQI API獲取即時空氣品質數據
2. 計算測站到台北車站的距離
3. 生成交互式地圖視覺化
4. 輸出分析結果到CSV檔案

作者：zhiwei85
日期：2026-02-26
"""

import os
import sys
from datetime import datetime

# 設定API金鑰
os.environ['MOENV_API_KEY'] = 'aeeee00c-6e01-4e17-b8dc-7ceee42facce'

# 導入自定義模組
from scripts.moenv_aqi_api import MOENVAQIAPI
from scripts.aqi_map import AQIMapVisualizer
from scripts.distance_analysis import DistanceAnalyzer

def print_banner():
    """顯示程式橫幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                AQI空氣品質分析系統                              ║
    ║            遙測與空間資訊之分析與應用 課程作業                ║
    ║                                                              ║
    ║  功能：                                                        ║
    ║  • 即時AQI數據獲取 (84個測站)                                  ║
    ║  • 空間距離計算 (到台北車站)                                    ║
    ║  • 互動式地圖視覺化                                            ║
    ║  • 分析結果輸出                                                ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_environment():
    """檢查執行環境"""
    print("🔍 檢查執行環境...")
    
    # 檢查必要目錄
    required_dirs = ['data', 'outputs', 'scripts']
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            print(f"❌ 缺少目錄: {dir_name}")
            return False
        else:
            print(f"✅ 目錄存在: {dir_name}")
    
    # 檢查必要檔案
    required_files = ['requirements.txt', 'README.md']
    for file_name in required_files:
        if not os.path.exists(file_name):
            print(f"❌ 缺少檔案: {file_name}")
            return False
        else:
            print(f"✅ 檔案存在: {file_name}")
    
    return True

def run_aqi_analysis():
    """執行AQI分析"""
    print("\n🚀 開始執行AQI分析...")
    
    try:
        # 1. 獲取AQI數據
        print("\n📊 步驟1: 獲取即時AQI數據...")
        api_client = MOENVAQIAPI()
        df = api_client.get_aqi_dataframe()
        
        if df.empty:
            print("❌ 無法獲取AQI數據")
            return False
        
        print(f"✅ 成功獲取 {len(df)} 個測站數據")
        
        # 2. 距離分析
        print("\n📏 步驟2: 計算測站距離...")
        distance_analyzer = DistanceAnalyzer()
        distance_df = distance_analyzer.analyze_distances()
        
        if distance_df.empty:
            print("❌ 距離分析失敗")
            return False
        
        print(f"✅ 完成 {len(distance_df)} 個測站的距離計算")
        
        # 3. 生成地圖
        print("\n🗺️ 步驟3: 生成互動式地圖...")
        map_visualizer = AQIMapVisualizer()
        
        # 生成AQI地圖
        aqi_map = map_visualizer.create_aqi_map()
        map_file = map_visualizer.save_map(aqi_map, "latest_aqi_map.html")
        
        # 生成熱力圖
        heatmap = map_visualizer.create_heatmap()
        heatmap_file = map_visualizer.save_map(heatmap, "latest_aqi_heatmap.html")
        
        print(f"✅ 地圖已生成: {map_file}")
        print(f"✅ 熱力圖已生成: {heatmap_file}")
        
        # 4. 保存距離分析結果
        print("\n💾 步驟4: 保存分析結果...")
        distance_file = distance_analyzer.save_distance_data(distance_df)
        print(f"✅ 距離分析已保存: {distance_file}")
        
        # 5. 顯示統計摘要
        print("\n📈 分析結果摘要:")
        stats = distance_analyzer.get_distance_statistics(distance_df)
        
        print(f"   • 總測站數: {stats.get('total_stations', 0)}")
        print(f"   • 平均距離: {stats.get('mean_distance', 0):.2f} 公里")
        print(f"   • 最近測站: {stats['nearest_station']['name']} ({stats['nearest_station']['distance']:.2f} 公里)")
        print(f"   • 最遠測站: {stats['farthest_station']['name']} ({stats['farthest_station']['distance']:.2f} 公里)")
        
        # 6. AQI統計
        aqi_stats = api_client.get_aqi_statistics()
        print(f"   • 平均AQI: {aqi_stats.get('aqi_mean', 0):.1f}")
        print(f"   • AQI範圍: {aqi_stats.get('aqi_min', 0):.0f} - {aqi_stats.get('aqi_max', 0):.0f}")
        
        return True
        
    except Exception as e:
        print(f"❌ 執行錯誤: {e}")
        return False

def show_output_files():
    """顯示輸出檔案"""
    print("\n📁 輸出檔案:")
    
    output_dir = "outputs"
    if os.path.exists(output_dir):
        for file in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                print(f"   📄 {file} ({size:,} bytes)")
    
    print(f"\n🌐 GitHub倉庫: https://github.com/zhiwei85/aqi-analysis")
    print("📮 請將此連結提交至NTU Cool作業系統")

def main():
    """主函數"""
    print_banner()
    
    # 檢查環境
    if not check_environment():
        print("\n❌ 環境檢查失敗，請確認檔案結構")
        sys.exit(1)
    
    # 執行分析
    if not run_aqi_analysis():
        print("\n❌ 分析執行失敗")
        sys.exit(1)
    
    # 顯示輸出檔案
    show_output_files()
    
    print("\n🎉 AQI空氣品質分析系統執行完成！")
    print("📚 課程: 遙測與空間資訊之分析與應用")
    print("👤 作者: zhiwei85")

if __name__ == "__main__":
    main()
