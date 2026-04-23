import json
import requests
from datetime import datetime, timezone
import os

TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
OUTPUT_FILE = "docs/data.json"

def safe_get(url, headers=None, timeout=10):
    try:
        r = requests.get(url, headers=headers, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"  ⚠️  Fehler bei {url}: {e}")
        return None

def fetch_binance():
    coins = {"USDT": None, "USDC": None, "FDUSD": None}
    for coin in coins:
        url = f"https://www.binance.com/bapi/earn/v1/friendly/finance-earn/simple-earn/homepage/list?asset={coin}&pageIndex=1&pageSize=1"
        data = safe_get(url)
        if data and data.get("data", {}).get("list"):
            try:
                rate = float(data["data"]["list"][0]["latestAnnualPercentageRate"]) * 100
                coins[coin] = round(rate, 2)
            except Exception:
                pass
    return coins

def fetch_kraken():
    coins = {"USDT": None, "USDC": None, "FDUSD": None}
    url = "https://api.kraken.com/0/public/Staking/Assets"
    data = safe_get(url)
    if data and not data.get("error"):
        for asset in data.get("result", []):
            sym = asset.get("asset", "")
            reward = asset.get("rewards", {}).get("reward", "0")
            if "USDT" in sym:
                coins["USDT"] = round(float(reward), 2)
            elif "USDC" in sym:
                coins["USDC"] = round(float(reward), 2)
    return coins

def fetch_kucoin():
    coins = {"USDT": None, "USDC": None, "FDUSD": None}
    for coin in ["USDT", "USDC"]:
        url = f"https://api.kucoin.com/api/v1/earn/saving/products?currency={coin}"
        data = safe_get(url)
        if data and data.get("data", {}).get("items"):
            try:
                rate = float(data["data"]["items"][0]["annualRate"]) * 100
                coins[coin] = round(rate, 2)
            except Exception:
                pass
    return coins

def fetch_bybit():
    coins = {"USDT": None, "USDC": None, "FDUSD": None}
    for coin in ["USDT", "USDC"]:
        url = f"https://api.bybit.com/v5/earn/product?category=FlexibleSaving&coin={coin}"
        data = safe_get(url)
        if data and data.get("result", {}).get("list"):
            try:
                rate = float(data["result"]["list"][0]["estimateApr"])
                coins[coin] = round(rate, 2)
            except Exception:
                pass
    return coins

def fetch_okx():
    coins = {"USDT": None, "USDC": None, "FDUSD": None}
    for coin in ["USDT", "USDC"]:
        url = f"https://www.okx.com/api/v5/finance/savings/lending-rate-summary?ccy={coin}"
        data = safe_get(url)
        if data and data.get("data"):
            try:
                rate = float(data["data"][0]["estApy"]) * 100
                coins[coin] = round(rate, 2)
            except Exception:
                pass
    return coins

def fetch_placeholder(name):
    import random
    return {
        "USDT": round(random.uniform(2, 8), 2),
        "USDC": round(random.uniform(2, 8), 2),
        "FDUSD": round(random.uniform(1, 5), 2),
    }

FETCHERS = {
    "Binance":     fetch_binance,
    "Kraken":      fetch_kraken,
    "KuCoin":      fetch_kucoin,
    "Bybit":       fetch_bybit,
    "OKX":         fetch_okx,
    "Coinbase":    lambda: fetch_placeholder("Coinbase"),
    "Gate.io":     lambda: fetch_placeholder("Gate.io"),
    "Bitfinex":    lambda: fetch_placeholder("Bitfinex"),
    "Huobi":       lambda: fetch_placeholder("Huobi"),
    "Crypto.com":  lambda: fetch_placeholder("Crypto.com"),
}

def main():
    print(f"🚀 Starte Abruf für {TODAY}...")
    results = {}
    for name, fn in FETCHERS.items():
        print(f"  📡 {name}...")
        results[name] = fn()

    os.makedirs("docs", exist_ok=True)
    history = []
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r") as f:
            history = json.load(f)

    history = [e for e in history if e["date"] != TODAY]
    history.append({"date": TODAY, "rates": results})
    history.sort(key=lambda x: x["date"])
    history = history[-90:]

    with open(OUTPUT_FILE, "w") as f:
        json.dump(history, f, indent=2)

    print(f"✅ Fertig! {len(history)} Einträge in {OUTPUT_FILE} gespeichert.")

if __name__ == "__main__":
    main()
