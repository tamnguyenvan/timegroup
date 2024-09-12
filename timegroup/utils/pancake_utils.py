import os
from datetime import datetime
from typing import Optional, Dict, Tuple
from functools import lru_cache

import requests
from loguru import logger
from timegroup.config import load_config


def request_pancake(path: str = None,
                    params: Optional[Dict] = None,
                    api_key: Optional[str] = None) -> Tuple:
    config = load_config()
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

def request_pancake_all(path, params, api_key, progress_callback):
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

        if progress_callback:
            progress_callback(f"Đang xử lý {page_number}/{total_pages}")

        page_number += 1
        data += request_data

    return data

def request_shop_orders(shop_id, params, api_key, progress_callback=None):
    data = request_pancake_all(f"shops/{shop_id}/orders", params=params, api_key=api_key, progress_callback=progress_callback)
    return data

def request_product_variations(shop_id, params, api_key, progress_callback=None):
    data = request_pancake_all(f"shops/{shop_id}/products/variations", params=params, api_key=api_key, progress_callback=progress_callback)
    return data