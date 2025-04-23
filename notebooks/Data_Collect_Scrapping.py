import os
import time
import random
import json
import csv
import pandas as pd
from tqdm import tqdm
from PIL import Image
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import requests

# === PARAMÈTRES GLOBAUX ===
NB_QUERIES = 7
NB_PAGES_PER_QUERY = 1000
MAX_LINKS = 1000000
WINDOW_WIDTH = 1280
MIN_HEIGHT = 800
MAX_HEIGHT = 10_000

IMG_DIR = "dataset_images"
ERROR_DIR = "errors"
META_JSON = "dataset_metadata.json"
META_CSV = "dataset_metadata.csv"
LOG_FILE = "log.txt"

SERPAPI_API_KEY = "edd29fc5094a91be55b8ee5fea56d43c2202cb7b858bb866284fa56dc5deccd0"  # 📅 Insère ta clé API ici

os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(ERROR_DIR, exist_ok=True)
metadata = {}

# === Requêtes aléatoires ===
queries = [
    "AI OR Data Science OR Machine Learning OR Deep Learning",
    "education ",
    "blog OR politics OR news",
    "health OR fitness OR wellness",
    "Food OR Cooking OR Recipes",
    "fashion OR clothing OR style OR trends",
    "articles"
]

# === Recherche via SerpAPI ===
def get_google_links_serpapi(query, max_results=100):
    results = []
    page = 0
    while len(results) < max_results:
        url = "https://serpapi.com/search"
        params = {
            "engine": "google",
            "q": query,
            "api_key": SERPAPI_API_KEY,
            "num": 100,
            "start": page * 100
        }
        response = requests.get(url, params=params)
        data = response.json()
        if "error" in data:
            print(f"[ERREUR SERPAPI] {data['error']}")
            break

        organic = data.get("organic_results", [])
        for r in organic:
            link = r.get("link")
            if link:
                results.append(link)
            if len(results) >= max_results:
                break
        if not organic:
            break
        page += 1
    return results

# === Scroll automatique ===
def scroll_smooth(driver, pause_time=1.0, max_scrolls=30):
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(max_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# === Démarrage du navigateur furtif ===
options = uc.ChromeOptions()
options.headless = True
options.add_argument(f"--window-size={WINDOW_WIDTH},{MIN_HEIGHT}")
options.add_argument("--disable-blink-features=AutomationControlled")
driver = uc.Chrome(options=options)

# === Lecture JSON existant ===
if os.path.exists(META_JSON):
    with open(META_JSON, "r") as f:
        metadata = json.load(f)
        existing_urls = {v["url"] for v in metadata.values()}
else:
    existing_urls = set()

# === Collecte ===
with open(LOG_FILE, "w", encoding="utf-8") as log:
    total_count = len(metadata)
    selected_queries = random.sample(queries, NB_QUERIES)

    for qidx, query in enumerate(selected_queries):
        print(f"\n🔍 [{qidx+1}/{NB_QUERIES}] Requête : {query}")
        log.write(f"\n--- Query: {query} ---\n")

        links = get_google_links_serpapi(query, max_results=MAX_LINKS)
        print(f"[DEBUG] {len(links)} liens trouvés via SerpAPI pour : {query}")

        random.shuffle(links)
        success = 0

        for idx, url in tqdm(enumerate(links), total=NB_PAGES_PER_QUERY, desc=f"  → {query[:30]}..."):
            print(f"[DEBUG] → test de l'URL : {url}")
            if success >= NB_PAGES_PER_QUERY:
                break
            if url in existing_urls:
                continue

            try:
                driver.get(url)
                time.sleep(3)

                body = driver.find_element(By.TAG_NAME, "body").text.strip()
                if len(body) < 200:
                    print(f"[DEBUG] Ignorée (page trop vide) : {url}")
                    continue

                real_height = driver.execute_script(
                    "return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)"
                )
                target_height = max(MIN_HEIGHT, min(real_height, MAX_HEIGHT))
                driver.set_window_size(WINDOW_WIDTH, target_height)
                scroll_smooth(driver, pause_time=1, max_scrolls=20)
                driver.set_window_size(WINDOW_WIDTH, target_height)

                base_name = f"{query.replace(' ', '_')}_{success}_{int(time.time())}"
                temp_png = os.path.join(IMG_DIR, base_name + ".png")
                final_jpg = os.path.join(IMG_DIR, base_name + ".jpg")

                driver.save_screenshot(temp_png)
                img = Image.open(temp_png).convert("RGB")
                img.save(final_jpg, "JPEG", quality=90)
                print(f"[✓] Image capturée : {final_jpg}")
                os.remove(temp_png)

                metadata[base_name + ".jpg"] = {
                    "url": url,
                    "query": query,
                    "height": target_height
                }
                existing_urls.add(url)
                log.write(f"[✓] {base_name}.jpg → {url}\n")
                success += 1
                total_count += 1

            except Exception as e:
                print(f"[ERREUR] {url} → {e}")
                err_file = os.path.join(ERROR_DIR, f"error_{qidx}_{idx}.txt")
                with open(err_file, "w", encoding="utf-8") as f:
                    f.write(f"URL: {url}\nErreur: {str(e)}")
                log.write(f"[!] ERREUR {url}\n{str(e)}\n")
                continue
        print(f"✅ {success} images capturées pour la requête : {query}")

# === Sauvegarde JSON + CSV
with open(META_JSON, "w") as f:
    json.dump(metadata, f, indent=2)

csv_data = [
    {"filename": fname, "url": info["url"], "query": info["query"], "height": info["height"]}
    for fname, info in metadata.items()
]
df = pd.DataFrame(csv_data)
df.to_csv(META_CSV, index=False)

print(f"\n📅 {total_count} images capturées au total.")
print(f"📁 Images : {IMG_DIR}")
print(f"📄 Metadata JSON : {META_JSON}")
print(f"📄 Metadata CSV : {META_CSV}")
print(f"📝 Log : {LOG_FILE}")

driver.quit()
