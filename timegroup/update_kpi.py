import csv

from timegroup.utils.datetime_utils import get_timestamps_for_date
from timegroup.utils.pancake_utils import get_shop_orders, parse_order

pancake_status_to_timegroup_status_map = {

}

def request_orders_data(shop_id, start_date, end_date):
    orders_data = []

    page_number = 1
    total_pages = 1000
    while page_number < total_pages + 1:
        orders, total_pages = get_shop_orders(shop_id, start_date, end_date, page_number)

        if orders is None:
            return orders_data

        for order in orders:
            parsed_order = parse_order(order)
            if parsed_order:
                orders_data.append(parsed_order)

        print(f'Page: {page_number}/{total_pages}')
        page_number += 1

    return orders_data

def save_orders_data(out_file, orders_data):
    pass

if __name__ == "__main__":
    shop_id = 20002121
    start_date, end_date = get_timestamps_for_date()

    orders_data = request_orders_data(shop_id, start_date, end_date)

    out_file = "output.csv"
    save_orders_data(out_file, orders_data)
    print("Done!")