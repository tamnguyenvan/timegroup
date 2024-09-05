import csv

from timegroup.utils.datetime_utils import get_timestamps_for_date
from timegroup.utils.pancake_utils import get_shop_orders, parse_order

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
    with open(out_file, "w") as file:
        writer = csv.writer(file, delimiter=",", quotechar="\"")
        column_names = ["MVĐ", "Khách hàng", "SĐT", "Mã sản phẩm", "Mã mẫu mã",
                         "Sản phẩm", "Bao gồm SP", "Tổng SL", "Số lượng", "COD",
                         "Facebook Page", "Page ID", "Người xử lý", "NV xác nhận",
                         "Ngày tạo đơn", "Kho hàng", "Ngày gửi"]
        writer.writerow(column_names)
        for order in orders_data:
            # Build row
            items = order["danh_sach_san_pham"]
            for i, item in enumerate(items):
                row = ["" for _ in range(len(column_names))]
                if i == 0:
                    row[0] = order["mvd"]
                    row[1] = order["khach_hang"]
                    row[2] = order["sdt"]
                    row[6] = ", ".join([item["chi_tiet_san_pham"] for item in items])
                    row[7] = sum(item["so_luong"] for item in items)
                    row[9] = order["cod"]
                    row[10] = order["facebook_page"]
                    row[11] = order["page_id"]
                    row[12] = order["nguoi_xu_ly"]
                    row[13] = order["nguoi_xac_nhan"]
                    row[14] = order["ngay_tao_don"]
                    row[15] = order["kho_hang"]
                    row[16] = order["ngay_gui"]

                row[3] = item["ma_san_pham"]
                row[4] = item["ma_mau_ma"]
                row[5] = item["san_pham"]
                row[8] = item["so_luong"]

                writer.writerow(row)

if __name__ == "__main__":
    shop_id = 20002121
    start_date, end_date = get_timestamps_for_date()

    orders_data = request_orders_data(shop_id, start_date, end_date)

    out_file = "output.csv"
    save_orders_data(out_file, orders_data)
    print("Done!")