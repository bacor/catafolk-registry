from pathlib import Path
from catafolk.configuration import Configuration
from catafolk.index import Index
from catafolk.sources import FileSource
from catafolk.corpora import EssenEntry
from catafolk.utils import load_corpus_metadata

CORPUS_DIR = Path(__file__).parent.parent
CORPUS_METADATA = load_corpus_metadata(CORPUS_DIR / "corpus.yml")
CORPUS_VERSION = CORPUS_METADATA["version"]
CORPUS_ID = CORPUS_METADATA["dataset_id"]


class BoehmeAltdeutschEntry(EssenEntry):

    constants = dict(
        dataset_id=CORPUS_ID,
        corpus_version=CORPUS_VERSION,
        file_has_music=True,
        file_has_lyrics=False,
        file_has_license=False,
        language="German",
        glottolog_id="stan1295",
        voice_use=True,
        publication_key="boehme1877altdeutsches",
    )

    sct_pattern = "A0*((\\d+)(\\w+)?)"

    def get_file_url(self):
        id = self.get("id")
        return f"https://kern.humdrum.org/cgi-bin/ksdata?file={id}&l=essen/europa/deutschl/altdeu1&format=kern"

    def get_file_preview_url(self):
        id = self.get("id")
        return (
            f"https://verovio.humdrum.org/?file=essen/europa/deutschl/altdeu1/{id}.krn"
        )


def generate_index():
    config = Configuration()
    data_dir = Path(config.get("data_dir")) / CORPUS_ID / CORPUS_VERSION
    index = Index()
    paths = data_dir.glob("data/*.krn")
    for path in paths:
        entry_id = path.stem
        sources = dict(file=FileSource(path, root=data_dir))
        entry = BoehmeAltdeutschEntry(entry_id, sources)
        index.add_entry(entry)
    index.export(CORPUS_DIR)


if __name__ == "__main__":
    generate_index()
