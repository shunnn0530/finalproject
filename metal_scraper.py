import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime

# 1. 目標網址與偽裝成瀏覽器的 Headers
url = 'https://www.cnyes.com/futures/basicmetal.aspx'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

# 2. 定義你要追蹤的戰略原物料 (必須對應網頁上的確切名稱)
targets = [
    '鈦海綿(Titanium Spon)',         # 航太鈦合金
    '金屬矽塊(Silicon Lumps)',       # 半導體矽原料
    '主力月上海螺紋鋼',              # 建築鋼筋 (根據你的HTML，全名為此)
    '碳酸鋰(=99.2%出廠價中國)',      # 電池級碳酸鋰
    '銅(現貨)',                      # 工業精煉銅
    '鎵錠(Gallium ingot)'            # 高科技鎵
]

print("🔍 開始抓取鉅亨網報價資料...\n")

try:
    # 發送請求
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8' # 確保中文不亂碼
    soup = BeautifulSoup(response.text, 'html.parser')

    scraped_data = []

    # 3. 解析資料
    for target in targets:
        # 尋找包含目標字串的 <a> 標籤
        # 使用 lambda 函數進行部分比對，避免網頁字串有些微空白差異
        a_tag = soup.find('a', string=lambda text: text and target in text)
        
        if a_tag:
            tr_tag = a_tag.find_parent('tr')
            tds = tr_tag.find_all('td')
            
            try:
                # 取得資料並清除千分位逗號與多餘空白
                date_str = tds[0].text.strip()
                name = tds[1].text.strip()
                # 鉅亨網格式: tds[4] 是收盤價，tds[7] 是開盤價
                close_price = tds[4].text.strip().replace(',', '')
                open_price = tds[7].text.strip().replace(',', '')
                
                scraped_data.append([date_str, name, open_price, close_price])
                print(f"✅ 成功抓取: {name} | 開盤: {open_price} | 收盤: {close_price}")
            
            except Exception as e:
                print(f"❌ 解析 {target} 時發生錯誤: {e}")
        else:
            print(f"⚠️ 找不到目標: {target} (可能網頁已下架或更名)")

    # 4. 將資料寫入 CSV 檔案
    if scraped_data:
        # 取得今天日期作為檔名的一部分
        today_str = datetime.now().strftime("%Y%m%d")
        filename = f"strategic_metals_{today_str}.csv"
        
        # 寫入 CSV (使用 utf-8-sig 讓 Windows Excel 打開不會亂碼)
        with open(filename, mode='w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['報價日期', '原物料名稱', '開盤價', '收盤價']) # 寫入標題列
            writer.writerows(scraped_data)                     # 寫入資料列
            
        print(f"\n📁 抓取完畢！資料已成功存檔至當前目錄: {filename}")
    else:
        print("\n⚠️ 未抓取到任何資料，無法存檔。")

except Exception as e:
    print(f"❌ 網路請求失敗，請檢查網路連線或網址狀態。錯誤訊息: {e}")