#!/usr/bin/env python3
import sqlite3
import pandas as pd

def export_to_excel():
    conn = sqlite3.connect('dynamic_pricing.db')
    query = """
    SELECT e.event_id, e.event_date, e.artist, s.sales, ph.predicted_price, ph.applied_at
    FROM events e
    LEFT JOIN sales s ON e.event_id = s.event_id
    LEFT JOIN pricing_history ph ON e.event_id = ph.event_id
    """
    df = pd.read_sql(query, conn)
    conn.close()
    output_file = "pricing_report.xlsx"
    with pd.ExcelWriter(output_file) as writer:
        df.to_excel(writer, index=False, sheet_name="Pricing Report")
    print(f"Report exported to {output_file}")

if __name__ == "__main__":
    export_to_excel()
