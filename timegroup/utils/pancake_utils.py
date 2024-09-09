import os
from datetime import datetime
from typing import Optional, Dict, Tuple

import requests
from loguru import logger
from timegroup.config import config


def request_pancake(path: str = None,
                    params: Optional[Dict] = None,
                    api_key: Optional[str] = None) -> Tuple:
    endpoint = config["api_endpoint"]
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

def request_pancake_all(path, params, api_key):
    page_number = 1
    total_pages = 1000
    data = []
    while page_number < total_pages + 1:
        params.update({"page_number": page_number})
        success, response = request_pancake(path, params, api_key=api_key)
        if not success:
            break

        request_data = response.get("data", [])
        total_pages = response.get("total_pages", 0)
        page_number += 1
        data += request_data

    return data

def request_shop_orders(shop_id, params, api_key):
    data = request_pancake_all(f"shops/{shop_id}/orders", params=params, api_key=api_key)
    return data
    # success, data = request_pancake(f"shops/{shop_id}/orders", params=params, api_key=api_key)
    # if success:
    #     orders = data.get("data", [])
    #     total_pages = data.get("total_pages", 0)
    #     return orders, total_pages

    # return None, None

def request_product_variations(shop_id, params, api_key):
    data = request_pancake_all(f"shops/{shop_id}/products/variations", params=params, api_key=api_key)
    # import json
    # for item in data[:3]:
    #     print(json.dumps(item))
    return data
    # success, data = request_pancake(f"shops/{shop_id}/products", params=params, api_key=api_key)
    # if success:
    #     orders = data.get("data", [])
    #     total_pages = data.get("total_pages", 0)
    #     return orders, total_pages

    # return None, None