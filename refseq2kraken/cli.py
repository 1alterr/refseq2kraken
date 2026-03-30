import argparse
import glob

from refseq2kraken.download import download_pipeline
from refseq2kraken.kraken import init_db, add_to_library, build_db
from refseq2kraken.utils import ensure_dir


def main():
    parser = argparse.ArgumentParser(
        prog="refseq2kraken",
        description="RefSeq → Kraken2 pipeline"
    )

    subparsers = parser.add_subparsers(dest="command")

    # ======================
    # TAXONOMY
    # ======================
    p_tax = subparsers.add_parser(
        "taxonomy",
        help="Download NCBI taxonomy"
    )
    p_tax.add_argument("--db", required=True, help="Kraken DB path")

    # ======================
    # DOWNLOAD
    # ======================
    p_dl = subparsers.add_parser(
        "download",
        help="Download and process RefSeq sequences"
    )
    p_dl.add_argument("--group", required=True, help="RefSeq group (plant, fungi, etc)")
    p_dl.add_argument("--threads", type=int, default=6)
    p_dl.add_argument("--outdir", required=True)

    # ======================
    # ADD
    # ======================
    p_add = subparsers.add_parser(
        "add",
        help="Add .fna files to Kraken2 library"
    )
    p_add.add_argument("--input", required=True, help="Directory with .fna files")
    p_add.add_argument("--db", required=True)

    # ======================
    # BUILD
    # ======================
    p_build = subparsers.add_parser(
        "build",
        help="Build the Kraken2 database"
    )
    p_build.add_argument("--db", required=True)
    p_build.add_argument("--threads", type=int, default=32)

    args = parser.parse_args()

    # ======================
    # EXECUTION
    # ======================
    if args.command == "taxonomy":
        init_db(args.db)

    elif args.command == "download":
        ensure_dir(args.outdir)
        download_pipeline(args.group, args.threads, args.outdir)

    elif args.command == "add":
        fna_files = glob.glob(f"{args.input}/*.fna")
        add_to_library(fna_files, args.db)

    elif args.command == "build":
        build_db(args.db, args.threads)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()