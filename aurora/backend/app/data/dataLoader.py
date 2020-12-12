import pandas as pd
import json
import pyarrow as pa
import pyarrow.parquet as pq


def load_historical_index(fund_codes, start_date, end_date):
    response_columns = fund_codes
    response_columns = ["date"] + fund_codes
    all_historical_prices = pq.read_table(
        "app/data/dailyPrice.parquet", columns=response_columns
    ).to_pandas()
    subset_data = all_historical_prices[all_historical_prices["date"] >= start_date][
        all_historical_prices["date"] <= end_date
    ]
    subset_data = subset_data.sort_values("date").reset_index(drop=True)

    idx = pd.date_range(start_date, end_date)

    subset_data = subset_data.set_index("date")
    subset_data.index.name = None
    subset_data.index = pd.DatetimeIndex(subset_data.index)
    subset_data = subset_data.reindex(idx, fill_value=None)
    subset_data = subset_data.interpolate(method="index", axis=0)
    subset_data = subset_data.reset_index(drop = False)
    subset_data.columns = response_columns
    subset_data['date'] = subset_data['date'].dt.strftime('%Y-%m-%d')

    for i in fund_codes:
        subset_data[f"{i}index"] = subset_data[i] / subset_data[i][0]

    subset_data = subset_data.fillna(0)
    subset_data = subset_data.drop(fund_codes, axis=1)
    subset_data.columns = response_columns

    return json.loads(subset_data.to_json(orient="records"))


def load_available_funds():
    all_funds = (
        pq.read_table("app/data/fundCodes.parquet")
        .to_pandas()
        .reset_index()
        .to_json(orient="records")
    )

    return json.loads(all_funds)