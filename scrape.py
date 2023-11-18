import requests
from bs4 import BeautifulSoup
from collections import deque
import json
import re

visited_urls = set()
urls_to_visit = deque(["https://www.aliexpress.us/item/3256804924530585.html"])


while urls_to_visit:
    prices = []
    current_url = urls_to_visit.popleft()
    if current_url not in visited_urls:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(current_url, headers=headers)

        # For debugging
        # soup = BeautifulSoup(response.text, 'html.parser')
        # with open('output.html', 'w', encoding='utf-8') as file:
        #     file.write(str(soup))

        if response.status_code == 200:
            html_content = response.text

        # For debugging
        # print(html_content[:1000])

        run_params_pattern_full = re.compile(
            r"window\.runParams\s*=\s*{\s*data:\s*({.*?})\s*};", re.DOTALL
        )

        run_params_match_full = run_params_pattern_full.search(html_content)

        if run_params_match_full:
            json_str_full = run_params_match_full.group(1)
            try:
                run_params_json_full = json.loads(json_str_full)

                # For debugging
                # with open("result.json", "w") as f:
                #     json.dump(run_params_json_full, f)
                for sku in run_params_json_full["priceComponent"]["skuPriceList"]:
                    low = float("inf")
                    high = -float("inf")
                    low = min(low, sku["skuVal"]["skuActivityAmount"]["value"])
                    high = max(high, sku["skuVal"]["skuActivityAmount"]["value"])
                prices.append([current_url, low, high])
            except json.JSONDecodeError as e:
                print(f"JSON decoding failed: {e}")
        else:
            print("Pattern not found in HTML")
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

    print(prices)
