from datetime import datetime

from loguru import logger

from timegroup.utils.spreadsheet_utils import get_service, replace_data, append_data

class SpreadSheet:
    def __init__(self, gid, reports):
        self._gid = gid
        self._reports = reports
        self._service = get_service()

    def upload(self):
        logger.debug(f"Uploading reports: {self._reports}")
        for report in self._reports:
            sheet_name = report.name
            data = report.data
            logger.debug(f"Report {report.name}")

            if len(data) > 0:
                if report.update_policy == "replace":
                    range_name = f"{sheet_name}!{report.range_name}"
                    logger.debug(f"Sheet name: {sheet_name} range {range_name} rows {len(data)}")
                    result = replace_data(
                        service=self._service,
                        spreadsheet_id=self._gid,
                        range_name=range_name,
                        values=data
                    )
                elif report.update_policy == "append":
                    range_name = f"{sheet_name}!{report.range_name}"
                    logger.debug(f"Sheet name: {sheet_name} range {range_name} rows {len(data)}")

                    result = append_data(
                        service=self._service,
                        spreadsheet_id=self._gid,
                        range_name=range_name,
                        values=data
                    )
                else:
                    raise ValueError()

    def rollback(self):
        pass

class Report:
    def __init__(self, name, range_name="", no_column="", update_policy="replace"):
        self._column_names = []
        self._name = name
        self._data = {}
        self._range_name = range_name
        self._no_column = no_column
        self._udpate_policy = update_policy

    @property
    def data(self):
        return self._data[self._name]

    @property
    def column_names(self):
        return self._column_names

    @property
    def name(self):
        return self._name

    @property
    def range_name(self):
        return self._range_name

    @range_name.setter
    def range_name(self, value):
        self._range_name = value

    @property
    def no_column(self):
        return self._no_column

    @no_column.setter
    def no_column(self, value):
        self._no_column = value

    @property
    def update_policy(self):
        return self._udpate_policy

    @update_policy.setter
    def update_policy(self, value):
        if value != self._udpate_policy:
            self._udpate_policy = value

    @property
    def rows(self):
        return len(self._data[self._name])

    def reorder_columns(self, indices):
        self._column_names = [self._column_names[i] for i in indices]

        data = self._data[self._name]
        for i, row in enumerate(data):
            data[i] = [row[idx] for idx in indices]
        return self._data

    def keep_columns(self, indices):
        self._column_names = [self._column_names[i] for i in indices]

        data = self._data[self._name]
        for i, row in enumerate(data):
            data[i] = [row[idx] for idx in indices]
        return self._data

    def parse(self, raw_data):
        raise NotImplementedError

class POSReport(Report):
    def __init__(self, name="Pos data"):
        super().__init__(name=name)
        self._column_names = ["Ngày tạo đơn", "COD", "Tổng số lượng SP", "Số lượng", "Mã sản phẩm", "Mã Mẫu Mã"]
        self._data = {self._name: []}
        self._udpate_policy = "replace"

    def parse(self, raw_data):
        data = self._data[self._name]

        for order in raw_data:
            items = order.get("items", [])
            for i, item in enumerate(items):
                row = ["" for _ in range(len(self._column_names))]
                if i == 0:
                    # Created date
                    status_history = order.get("status_history", [])
                    created_order_date = None
                    for status_data in status_history:
                        if status_data.get("status") == 1:
                            created_order_date = status_data["updated_at"]

                    if created_order_date is None:
                        continue

                    row[0] = format_isoformat(created_order_date)
                    row[1] = order["cod"]
                    row[2] = order["total_quantity"]

                row[3] = item["quantity"]
                variation_info = item["variation_info"]
                row[4] = variation_info["product_display_id"]
                row[5] = variation_info["display_id"]

                data.append(row)
        return len(data)

class RemainProductReport(Report):
    def __init__(self, name="TỒN KHO"):
        super().__init__(name)
        self._column_names = [
            "MA_SP", "MA_MAU_MA", "TON_KHO", "Danh mục", "Tổng nhập"
        ]
        self._data = {self._name: []}
        self._udpate_policy = "replace"

    def parse(self, raw_data):
        data = self._data[self._name]
        for variation in raw_data:
            row = ["" for _ in range(len(self._column_names))]

            product_info = variation.get("product")
            if product_info:
                # ma_sp
                row[0] = product_info["display_id"]

                # danh_muc
                categories = product_info.get("categories")
                if categories:
                    row[3] = categories[0].get("name", "")

            # ma_mau_ma
            row[1] = variation["display_id"]

            variations_warehouses = variation.get("variations_warehouses", [])
            if variations_warehouses:
                warehouse = variations_warehouses[0]
                row[2] = warehouse["actual_remain_quantity"]
                row[4] = warehouse["total_quantity"]
            else:
                row[2] = 0
                row[4] = 0

            data.append(row)
        return len(data)

