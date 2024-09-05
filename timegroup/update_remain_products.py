import json

from loguru import logger
from timegroup.utils.pancake_utils import request_pancake

def request_remain_products_info_one_page(shop_id, page_number):
    params = {
        "page_number": page_number
    }
    path = f"shops/{shop_id}/products/variations"
    success, response = request_pancake(path, params=params)
    if success:
        return response
    else:
        logger.error(f"Failed to get remain products info for shop {shop_id}")

def parse_product_info(json_data):
    total_pages = json_data["total_pages"]
    data = json_data["data"]
    results = []
    for item in data:
        # ma_sp
        product_display_id = item.get("product", {}).get("display_id")
        if not product_display_id:
            logger.error(f"Product display id emtpy")
            continue

        # ma_mau_ma
        display_id = item.get("display_id")
        if not display_id:
            logger.error(f"Display id emtpy")
            continue

        # category
        categories = item.get("product", {}).get("categories")
        if not categories:
            logger.error(f"Categories empty")
            continue

        category_name = categories[0].get("name")
        if not category_name:
            logger.error(f"Category empty")
            continue

        # ton_kho
        variations_warehouses = item.get("variations_warehouses")
        if not variations_warehouses:
            logger.error(f"Variations warehouses empty")
            continue

        actual_remain_quantity = variations_warehouses[0].get("actual_remain_quantity", 0)

        # tong nhap
        total_quantity = variations_warehouses[0].get("total_quantity", 0)
        results.append((product_display_id, display_id, actual_remain_quantity, category_name, total_quantity))
        logger.info(f"{results[-1]}")

    return total_pages, results

def request_remain_products_info(shop_id):
    page_number = 1
    total_pages = 1000
    results = []
    while page_number <= total_pages:
        json_data = request_remain_products_info_one_page(shop_id, page_number)
        total_pages, results_page = parse_product_info(json_data)
        results += results_page

        print(f"Page {page_number}/{total_pages}")
        page_number += 1
    return results

if __name__ == "__main__":
    shop_id = 20002121
    results = request_remain_products_info(shop_id)
    for row in results:
        print(row)