import re
from pathlib import Path
from catafolk.configuration import Configuration
from catafolk.index import IndexEntry, Index
from catafolk.sources import CSVSource, FileSource
from catafolk.utils import load_corpus_metadata

CORPUS_DIR = Path(__file__).parent.parent
CORPUS_METADATA = load_corpus_metadata(CORPUS_DIR / "corpus.yml")
CORPUS_VERSION = CORPUS_METADATA["version"]
CORPUS_ID = CORPUS_METADATA["dataset_id"]


class DensmoreTetonSiouxEntry(IndexEntry):

    source_names = ["file"]

    constants = dict(
        dataset_id=CORPUS_ID,
        corpus_version=CORPUS_VERSION,
        file_has_music=True,
        file_has_lyrics=False,
        file_has_license=True,
        collection_date_earliest=1911,
        collection_date_latest=1914,
        culture_dplace_id="Ne8",
        encoders=["Craig Stuart Sapp"],
        license_id="CC BY-NC-SA 4.0",
        auto_geocoded=False,
        language="Sioux",
        glottolog_id="siou1253",
        publication_key="densmore1918teton",
        publication_type="book",
        publication_authors="Frances Densmore",
        publication_title="Teton Sioux Music",
        publication_date=1918,
    )

    mappings = dict(
        file_path="file.cf_path",
        file_format="file.cf_format",
        file_checksum="file.cf_checksum",
        genres="file.AGN",
        file_url="file.URL",
        collectors="file.OCL",
        culture="file.CNT",
        encoders="file.ENC",
        encoding_date="file.END",
        copyright="file.YEC",
        location="file.MLC",
        title="file.OTL@ENG",
        publication_page_num="file.PPG",
        publication_song_num="file.ONM",
        comments="file.RNB",
    )

    export_unused_fields = True
    used_fields = [
        "file.MPN@@SIO",
        "file.MPN@ENG",
        "file.YEM",
        "file.PPR",
        "file.PPP",
        "file.PDT",
        "file.YOR1",
        "file.YOR2",
        "file.ARL",
        "file.catalog",
        "file.title",
        "file.EED",
        "file.MRD"
    ]

    def get_file_preview_url(self):
        fn = self.get('file.cf_name')
        return f'http://verovio.humdrum.org/?file=folk/sioux/{fn}.krn'

    def get_publication_preview_url(self):
        page = self.get('publication_page_num')
        return f'https://books.google.nl/books?id=Adw_AAAAYAAJ&pg=PA{page}'

    def get_latitude(self):
        arl = self.get('file.ARL')
        matches = re.match("([\\d\\.-]+)\/([\\d\\.-]+)", arl)
        return matches[1]
    
    def get_longitude(self):
        arl = self.get('file.ARL')
        matches = re.match("([\\d\\.-]+)\/([\\d\\.-]+)", arl)
        return matches[2]

    def get_performers(self):
        sio_name = self.get('file.MPN@@SIO')
        eng_name = self.get('file.MPN@ENG')
        return f"{sio_name} ({eng_name})"

    def get_catalogue_number(self):
        num = self.get('file.catalog')
        matches = re.match('Catalogue No\\. (\\d+)', num)
        return matches[1]

def generate_index():
    config = Configuration()
    data_dir = Path(config.get("data_dir")) / CORPUS_ID / CORPUS_VERSION
    index = Index()
    paths = data_dir.glob("data/kern/*.krn")
    for path in paths:
        entry_id = path.stem
        sources = dict(file=FileSource(path, root=data_dir))
        entry = DensmoreTetonSiouxEntry(entry_id, sources)
        index.add_entry(entry)

    index.export(CORPUS_DIR)


if __name__ == "__main__":
    generate_index()
