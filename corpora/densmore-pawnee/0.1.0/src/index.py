import re
from pathlib import Path
from catafolk.configuration import Configuration
from catafolk.index import IndexEntry, Index
from catafolk.sources import CSVSource, FileSource


class DensmorePawneeEntry(IndexEntry):

    source_names = ["file"]

    default_source = "file"

    constants = dict(
        dataset_id="densmore-pawnee",
        file_has_music=True,
        file_has_lyrics=False,
        file_has_license=False,
        publication_key="densmore1929pawnee",
        publication_type="book",
        publication_authors="Frances Densmore",
        publication_date=1929,
    )

    mappings = dict(
        checksum = ("file", "cf_checksum"),
        path=("file", 'cf_path'),
        format=('file', 'cf_format'),
        title=('file', 'OTL'),
        location=('file', 'MLC'),
        collection_date=('file', 'ODT'),
        performers=('file', 'MPN'),
        genre=('file', 'AST'),
        meter=('file', 'AMT'),
        culture=('file', 'CNT'),
        collectors=('file', 'OCL'),
        encoders=('file', 'ENC'),
        encoding_date=('file', 'RDT'),
        copyright=('file', 'YEC'),
    )

    def get_preview_url(self):
        path = self.get('path')
        return f"https://verovio.humdrum.org/?file=osu/densmore/pawnee/{path}"

    def get_publication_preview_url(self):
        page_num = self.get("publication_page_num")
        return f'https://books.google.com/books?id=-9e65i0Fu2kC&pg=PA{page_num}'

    def get_version(self):
        eev = self.get_from_source('file', 'EEV')
        groups = re.match('Release ([\\d\\.]+)', eev)
        return groups[1]
    
    def get_publication_page_num(self):
        yor = ", ".join(self.get_from_source('file', 'YOR'))
        matches = re.match('.*Bulletin 93, page (\\d+), No\\. (\\d+)', yor)
        return matches[1]

    def get_publication_song_num(self):
        yor = ", ".join(self.get_from_source('file', 'YOR'))
        matches = re.match('.*Bulletin 93, page (\\d+), No\\. (\\d+)', yor)
        return matches[2]


def generate_index(data_dir):
    corpus_dir = Path(__file__).parent.parent
    index = Index()
    paths = data_dir.glob("data/*.krn")
    for path in paths:
        matches = re.match("pawnee(\d+)", path.name)
        entry_id = f"pawnee{matches[1]:0>2}"
        sources = dict(file=FileSource(path))
        entry = DensmorePawneeEntry(entry_id, sources)
        index.add_entry(entry)
    index.export_csv(corpus_dir / "index-test.csv")


if __name__ == "__main__":
    config = Configuration()
    data_dir = Path(config.get("data_dir")) / "densmore-pawnee" / "0.1.0"
    generate_index(data_dir)
