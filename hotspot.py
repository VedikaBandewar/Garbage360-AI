import pandas as pd


def build_hotspot_table(reports):
    if not reports:
        return pd.DataFrame(columns=["location", "reports", "highest_severity", "p1_or_p2_count", "hotspot_level"])

    df = pd.DataFrame(reports)
    severity_order = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}
    df["_severity_score"] = df["severity"].map(severity_order).fillna(0).astype(int)

    grouped = (
        df.groupby("location")
        .agg(
            reports=("id", "count"),
            highest_severity=("_severity_score", "max"),
            p1_or_p2_count=("priority", lambda x: sum(v in ["P1", "P2"] for v in x)),
        )
        .reset_index()
    )

    reverse = {v: k for k, v in severity_order.items()}
    grouped["highest_severity"] = grouped["highest_severity"].map(reverse).fillna("Low")
    grouped["hotspot_level"] = grouped.apply(
        lambda r: "Critical" if r["p1_or_p2_count"] >= 2 or r["reports"] >= 5
        else "Watch" if r["reports"] >= 2
        else "Normal",
        axis=1,
    )
    return grouped.sort_values(["reports", "p1_or_p2_count"], ascending=False)

