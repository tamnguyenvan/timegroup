from openpyxl import Workbook
from datetime import datetime
from timegroup.utils.datetime_utils import get_timestamps_for_date
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

def save_orders_data(outfile, orders_data):
    # Create a workbook and select the active worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Orders Report"

    # Define column headers
    column_names = ["Ngày tạo đơn", "COD", "Tổng số lượng SP", "Số lượng", "Mã sản phẩm", "Sản phẩm", "Mã mẫu mã"]
    ws.append(column_names)

    count = 0
    for order in orders_data:
        items = order.get("items", [])
        for i, item in enumerate(items):
            count += 1
            print('count', count)
            row = ["" for _ in range(len(column_names))]
            if i == 0:
                # Fill the first three columns for the first item in the order
                row[0] = format_updated_at(order["updated_at"])
                row[1] = order["cod"]
                row[2] = order["total_quantity"]

            # Fill the item-specific columns
            row[3] = item["quantity"]
            variation_info = item["variation_info"]
            row[4] = variation_info["product_display_id"]
            name = variation_info["name"]
            row[5] = " / ".join([name] + [field["name"] + ": " + field["value"] for field in variation_info["fields"]])
            row[6] = variation_info["display_id"]

            # Append the row to the worksheet
            ws.append(row)

    # Save the workbook to the specified file
    wb.save(outfile)


def create_report(shop_id, time_period, outfile):
    start_date, end_date = time_period
    start_date, end_date = get_timestamps_for_date(date="yesterday")

    orders_data = request_orders_data(shop_id, start_date, end_date)
    print(len(orders_data))

    save_orders_data(outfile, orders_data)
    return outfile