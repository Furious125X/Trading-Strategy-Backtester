import json
import csv
import os


def export_summary(summary, filename="outputs/performance_summary.json"):

    os.makedirs("outputs", exist_ok=True)

    with open(filename, "w") as f:
        json.dump(summary, f, indent=4)


def export_optimizer_results(results, filename="outputs/optimizer_results.csv"):

    os.makedirs("outputs", exist_ok=True)

    with open(filename, "w", newline="") as f:

        writer = csv.writer(f)

        writer.writerow(["risk_reward", "rsi_threshold", "trades", "total_r"])

        for r in results:

            params = r["params"]

            writer.writerow([
                params.get("risk_reward"),
                params.get("rsi_threshold"),
                r["trades"],
                r["total_r"]
            ])

def export_walkforward(results, filename="outputs/walkforward_results.json"):

    os.makedirs("outputs", exist_ok=True)

    with open(filename, "w") as f:
        json.dump(results, f, indent=4)