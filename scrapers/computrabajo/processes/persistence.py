import os
import json
from datetime import datetime

def save_to_json(results, keyword_slug):
    date_str = datetime.now().strftime("%Y_%m_%d")
    output_filename = f"scraper_{date_str}.json"

    output_path = os.path.join(
        "scrapers", "computrabajo", "data", keyword_slug, output_filename
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    return output_path
