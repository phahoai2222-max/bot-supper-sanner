import requests
import time

BASE = "https://fapi.binance.com"

volume_memory = {}
oi_memory = {}

def get_symbols():

    url = BASE + "/fapi/v1/exchangeInfo"
    data = requests.get(url).json()

    symbols = []

    for s in data["symbols"]:
        if s["quoteAsset"] == "USDT" and s["status"] == "TRADING":
            symbols.append(s["symbol"])

    return symbols


def get_volume(symbol):

    url = BASE + "/fapi/v1/ticker/24hr?symbol=" + symbol
    data = requests.get(url).json()

    return float(data["volume"])


def get_funding(symbol):

    url = BASE + "/fapi/v1/fundingRate?symbol=" + symbol + "&limit=1"
    data = requests.get(url).json()

    return float(data[0]["fundingRate"])


def get_open_interest(symbol):

    url = BASE + "/fapi/v1/openInterest?symbol=" + symbol
    data = requests.get(url).json()

    return float(data["openInterest"])


def get_orderbook(symbol):

    url = BASE + "/fapi/v1/depth?symbol=" + symbol + "&limit=50"
    data = requests.get(url).json()

    bids = sum(float(b[1]) for b in data["bids"])
    asks = sum(float(a[1]) for a in data["asks"])

    return bids, asks


def analyze(symbol):

    score = 0
    signals = []

    volume = get_volume(symbol)
    funding = get_funding(symbol)
    oi = get_open_interest(symbol)
    bids, asks = get_orderbook(symbol)

    # volume spike
    if symbol in volume_memory:

        old_volume = volume_memory[symbol]

        if volume > old_volume * 3:

            score += 3
            signals.append("Volume spike")

    volume_memory[symbol] = volume

    # funding
    if funding < -0.01:

        score += 2
        signals.append("Short squeeze setup")

    # open interest spike
    if symbol in oi_memory:

        old_oi = oi_memory[symbol]

        if oi > old_oi * 1.2:

            score += 2
            signals.append("OI rising")

    oi_memory[symbol] = oi

    # orderbook
    if bids > asks * 1.5:

        score += 2
        signals.append("Whale buy wall")

    return {
        "symbol": symbol,
        "score": score,
        "signals": signals
    }


def scan():

    symbols = get_symbols()

    results = []

    print("Scanning market...")

    for s in symbols:

        try:

            r = analyze(s)

            if r["score"] >= 4:

                results.append(r)

        except:
            pass

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    print("\n🔥 TOP PUMP SETUPS\n")

    for r in results[:10]:

        print("================================")

        print("Coin:", r["symbol"])

        print("Score:", r["score"])

        print("Signals:")

        for s in r["signals"]:
            print("-", s)

        if r["score"] >= 7:
            print("🚀 HIGH PUMP PROBABILITY (20-100%)")

        elif r["score"] >= 5:
            print("⚡ MEDIUM PUMP PROBABILITY")

        print("================================")


while True:

    scan()

    print("\nNext scan in 60 seconds...\n")

    time.sleep(60)
