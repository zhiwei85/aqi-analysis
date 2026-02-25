# 環境部空氣品質監測系統

串接環境部AQI API (aqx_p_432) 獲取全台即時空氣品質數據，並使用Folium在地圖上視覺化顯示。

## 🌟 功能特色

- 🔄 **即時數據**: 串接環境部AQI API獲取最新空氣品質數據
- 🗺️ **互動地圖**: 使用Folium創建互動式空氣品質地圖
- 🎨 **顏色分級**: 根據AQI值自動分色顯示(綠→黃→橙→紅→紫→栗)
- 📊 **統計面板**: 顯示AQI統計資訊和分級分布
- 🔥 **熱力圖**: 提供AQI熱力圖視覺化
- 💾 **數據保存**: 自動保存CSV和HTML檔案
- 🔐 **安全設定**: 使用.env檔案管理API金鑰

## 📁 專案結構

```
spatial-analysis/
├── .env                    # 環境變數和API金鑰
├── .gitignore             # Git忽略檔案
├── requirements.txt        # Python套件依賴
├── setup.py               # 自動安裝腳本
├── README.md              # 專案說明
├── data/                  # 資料目錄
├── outputs/               # 輸出結果目錄
└── scripts/               # Python腳本
    ├── moenv_aqi_api.py   # AQI API客戶端
    └── aqi_map.py         # 地圖視覺化
```

## 🚀 快速開始

### 1. 自動安裝環境

```bash
python setup.py
```

這個腳本會自動：
- ✅ 檢查Python版本
- ✅ 安裝所需套件
- ✅ 建立必要目錄
- ✅ 驗證API連線

### 2. 手動安裝 (可選)

如果自動安裝失敗，可以手動執行：

```bash
# 安裝套件
pip install -r requirements.txt

# 設定API金鑰 (編輯.env檔案)
```

### 3. 執行程式

```bash
# 生成AQI地圖
python scripts/aqi_map.py

# 測試API功能
python scripts/moenv_aqi_api.py
```

## 🔧 環境設定

### API金鑰設定

編輯 `.env` 檔案，設定您的環境部API金鑰：

```bash
# API Keys
MOENV_API_KEY=your_moenv_api_key_here
```

**如何獲取API金鑰：**
1. 前往 [環境部開放資料平台](https://data.moenv.gov.tw/)
2. 註冊帳號並申請API金鑰
3. 將金鑰填入 `.env` 檔案

## 📊 AQI顏色對應

| AQI範圍 | 等級 | 顏色 | 說明 |
|---------|------|------|------|
| 0-50 | 良好 | 🟢 綠色 | 空氣品質令人滿意 |
| 51-100 | 普通 | 🟡 黃色 | 空氣品質可接受 |
| 101-150 | 對敏感族群不健康 | 🟠 橙色 | 敏感族群可能有輕微影響 |
| 151-200 | 對所有族群不健康 | 🔴 紅色 | 所有族群可能開始有影響 |
| 201-300 | 非常不健康 | 🟣 紫色 | 對健康有明顯影響 |
| 301+ | 危險 | 🟤 栗色 | 對健康有嚴重影響 |

## 🗺️ 地圖功能

### AQI監測站地圖
- 📍 **測站位置**: 顯示全台所有空氣品質監測站
- 🎯 **圓形標記**: 大小根據AQI值調整
- 📱 **彈出視窗**: 點擊查看詳細資訊
- 🏷️ **測站名稱**: 直接顯示在地圖上
- 📊 **統計面板**: 右上角顯示統計資訊

### AQI熱力圖
- 🔥 **熱力分佈**: 顯示空氣品質空間分佈
- 🌈 **漸層色彩**: 根據AQI值顯示熱力強度
- 🎨 **自訂配色**: 符合環署標準色彩

## 📋 輸出檔案

程式執行後會在 `outputs/` 目錄生成：

### 地圖檔案
- `taiwan_aqi_map_YYYYMMDD_HHMMSS.html` - 互動式AQI地圖
- `taiwan_aqi_heatmap_YYYYMMDD_HHMMSS.html` - AQI熱力圖

### 數據檔案
- `aqi_data_YYYYMMDD_HHMMSS.csv` - 完整AQI數據

## 🔍 API數據欄位

| 欄位名稱 | 說明 | 範例 |
|---------|------|------|
| SiteId | 測站ID | 14 |
| SiteName | 測站名稱 | 基隆 |
| County | 縣市 | 基隆市 |
| AQI | 空氣品質指數 | 45 |
| PM25 | PM2.5濃度 | 12 |
| PM10 | PM10濃度 | 18 |
| O3 | 臭氧濃度 | 45 |
| CO | 一氧化碳濃度 | 0.3 |
| NO2 | 二氧化氮濃度 | 8 |
| SO2 | 二氧化硫濃度 | 2 |
| Status | 空氣品質狀態 | 良好 |
| Pollutant | 主要污染物 | - |
| Latitude | 緯度 | 25.128 |
| Longitude | 經度 | 121.739 |
| PublishTime | 發布時間 | 2024-02-25 15:00 |

## 🛠️ 開發說明

### 主要類別

#### `MOENVAQIAPI`
- 環境部AQI API客戶端
- 處理API請求和數據解析
- 提供DataFrame格式數據

#### `AQIMapVisualizer`
- Folium地圖視覺化器
- AQI顏色分級和標記
- 統計面板和熱力圖

### 自訂功能

您可以修改以下參數：

```python
# 地圖中心座標
center = [23.8, 120.9]  # [緯度, 經度]

# 縮放級別
zoom = 8

# AQI顏色自訂
def get_aqi_color(self, aqi_value):
    # 自訂顏色邏輯
    pass
```

## 🐛 故障排除

### 常見問題

1. **API金鑰錯誤**
   ```
   錯誤: MOENV_API_KEY not found in environment variables
   ```
   **解決**: 檢查 `.env` 檔案是否正確設定

2. **網路連線問題**
   ```
   錯誤: API 請求失敗
   ```
   **解決**: 檢查網路連線和防火牆設定

3. **套件安裝失敗**
   ```
   錯誤: pip install failed
   ```
   **解決**: 升級pip `python -m pip install --upgrade pip`

4. **地圖無法顯示**
   ```
   錯誤: 沒有有效的測站座標數據
   ```
   **解決**: 檢查API是否返回有效數據

## 📝 更新日誌

### v1.0.0 (2024-02-25)
- ✨ 初始版本發布
- 🔄 串接環境部AQI API
- 🗺️ Folium地圖視覺化
- 📊 AQI統計功能
- 🔥 熱力圖功能
- 🔐 環境變數管理

## 📄 授權

MIT License

## 🤝 貢獻

歡迎提交Issue和Pull Request！

## 📞 聯絡方式

如有問題請透過GitHub Issues聯繫。

---

**注意**: 本專案僅供學習和研究使用，請遵守環境部API使用規範。
