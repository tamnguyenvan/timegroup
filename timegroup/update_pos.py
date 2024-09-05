import csv
from datetime import datetime
import json

from timegroup.utils.datetime_utils import get_timestamps_for_date, isoformat_to_date_string
from timegroup.utils.pancake_utils import get_shop_orders

def request_orders_data(shop_id, start_date, end_date):
    orders_data = []

    page_number = 1
    total_pages = 1000
    while page_number < total_pages + 1:
        params = {
            "updateStatus": 1,
            "startDateTime": start_date,
            "endDateTime": end_date,
            "page_number": page_number
        }
        orders, total_pages = get_shop_orders(shop_id, params)
        print(f'Page: {page_number}/{total_pages}')
        page_number += 1

        if orders is None:
            continue

        orders_data += orders

    return orders_data

def format_updated_at(updated_at_str):
    dt = datetime.fromisoformat(updated_at_str)
    return dt.strftime("%d/%m/%Y %H:%M")

def save_orders_data(out_file, orders_data):
    with open(out_file, "w") as file:
        writer = csv.writer(file, delimiter=",", quotechar="\"")
        column_names = ["Ngày tạo đơn", "COD", "Tổng số lượng SP", "Số lượng", "Mã sản phẩm", "Sản phẩm", "Mã mẫu mã"]

        writer.writerow(column_names)
        count = 0
        for order in orders_data:
            # Build row
            items = order.get("items", [])
            for i, item in enumerate(items):
                count += 1
                print('count', count)
                row = ["" for _ in range(len(column_names))]
                if i == 0:
                    # ngay tao don
                    row[0] = format_updated_at(order["updated_at"])
                    row[1] = order["cod"]
                    row[2] = order["total_quantity"]

                row[3] = item["quantity"]
                variation_info = item["variation_info"]
                row[4] = variation_info["product_display_id"]
                name = variation_info["name"]
                row[5] = " / ".join([name] + [field["name"] + ": " + field["value"] for field in variation_info["fields"]])
                row[6] = variation_info["display_id"]

                writer.writerow(row)

if __name__ == "__main__":
    shop_id = 20002121
    start_date, end_date = get_timestamps_for_date(date="yesterday")

    orders_data = request_orders_data(shop_id, start_date, end_date)
    print(len(orders_data))

    out_file = "output.csv"
    save_orders_data(out_file, orders_data)
    print("Done!")