class AwaitingOrderReport(Report):
    def __init__(self, name="CHỜ HÀNG"):
        super().__init__(name=name)
        self._column_names = [
            "Ngày tạo đơn", "Mã sản phẩm", "Mã Mẫu mã", "Sản phẩm", "Mã đơn hàng",
            "Tổng số lượng SP", "Số lượng", "Giá", "Giảm giá", "Tình trạng kho", "COD"
        ]
        self._data = {self._name: []}
        self._udpate_policy = "replace"

    def parse(self, raw_data):
        data = self._data[self._name]
        for order in raw_data:
            items = order.get("items", [])
            for i, item in enumerate(items):
                row = ["" for _ in range(len(self._column_names))]
                if i == 0:
                    # Created date
                    status_history = order.get("status_history", [])
                    created_order_date = None
                    for status_data in status_history:
                        if status_data.get("status") == 1:
                            created_order_date = status_data["updated_at"]

                    if created_order_date is None:
                        continue

                    # ngay_tao_don
                    row[0] = format_isoformat(created_order_date)

                    # ma_don_hang
                    row[4] = order["id"]

                    # tong_so_luong
                    row[5] = order["total_quantity"]

                    # cod
                    row[10] = order["cod"]

                variation_info = item["variation_info"]
                # ma_san_pham
                row[1] = variation_info["product_display_id"]

                # ma_mau_ma
                row[2] = variation_info["display_id"]

                # san_pham
                name = variation_info["name"]
                if variation_info["fields"]:
                    row[3] = " / ".join([name] + [field["name"] + ": " + field["value"] for field in variation_info["fields"]])

                # so_luong
                row[6] = item["quantity"]

                # gia
                row[7] = variation_info["retail_price"]

                # giam gia
                row[8] = item["discount_each_product"]

                # tinh trang kho
                row[9] = "Đủ hàng" if item["quantity"] == item["added_to_cart_quantity"] else "Thiếu hàng"
                data.append(row)

        return len(data)

class GHTKOrderReport(Report):
    def __init__(self, name="Đơn hàng ghtk data"):
        super().__init__(name=name)
        self._partner_id = 1
        self._column_names = [
            "MVĐ", "Khách hàng", "SĐT", "Mã sản phẩm", "Mã mẫu mã", "Sản phẩm", "Tổng SL",
            "Số lượng", "COD", "Phí trả cho ĐVVC", "Facebook Page", "PAGE ID",
            "Người xử lý", "NV xác nhận", "Ngày tạo đơn", "Kho hàng", "Ngày gửi"
        ]
        self._data = {self._name: []}
        self._udpate_policy = "append"

    def parse(self, raw_data):
        data = self._data[self._name]
        for order in raw_data:
            partner = order.get("partner")

            # ma van don
            extend_code = partner.get("extend_code")

            # don vi van chuyen
            partner_id = partner.get("partner_id")
            if partner_id != self._partner_id:
                continue

            items = order.get("items", [])
            for i, item in enumerate(items):
                row = ["" for _ in range(len(self._column_names))]
                if i == 0:
                    # Created date
                    status_history = order.get("status_history", [])
                    created_order_date = None
                    for status_data in status_history:
                        if status_data.get("status") == 1:
                            created_order_date = status_data["updated_at"]

                    if created_order_date is None:
                        continue

                    row[0] = extend_code[-10:]

                    # bao gom sp
                    included_products = []
                    for order_item in items:
                        variation_info = order_item["variation_info"]
                        name = variation_info["name"]
                        if variation_info["fields"]:
                            included_products.append(" ".join([name] + [field["name"] + " " + field["value"] for field in variation_info["fields"]]))
                    row[6] = ", ".join(included_products)

                    row[7] = order["total_quantity"]
                    row[9] = order["cod"]
                    row[14] = format_isoformat(created_order_date)

                    # khach hang
                    customer = order["customer"]
                    customer_name = customer["name"]
                    row[1] = customer_name

                    # sdt
                    phone_number = (customer.get("phone_numbers") or [""])[0]
                    row[2] = phone_number

                    # Facebook page and id
                    page = order.get("page", {})
                    facebook_page = page.get("name", "")
                    page_id = page.get("id", "")
                    row[10] = facebook_page
                    row[11] = page_id

                    # nguoi xu ly
                    assigning_seller = order["assigning_seller"]
                    row[12] = assigning_seller["name"]

                    # nguoi xac nhan
                    confirm_staff = ""
                    status_history = order.get("status_history", [])
                    for status_item in status_history:
                        if status_item["status"] in (1, 11):
                            confirm_staff = status_item["name"]
                    row[13] = confirm_staff

                    # kho hang
                    warehouse_info = order["warehouse_info"]
                    row[15] = warehouse_info["name"]

                    # ngay gui
                    time_send_partner = order.get("time_send_partner")
                    if time_send_partner:
                        row[16] = format_isoformat(time_send_partner)

                # ma_san_pham
                variation_info = item["variation_info"]
                row[3] = variation_info["product_display_id"]

                # ma_mau_ma
                row[4] = variation_info["display_id"]

                # san_pham
                name = variation_info["name"]
                if variation_info["fields"]:
                    row[5] = " / ".join([name] + [field["name"] + ": " + field["value"] for field in variation_info["fields"]])

                # so luong
                row[8] = item["quantity"]

                data.append(row)
        return len(data)

