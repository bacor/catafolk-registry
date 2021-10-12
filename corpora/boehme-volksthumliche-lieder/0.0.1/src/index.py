from pathlib import Path
from catafolk.configuration import Configuration
from catafolk.index import Index
from catafolk.corpora import EssenEntry
from catafolk.sources import FileSource

CORPUS_ID = "boehme-volksthumliche-lieder"
VERSION = "0.0.1"


class BoehmeVolksthumlicheLiederEntry(EssenEntry):
    constants = dict(
        dataset_id=CORPUS_ID,
        file_has_music=True,
        file_has_lyrics=False,
        file_has_license=False,
        culture="German",
        language="German",
        glottolog_id="stan1295",
        voice_use=True,
        publication_key="boehme1895volksthumliche",
    )

    sct_pattern = "A0*((\\d+)(\\w+)?)"

    def get_file_url(self):
        id = self.get("id")
        return f"https://kern.humdrum.org/cgi-bin/ksdata?file={id}.krn&l=essen/europa/deutschl/boehme&format=kern"

    def get_file_preview_url(self):
        id = self.get("id")
        return (
            f"https://verovio.humdrum.org/?file=essen/europa/deutschl/boehme/{id}.krn"
        )


def generate_index():
    config = Configuration()
    data_dir = Path(config.get("data_dir")) / CORPUS_ID / VERSION
    corpus_dir = Path(__file__).parent.parent
    paths = data_dir.glob("data/*.krn")

    index = Index()
    for path in paths:
        entry_id = path.stem
        sources = dict(file=FileSource(path, root=data_dir))
        entry = BoehmeVolksthumlicheLiederEntry(entry_id, sources)
        index.add_entry(entry)
    index.export_csv(corpus_dir / "index.csv")


if __name__ == "__main__":
    generate_index()
