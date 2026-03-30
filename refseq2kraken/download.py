import requests
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed  # 🔁 MODIFY
import glob  # 🔥 ADD
import time  # 🔥 ADD
import random  # 🔥 ADD

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

            # 🔥 ADD (validação)
            if ftp == "na" or not ftp.startswith("https"):
                continue

            urls.append(ftp)

    return urls

def download_genome(url, outdir, retries=3):
    # 🔥 remove barra final se existir
    base = url.rstrip("/").split("/")[-1]

    # 🔥 monta nome correto do arquivo
    fname = f"{base}_genomic.fna.gz"
    full_url = f"{url}/{fname}"

    output_file = os.path.join(outdir, fname)

    # 🔥 evita re-download
    if os.path.exists(output_file):
        print(f"[SKIP] {fname}")
        return

    for attempt in range(retries):
        result = subprocess.run(
            ["wget", "-q", "-P", outdir, full_url]
        )

        if result.returncode == 0:
            print(f"[OK] {fname}")
            return
        else:
            print(f"[RETRY {attempt+1}] {full_url}")

        import time, random
        time.sleep(random.uniform(0.5, 1.5))

    print(f"[FAIL] {full_url}")

def unzip_all(outdir):
    gz_files = glob.glob(f"{outdir}/*.gz")

    if not gz_files:
        print("[WARNING] No .gz files found")
        return

    with ThreadPoolExecutor(max_workers=8) as ex:  # paralelismo
        ex.map(lambda f: subprocess.run(["gunzip", f]), gz_files)

def download_pipeline(group, threads, outdir):
    os.makedirs(outdir, exist_ok=True)

    summary = download_summary(group, outdir)
    urls = parse_summary(summary)

    print(f"[INFO] Found {len(urls)} genomes")

    # 🔥 ADD (controle real + tracking)
    with ThreadPoolExecutor(max_workers=threads) as ex:
        futures = [ex.submit(download_genome, u, outdir) for u in urls]

        for f in as_completed(futures):
            pass

    unzip_all(outdir)

    print("[OK] Download complete")