class VTPOrderReport(Report):
    def __init__(self, name="Đơn hàng vtp data"):
        super().__init__(name=name)
        self._partner_id = 3
        self._column_names = [
            "MVĐ", "Khách hàng", "SĐT", "Mã sản phẩm", "Mã mẫu mã", "Sản phẩm", "Tổng SL",
            "Số lượng", "COD", "Phí trả cho ĐVVC", "Facebook Page", "PAGE ID",
            "Người xử lý", "NV xác nhận", "Ngày tạo đơn", "Kho hàng", "Ngày gửi"
        ]
        self._data = {self._name: []}
        self._udpate_policy = "append"

    def parse(self, raw_data):
        data = self._data[self._name]
        for order in raw_data:
            partner = order.get("partner")

            # ma van don
            order_number_vtp = partner.get("order_number_vtp")

            # don vi van chuyen
            partner_id = partner.get("partner_id")
            if partner_id != self._partner_id:
                continue

            items = order.get("items", [])
            for i, item in enumerate(items):
                row = ["" for _ in range(len(self._column_names))]
                if i == 0:
                    # Created date
                    status_history = order.get("status_history", [])
                    created_order_date = None
                    for status_data in status_history:
                        if status_data.get("status") == 1:
                            created_order_date = status_data["updated_at"]

                    if created_order_date is None:
                        continue

                    # ma van don
                    row[0] = order_number_vtp

                    # bao gom sp
                    included_products = []
                    for order_item in items:
                        variation_info = order_item["variation_info"]
                        if variation_info["fields"]:
                            name = variation_info["name"]
                            included_products.append(" ".join([name] + [field["name"] + " " + field["value"] for field in variation_info["fields"]]))
                    row[6] = ", ".join(included_products) + f" x {len(items)}"

                    row[7] = order["total_quantity"]
                    row[9] = order["cod"]
                    row[14] = format_isoformat(created_order_date)

                    # khach hang
                    customer = order["customer"]
                    customer_name = customer["name"]
                    row[1] = customer_name

                    # sdt
                    phone_number = (customer.get("phone_numbers") or [""])[0]
                    row[2] = phone_number

                    # Facebook page and id
                    page = order.get("page", {})
                    facebook_page = page.get("name", "")
                    page_id = page.get("id", "")
                    row[10] = facebook_page
                    row[11] = page_id

                    # nguoi xu ly
                    assigning_seller = order["assigning_seller"]
                    row[12] = assigning_seller["name"]

                    # nguoi xac nhan
                    confirm_staff = ""
                    status_history = order.get("status_history", [])
                    for status_item in status_history:
                        if status_item["status"] in (1, 11):
                            confirm_staff = status_item["name"]
                    row[13] = confirm_staff

                    # kho hang
                    warehouse_info = order["warehouse_info"]
                    row[15] = warehouse_info["name"]

                    # ngay gui
                    time_send_partner = order.get("time_send_partner")
                    if time_send_partner:
                        row[16] = format_isoformat(time_send_partner)

                # ma_san_pham
                variation_info = item["variation_info"]
                row[3] = variation_info["product_display_id"]

                # ma_mau_ma
                row[4] = variation_info["display_id"]

                # san_pham
                name = variation_info["name"]
                if variation_info["fields"]:
                    row[5] = " / ".join([name] + [field["name"] + ": " + field["value"] for field in variation_info["fields"]])

                # so luong
                row[8] = item["quantity"]

                data.append(row)
        return len(data)

def format_isoformat(updated_at_str, format="%d/%m/%Y"):
    dt = datetime.fromisoformat(updated_at_str)
    return dt.strftime(format)
