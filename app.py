from flask import Flask, jsonify, request, redirect, send_from_directory
from flask_cors import CORS

import requests
from bs4 import BeautifulSoup

app = Flask(__name__, static_folder="public", static_url_path="")
CORS(app)




app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return redirect("/index.html", code=307)


app = Flask(__name__)
CORS(app)

# =====================================
# 爬蟲函式
# =====================================

def scrape_material_prices():

    url = "https://www.cnyes.com/futures/basicmetal.aspx"

    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    targets = {
        "titanium": "鈦海綿(Titanium Spon)",
        "silicon": "金屬矽塊(Silicon Lumps)",
        "rebar": "主力月上海螺紋鋼",
        "lithium": "碳酸鋰(=99.2%出廠價中國)",
        "copper": "銅(現貨)",
        "gallium": "鎵錠(Gallium ingot)",
    }

    results = {}

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        response.encoding = "utf-8"

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        for material_key, target_name in targets.items():

            a_tag = soup.find(
                "a",
                string=lambda text:
                text and target_name in text
            )

            if not a_tag:
                print(f"找不到 {target_name}")
                continue

            tr_tag = a_tag.find_parent("tr")

            if not tr_tag:
                continue

            tds = tr_tag.find_all("td")

            try:

                date_str = tds[0].text.strip()

                close_price = float(
                    tds[4].text.strip().replace(",", "")
                )

                open_price = float(
                    tds[7].text.strip().replace(",", "")
                )

                results[material_key] = {
                    "name": target_name,
                    "date": date_str,
                    "open": open_price,
                    "close": close_price
                }

                print(
                    f"成功抓取 {target_name}"
                    f" 開盤:{open_price}"
                    f" 收盤:{close_price}"
                )

            except Exception as e:
                print(f"{target_name}解析失敗: {e}")

        return results

    except Exception as e:

        print("爬蟲失敗:", e)

        return {}


# =====================================
# 儲存 CSV
# =====================================



# =====================================
# 啟動時先抓一次
# =====================================

cached_prices = scrape_material_prices()

@app.route("/")
def home():
    return send_from_directory("public", "index.html")


# =====================================
# API
# =====================================

@app.route("/api/price", methods=["GET"])
def get_price():

    material = request.args.get(
        "material",
        "titanium"
    )

    material_data = cached_prices.get(material)

    if not material_data:

        return jsonify({
            "status": "error",
            "message": "查無資料"
        }), 404

    return jsonify({

        "status": "success",

        "material_requested": material,

        "base_price":
        material_data["close"],

        "open":
        material_data["open"],

        "close":
        material_data["close"],

        "date":
        material_data["date"]

    })


# =====================================
# 查看全部資料
# =====================================

@app.route("/api/all_prices")
def all_prices():

    return jsonify(cached_prices)


# =====================================
# 手動重新爬取
# =====================================

@app.route("/api/refresh")
def refresh():

    global cached_prices

    cached_prices = scrape_material_prices()

    return jsonify({
        "status": "success",
        "message": "資料已更新"
    })


# =====================================
# Flask 啟動
# =====================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )