# 專案目錄結構

```
spatial-analysis/
├── .env                    # 環境變數和API金鑰 (敏感資訊)
├── .gitignore             # Git忽略檔案設定
├── requirements.txt        # Python套件依賴
├── README.md              # 專案說明文件
├── PROJECT_STRUCTURE.md   # 專案結構說明 (本檔案)
├── data/                  # 原始資料目錄
│   ├── raw/              # 原始資料
│   ├── processed/        # 處理後資料
│   └── external/         # 外部資料
├── outputs/               # 輸出結果目錄
│   ├── maps/             # 地圖檔案
│   ├── reports/          # 報告檔案
│   └── figures/          # 圖表檔案
├── scripts/               # Python腳本
│   ├── data_processing.py
│   ├── analysis.py
│   └── visualization.py
├── notebooks/             # Jupyter Notebook
│   └── exploratory_analysis.ipynb
└── tests/                 # 測試檔案
    └── test_analysis.py
```

## 目錄說明

### `/data`
存放原始和處理後的資料檔案
- `raw/`: 原始資料檔案
- `processed/`: 清理和處理後的資料
- `external/`: 外部資料來源

### `/outputs`
存放分析結果和輸出檔案
- `maps/`: 地圖視覺化檔案
- `reports/`: 分析報告
- `figures/`: 圖表和視覺化

### `.env`
存放敏感資訊，包含：
- API金鑰 (CWA_API_KEY)
- 資料庫連線資訊
- 其他設定參數

**注意：** .env檔案已加入.gitignore，不會被提交到版本控制

### `.gitignore`
排除以下檔案：
- 環境變數檔案 (.env)
- Python快取 (__pycache__)
- 虛擬環境 (venv/, env/)
- IDE設定檔
- 作業系統檔案
- 大型資料檔案 (可選)

## 使用方式

1. **複製專案**
2. **安裝依賴**: `pip install -r requirements.txt`
3. **設定環境變數**: 編輯 `.env` 檔案
4. **執行分析**: `python scripts/analysis.py`
