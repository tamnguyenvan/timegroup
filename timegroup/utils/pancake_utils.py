import os
from datetime import datetime
from typing import Optional, Dict, Tuple

import requests
from dotenv import load_dotenv

load_dotenv()

def request_pancake(path: str = None,
                    params: Optional[Dict] = None,
                    api_key: Optional[str] = None) -> Tuple:
    endpoint = os.getenv("PANCAKE_ENDPOINT")
    api_key = api_key

    try:
        url = f"{endpoint}/{path}"
        api_params = {
            "api_key": api_key
        }
        if params is not None:
            api_params.update(params)

        response = requests.get(url, params=api_params)
        if response.status_code == 200:
            return True, response.json()
        else:
            response.raise_for_status()
    except Exception as e:
        print(f"Error: {str(e)}")
        return False, str(e)

def get_shop_orders(shop_id, params, api_key):
    success, data = request_pancake(f"shops/{shop_id}/orders", params=params, api_key=api_key)
    if success:
        orders = data.get("data", [])
        total_pages = data.get("total_pages", 0)
        return orders, total_pages

    return None, None

def parse_order(order):
    result = {}

    # Partner
    partner = order.get("partner")
    customer = order.get("customer")
    items = order.get("items")
    if (
        not partner
        or not customer
        or not items
    ):
        return

    # mvd
    partner_id = partner.get("partner_id")
    order_number = ""

    if partner_id == 3:
        order_number = partner.get("order_number_vtp", "")
    elif partner_id == 1:
        order_number = partner.get("extend_code").split('.')[-1]
    else:
        return

    if not order_number:
        return

    # customer
    customer_name = customer.get("name", "")
    phone_number = customer.get("phone_numbers", [""])[0]

    result = {
        "mvd": order_number,
        "khach_hang": customer_name,
        "sdt": phone_number,
        "danh_sach_san_pham": []
    }

    items = order["items"]
    for item in items:
        variation_info = item["variation_info"]
        display_id = variation_info["display_id"]
        product_display_id = variation_info["product_display_id"]
        quantity = item["quantity"]
        fields = variation_info["fields"]
        product_name_and_fields = [variation_info["name"]] + [f"{field['name']}: {field['value']}" for field in fields]
        product_display_name = " / ".join(product_name_and_fields)

        product_name_and_fields = [variation_info["name"]] + [f"{field['name']} {field['value']}" for field in fields]
        product_detail = " ".join(product_name_and_fields) + f" x {quantity}"

        result["danh_sach_san_pham"].append({
            "ma_san_pham": product_display_id,
            "ma_mau_ma": display_id,
            "san_pham": product_display_name,
            "chi_tiet_san_pham": product_detail,
            "so_luong": quantity
        })

    # cod
    cod = order["cod"]
    facebook_page = order["page"]["name"]
    page_id = order["page"]["id"]

    # nguoi xu ly
    assigning_seller = order["assigning_seller"]["name"]

    # nguoi xac nhan
    confirm_staff = ""
    status_history = order["status_history"]
    for status_item in status_history:
        if status_item["status"] == 1:
            confirm_staff = status_item["name"]

    # ngay tao don
    inserted_at = datetime.fromisoformat(order["inserted_at"]).strftime("%d/%m/%Y")

    # kho hang
    warehouse_name = order["warehouse_info"]["name"]

    # ngay gui
    time_send_partner = datetime.fromisoformat(order["time_send_partner"]).strftime("%d/%m/%Y")
    result.update({
        "cod": cod,
        "facebook_page": facebook_page,
        "page_id": page_id,
        "nguoi_xu_ly": assigning_seller,
        "nguoi_xac_nhan": confirm_staff,
        "ngay_tao_don": inserted_at,
        "kho_hang": warehouse_name,
        "ngay_gui": time_send_partner,
    })
    return result
