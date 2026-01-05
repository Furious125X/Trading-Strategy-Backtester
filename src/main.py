from loader import load_candles

def main():
    candles = load_candles("data/xrp_15m.csv")
    print(f"Loaded {len(candles)} candles")
    print(candles[0])
    print(candles[-1])

if __name__ == "__main__":
    main()
