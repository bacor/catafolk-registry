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


class DensmoreNootkaEntry(IndexEntry):

    source_names = ["meta", "file"]
    default_source = "meta"

    constants = dict(
        dataset_id=CORPUS_ID,
        corpus_version=CORPUS_VERSION,
        file_has_music=True,
        file_has_lyrics=True,
        file_has_license=False,
        collectors="Frances Densmore",
        collection_date_earliest=1923,
        collection_date_latest=1926,
        encoders=["Daniel Shanahan", "Eva Shanahan"],
        encoding_date="2014",
        copyright="Copyright 2014 Daniel and Eva Shanahan",
        location="Neah Bay, Washington, U.S.A",
        latitude=48.365556,
        longitude=-124.615556,
        auto_geocoded=False,
        voice_use=True,
        publication_key="densmore1939nootka",
        publication_type="book",
        publication_authors="Frances Densmore",
        publication_date=1939,
    )

    mappings = dict(
        file_path="file.cf_path",
        file_format="file.cf_format",
        file_checksum="file.cf_checksum",
        culture="meta.culture",
        performers="meta.performer",
        performer_genders="meta.performer_gender",
        tempo="meta.bpm",
        publication_song_num="meta.song_num",
        publication_page_num="meta.page_num",
    )

    def get_file_url(self):
        filename = self.get("filename")
        return f"https://github.com/shanahdt/densmore/blob/master/Densmore/nootka/{filename}.krn"

    def get_glottolog_id(self):
        mapping = dict(Makah="maka1318", Clayoquot="nuuc1236", Quileute="quil1240")
        culture = self.get("culture")
        return mapping.get(culture, None)

    def get_language(self):
        mapping = dict(Quileute="Quileute", Clayoquot="Nuu-chah-nulth", Makah="Makah")
        culture = self.get("culture")
        return mapping.get(culture, None)

    def get_publication_preview_url(self):
        page_num = self.get("publication_page_num") + 52
        return (
            f"https://babel.hathitrust.org/cgi/pt?id=mdp.39015025347033&seq={page_num}"
        )

    def get_publication_song_num(self):
        otl = self.get_from_source("file", "OTL")
        matches = re.match("No_+(\d+)_([^\.]+).krn", otl)
        return int(matches[1])

    def get_title(self):
        otl = self.get_from_source("file", "OTL")
        matches = re.match("No_+(\d+)_([^\.]+).krn", otl)
        title = matches[2].replace("_", " ")
        return title

    def get_genres(self):
        superfunction = self.get_from_source("file", "SUPERFUNCTION")
        if type(superfunction) == str:
            return superfunction
        else:
            return sorted(set(superfunction))

    def get_other_fields(self):
        return dict(
            language_type=self.get_from_source("file", "LANG"),
            language_family=self.get_from_source("file", "LING_GROUP"),
            social_function=self.get_from_source("file", "SOCIAL_FUNCTION"),
        )


def generate_index():
    config = Configuration()
    data_dir = Path(config.get("data_dir")) / CORPUS_ID / CORPUS_VERSION
    corpus_dir = Path(__file__).parent.parent
    index = Index()
    paths = data_dir.glob("data/*.krn")
    meta_source = CSVSource(corpus_dir / "src/additional-metadata.csv")
    for path in paths:
        matches = re.match("No_+(\d+)", path.name)
        entry_id = f"nootka{matches[1]:0>3}"
        sources = dict(file=FileSource(path, root=data_dir), meta=meta_source)
        entry = DensmoreNootkaEntry(entry_id, sources)
        index.add_entry(entry)

    index.export(CORPUS_DIR)


if __name__ == "__main__":
    generate_index()
