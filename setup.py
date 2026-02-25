#!/usr/bin/env python3
"""
自動環境安裝腳本
自動安裝Python套件並驗證環境設定
"""

import subprocess
import sys
import os
from pathlib import Path

def check_python_version():
    """檢查Python版本"""
    print("檢查Python版本...")
    version = sys.version_info
    print(f"目前Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("錯誤: 需要Python 3.8或更高版本")
        return False
    
    print("OK Python版本符合要求")
    return True

def check_virtual_env():
    """檢查虛擬環境"""
    print("\n檢查虛擬環境...")
    
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("OK 已在虛擬環境中")
        return True
    else:
        print("注意: 建議使用虛擬環境")
        print("建立虛擬環境命令:")
        print("python -m venv .venv")
        print("啟動虛擬環境命令:")
        print(".venv\\Scripts\\activate  # Windows")
        return False

def install_requirements():
    """安裝requirements.txt中的套件"""
    print("\n安裝Python套件...")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("錯誤: requirements.txt檔案不存在")
        return False
    
    try:
        # 升級pip
        print("升級pip...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        
        # 安裝套件
        print("安裝requirements.txt中的套件...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        
        print("OK 套件安裝完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print("錯誤: 套件安裝失敗:")
        return False

def check_env_file():
    """檢查.env檔案"""
    print("\n檢查環境變數檔案...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("錯誤: .env檔案不存在")
        print("請建立.env檔案並設定API金鑰")
        return False
    
    # 檢查API金鑰
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        moenv_key = os.getenv('MOENV_API_KEY')
        if not moenv_key:
            print("錯誤: MOENV_API_KEY未設定")
            return False
        
        print("OK MOENV_API_KEY已設定")
        return True
        
    except ImportError:
        print("錯誤: python-dotenv未安裝")
        return False

def create_directories():
    """建立必要的目錄"""
    print("\n建立必要的目錄...")
    
    directories = ["data", "outputs", "scripts"]
    
    for directory in directories:
        dir_path = Path(directory)
        dir_path.mkdir(exist_ok=True)
        print(f"OK {directory}/ 目錄已準備")
    
    return True

def test_api_connection():
    """測試API連線"""
    print("\n測試API連線...")
    
    try:
        from scripts.moenv_aqi_api import MOENVAQIAPI
        
        aqi_api = MOENVAQIAPI()
        df = aqi_api.get_aqi_dataframe(limit=5)  # 只獲取5筆資料測試
        
        if not df.empty:
            print(f"OK API連線成功，獲取到 {len(df)} 筆測試資料")
            return True
        else:
            print("錯誤: API回應空資料")
            return False
            
    except Exception as e:
        print(f"錯誤: API連線失敗: {e}")
        return False

def main():
    """主函數"""
    print("=== 環境部空氣品質系統自動安裝 ===")
    print("=" * 50)
    
    # 檢查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 檢查虛擬環境
    check_virtual_env()
    
    # 建立目錄
    if not create_directories():
        sys.exit(1)
    
    # 安裝套件
    if not install_requirements():
        sys.exit(1)
    
    # 檢查環境變數
    if not check_env_file():
        print("\n請編輯.env檔案，設定正確的MOENV_API_KEY")
        sys.exit(1)
    
    # 測試API連線
    if not test_api_connection():
        print("\n請檢查API金鑰是否正確")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("OK 安裝完成！")
    print("\n接下來可以執行:")
    print("python scripts/aqi_map.py  # 生成AQI地圖")
    print("python scripts/moenv_aqi_api.py  # 測試API")

if __name__ == "__main__":
    main()
