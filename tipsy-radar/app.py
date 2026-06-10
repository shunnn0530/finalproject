from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import time

app = Flask(__name__)
# 允許所有來源發送請求 (解決 CORS 問題的關鍵)
CORS(app) 

# 建立一個 API 網址：http://127.0.0.1:5000/api/price
@app.route('/api/price', methods=['GET'])
def get_price():
    # 接收前端傳來的材料參數，例如 ?material=titanium
    material = request.args.get('material', 'unknown')

    # 模擬去外部資料庫或真實 API 爬蟲的時間 (停頓 1 秒)
    time.sleep(1)

    # 根據不同材料，後端產生不同的基礎價格區間
    base_prices = {
        'titanium': random.randint(150, 200),     # 鈦合金較貴
        'silicon': random.randint(50, 80),        # 矽晶圓
        'rebar': random.randint(20, 40),          # 鋼筋便宜
        'lithium': random.randint(100, 150),      # 鋰
        'copper': random.randint(80, 120),        # 銅
        'rare_earth': random.randint(300, 500)    # 稀土最貴
    }

    # 取得價格，如果不在清單內則給 100
    price = base_prices.get(material, 100)

    # 將結果打包成 JSON 格式回傳給前端
    return jsonify({
        "status": "success",
        "material_requested": material,
        "base_price": price
    })

if __name__ == '__main__':
    # 啟動伺服器，預設跑在 port 5000
    app.run(debug=True, port=5000)