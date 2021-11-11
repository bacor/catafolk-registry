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


class DensmorePuebloEntry(IndexEntry):

    source_names = ["meta", "file"]
    default_source = "meta"

    constants = dict(
        dataset_id=CORPUS_ID,
        corpus_version=CORPUS_VERSION,
        file_has_music=True,
        file_has_lyrics=True,
        collection_date_earliest=1928,
        collection_date_latest=1957,
        encoders=["Daniel Shanahan", "Eva Shanahan"],
        encoding_date="2014",
        copyright="Copyright 2014 Daniel and Eva Shanahan",
        auto_geocoded=False,
        performer_genders="male", # See Densmore 1957, p XII
        voice_use=True,
        publication_key="densmore1957pueblo",
        publication_type="book",
        publication_authors="Frances Densmore",
        publication_title="Pueblo Music",
        publication_date=1957,
    )

    mappings = dict(
        file_path="file.cf_path",
        file_format="file.cf_format",
        file_checksum="file.cf_checksum",
        collectors="meta.collector",
        collection_date="meta.collection_date",
        culture="meta.culture",
        location="meta.location",
        latitude="meta.latitude",
        longitude="meta.longitude",
        performers="meta.performer",
        publication_page_num="meta.page_num",
        publication_song_num="meta.song_num",
        catalogue_number="meta.catalogue_num"
    )

    export_unused_fields = True
    used_fields = [
        "file.OTL",
        "file.PDT",
        "meta.genre",
    ]

    def get_genres(self):
        genres = self.get('meta.genres')
        if genres is not None:
            return genres.lower().replace('song', '').strip()
        else:
            return None

    def get_file_url(self):
        fn = self.get("filename")
        return f"https://github.com/shanahdt/densmore/raw/master/Densmore/acoma/{fn}.krn"

    def get_publication_preview_url(self):
        seq = self.get('publication_page_num') + 12
        return f'https://babel.hathitrust.org/cgi/pt?id=mdp.39015024865878&view=1up&seq={seq}'

    def get_language(self):
        mapping = dict(Acoma="Acoma", Cochiti="Cochiti", Isleta="Isleta", Zuni="Zuñi")
        culture = self.get('culture')
        return mapping.get(culture, None)

    def get_glottolog_id(self):
        mapping = dict(Acoma="acom145", Cochiti="coch1273", Isleta="isle1245", Zuni="zuni1245")
        culture = self.get('culture')
        return mapping.get(culture, None)

    def get_title(self):
        otl = self.get('file.OTL')
        matches = re.match('No_(\d+)_([^\.]+).krn', otl)
        if matches:
            return matches[2].replace('_', ' ')
        else:
            return None

    def get_publication_song_num(self):
        otl = self.get('file.OTL')
        matches = re.match('No_(\d+)_([^\.]+).krn', otl)
        if matches:
            return matches[1]
        else:
            return None

def generate_index():
    config = Configuration()
    data_dir = Path(config.get("data_dir")) / CORPUS_ID / CORPUS_VERSION
    index = Index()
    paths = data_dir.glob("data/*.krn")
    meta_source = CSVSource(CORPUS_DIR / "src/additional-metadata.csv")
    for path in paths:
        matches = re.match("No_+(\d+)", path.stem)
        entry_id = f"pueblo{matches[1]:0>2}"
        sources = dict(file=FileSource(path, root=data_dir), meta=meta_source)
        entry = DensmorePuebloEntry(entry_id, sources)
        index.add_entry(entry)

    index.export(CORPUS_DIR)


if __name__ == "__main__":
    generate_index()
