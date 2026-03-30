import argparse
from refseq2kraken.download import download_pipeline
from refseq2kraken.kraken import init_db, add_to_library, build_db
from refseq2kraken.utils import ensure_dir


def main():
    parser = argparse.ArgumentParser(
        description="RefSeq → Kraken2 pipeline"
    )

    parser.add_argument("--group", required=True)
    parser.add_argument("--db", required=True)
    parser.add_argument("--outdir", required=True)

    parser.add_argument("--download-threads", type=int, default=6)
    parser.add_argument("--build-threads", type=int, default=32)

    parser.add_argument("--skip-init", action="store_true")
    parser.add_argument("--skip-download", action="store_true")
    parser.add_argument("--skip-add", action="store_true")
    parser.add_argument("--skip-build", action="store_true")

    args = parser.parse_args()

    ensure_dir(args.outdir)

    fna_files = []

    # 🔥 1. INIT
    if not args.skip_init:
        init_db(args.db)

    # 🔥 2. DOWNLOAD
    if not args.skip_download:
        fna_files = download_pipeline(
            args.group,
            args.download_threads,
            args.outdir
        )

    # 🔥 3. ADD
    if not args.skip_add:
        if not fna_files:
            import glob
            fna_files = glob.glob(f"{args.outdir}/*.fna")

        add_to_library(fna_files, args.db)

    # 🔥 4. BUILD
    if not args.skip_build:
        build_db(args.db, args.build_threads)

    print("[DONE]")


if __name__ == "__main__":
    main()