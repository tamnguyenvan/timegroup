from openpyxl import Workbook
from datetime import datetime
from timegroup.utils.pancake_utils import get_shop_orders
from loguru import logger

def request_orders_data(credentials, start_date, end_date):
    shop_id = credentials["shop_id"]
    api_key = credentials["api_key"]
    orders_data = []
    logger.debug(f"Processing shop {shop_id}")

    page_number = 1
    total_pages = 1000
    while page_number < total_pages + 1:
        params = {
            "updateStatus": 1,
            "startDateTime": start_date,
            "endDateTime": end_date,
            "page_number": page_number,
            "page_size": 100
        }
        orders, total_pages = get_shop_orders(shop_id, params, api_key=api_key)
        if orders is None:
            break

        logger.debug(f'Shop {shop_id} page: {page_number}/{total_pages}')
        page_number += 1

        orders_data += orders

    return orders_data

def format_updated_at(updated_at_str):
    dt = datetime.fromisoformat(updated_at_str)
    return dt.strftime("%d/%m/%Y %H:%M")

def write_order_report(outfile, orders_data):
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
            row = ["" for _ in range(len(column_names))]
            if i == 0:
                # Fill the first three columns for the first item in the order
                status_history = order.get("status_history", [])
                created_order_date = None
                for status_data in status_history:
                    if status_data.get("status") == 1:
                        created_order_date = status_data["updated_at"]

                if created_order_date is None:
                    continue

                row[0] = format_updated_at(created_order_date)
                row[1] = order["cod"]
                row[2] = order["total_quantity"]

            # Fill the item-specific columns
            row[3] = item["quantity"]
            variation_info = item["variation_info"]
            row[4] = variation_info["product_display_id"]
            name = variation_info["name"]
            if variation_info["fields"]:
                row[5] = " / ".join([name] + [field["name"] + ": " + field["value"] for field in variation_info["fields"]])
            row[6] = variation_info["display_id"]

            # Append the row to the worksheet
            ws.append(row)

    # Save the workbook to the specified file
    wb.save(outfile)
    logger.debug("Total count", count)
    logger.debug("Done!")
