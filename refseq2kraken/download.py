import requests
import os
import subprocess
import glob
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://ftp.ncbi.nlm.nih.gov/genomes/refseq"

def download_summary(group, outdir):
    url = f"{BASE_URL}/{group}/assembly_summary.txt"
    out = os.path.join(outdir, "assembly_summary.txt")

    r = requests.get(url)
    with open(out, "wb") as f:
        f.write(r.content)

    return out

def parse_summary(file):
    urls = []
    with open(file) as f:
        for line in f:
            if line.startswith("#"):
                continue
            cols = line.strip().split("\t")

            ftp = cols[19]

            if ftp == "na" or not ftp.startswith("https"):
                continue

            urls.append(ftp)

    return urls

def download_genome(url, outdir, retries=3):
    base = url.rstrip("/").split("/")[-1]
    fname = f"{base}_genomic.fna.gz"
    full_url = f"{url}/{fname}"

    gz_path = os.path.join(outdir, fname)
    fna_path = gz_path.replace(".gz", "")

    # evita re-download (já descompactado)
    if os.path.exists(fna_path):
        print(f"[SKIP] {base}")
        return

    for attempt in range(retries):
        try:
            # STREAM download + decompress direto
            wget = subprocess.Popen(
                ["wget", "-q", "-O", "-", full_url],
                stdout=subprocess.PIPE
            )

            gunzip = subprocess.Popen(
                ["gunzip"],
                stdin=wget.stdout,
                stdout=open(fna_path, "wb")
            )

            wget.stdout.close()
            gunzip.communicate()

            if gunzip.returncode == 0:
                print(f"[OK] {base}")
                return
            else:
                print(f"[RETRY {attempt+1}] {full_url}")

        except Exception as e:
            print(f"[ERROR] {e}")

        time.sleep(random.uniform(0.5, 1.5))

    print(f"[FAIL] {full_url}")



def download_pipeline(group, threads, outdir):
    os.makedirs(outdir, exist_ok=True)

    summary = download_summary(group, outdir)
    urls = parse_summary(summary)

    print(f"[INFO] Found {len(urls)} genomes")

    results = []

    with ThreadPoolExecutor(max_workers=threads) as ex:
        futures = []

        for u in urls:
            futures.append(ex.submit(download_and_unzip, u, outdir))
            time.sleep(0.05)

        for f in as_completed(futures):
            res = f.result()
            if res:
                results.append(res)

    print("[OK] Download complete")
    return results