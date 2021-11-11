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


class DensmorePawneeEntry(IndexEntry):

    source_names = ["file"]

    default_source = "file"

    constants = dict(
        dataset_id=CORPUS_ID,
        corpus_version=CORPUS_VERSION,
        file_has_music=True,
        file_has_lyrics=False,
        file_has_license=False,
        publication_key="densmore1929pawnee",
        publication_type="book",
        publication_authors="Frances Densmore",
        publication_title="Pawnee Music",
        publication_date=1929,
    )

    mappings = dict(
        checksum="file.cf_checksum",
        path="file.cf_path",
        format="file.cf_format",
        title="file.OTL",
        location="file.MLC",
        collection_date="file.ODT",
        performers="file.MPN",
        genres="file.AST",
        meters="file.AMT",
        culture="file.CNT",
        collectors="file.OCL",
        encoders="file.ENC",
        encoding_date="file.RDT",
        copyright="file.YEC",
        comments="file._comments",
        warnings="file.RWG"
    )

    export_unused_fields = True
    used_fields = [
        "file.HAO",
        "file.EEV",
        "file.PDT",
        "file.PPR",
        "file.PPP",
        "file.YOR",
        "file.HTX",
        "file.AIN",
    ]

    def get_preview_url(self):
        path = self.get("path")
        return f"https://verovio.humdrum.org/?file=osu/densmore/pawnee/{path}"

    def get_publication_preview_url(self):
        page_num = self.get("publication_page_num")
        return f"https://books.google.com/books?id=-9e65i0Fu2kC&pg=PA{page_num}"

    def get_version(self):
        eev = self.get_from_source("file", "EEV")
        groups = re.match("Release ([\\d\\.]+)", eev)
        return groups[1]

    def get_publication_page_num(self):
        yor = ", ".join(self.get_from_source("file", "YOR"))
        matches = re.match(".*Bulletin 93, page (\\d+), No\\. (\\d+)", yor)
        return matches[1]

    def get_publication_song_num(self):
        yor = ", ".join(self.get_from_source("file", "YOR"))
        matches = re.match(".*Bulletin 93, page (\\d+), No\\. (\\d+)", yor)
        return matches[2]

    def get_description(self):
        hao = self.get('file.HAO')
        if hao == "[no description]":
            return None
        elif type(hao) == str:
            return hao
        else:
            return "\n".join(hao)

    def get_instrumentation(self):
        return self.get('file.AIN').replace('vox', 'voice')

    def get_lyrics_translation(self):
        htx = self.get('file.HTX')
        if htx == '[no free translation]':
            return None
        else:
            return htx

    # def get_comments(self):
    #     return self.concatenate('meta.comments', 'file._comments')


def generate_index():
    config = Configuration()
    data_dir = Path(config.get("data_dir")) / CORPUS_ID / CORPUS_VERSION
    index = Index()
    paths = data_dir.glob("data/*.krn")
    for path in paths:
        matches = re.match("pawnee(\d+)", path.name)
        entry_id = f"pawnee{matches[1]:0>2}"
        sources = dict(file=FileSource(path))
        entry = DensmorePawneeEntry(entry_id, sources)
        index.add_entry(entry)
    index.export(CORPUS_DIR)


if __name__ == "__main__":
    generate_index()
