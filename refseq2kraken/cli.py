import typer
from refseq2kraken.download import download_pipeline
from refseq2kraken.kraken import add_to_library, build_db

app = typer.Typer()

@app.command()
def download(
    group: str = typer.Option(..., help="refseq group (plant, invertebrate, etc)"),
    threads: int = 8,
    outdir: str = "data"
):
    download_pipeline(group, threads, outdir)

@app.command()
def add(
    input_dir: str,
    db: str
):
    add_to_library(input_dir, db)

@app.command()
def build(
    db: str,
    threads: int = 16
):
    build_db(db, threads)

if __name__ == "__main__":
    app()