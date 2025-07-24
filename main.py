from signal_generator import generate_signals, export_signals


def main():
    df = generate_signals()
    if df.empty:
        print("No signals generated. Check data or network access.")
    else:
        print(df)
        export_signals(df)
        print("Signals exported to signals.csv and signals.json")