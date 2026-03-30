import requests
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

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
            urls.append(cols[19])
    return urls

def download_genome(url, outdir):
    fname = url.split("/")[-1]
    full_url = f"{url}/{fname}_genomic.fna.gz"

    subprocess.run([
        "wget", "-q",
        "-P", outdir,
        full_url
    ])

def unzip_all(outdir):
    subprocess.run(f"gunzip {outdir}/*.gz", shell=True)

def download_pipeline(group, threads, outdir):
    os.makedirs(outdir, exist_ok=True)

    summary = download_summary(group, outdir)
    urls = parse_summary(summary)

    print(f"[INFO] Found {len(urls)} genomes")

    with ThreadPoolExecutor(max_workers=threads) as ex:
        for u in urls:
            ex.submit(download_genome, u, outdir)

    unzip_all(outdir)

    print("[OK] Download complete")