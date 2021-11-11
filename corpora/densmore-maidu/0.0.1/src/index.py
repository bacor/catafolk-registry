from pathlib import Path
from catafolk.configuration import Configuration
from catafolk.index import Index, IndexEntry
from catafolk.sources import CSVSource, FileSource
from catafolk.utils import load_corpus_metadata
import re
from numpy import isnan

CORPUS_DIR = Path(__file__).parent.parent
CORPUS_METADATA = load_corpus_metadata(CORPUS_DIR / "corpus.yml")
CORPUS_VERSION = CORPUS_METADATA["version"]
CORPUS_ID = CORPUS_METADATA["dataset_id"]


class DensmoreMaiduEntry(IndexEntry):

    source_names = ["file", "meta"]
    default_source = "meta"

    constants = dict(
        dataset_id=CORPUS_ID,
        corpus_version=CORPUS_VERSION,
        file_has_music=True,
        file_has_lyrics=False,
        file_has_license=False,
        publication_key="densmore1958maidu",
        publication_type="book",
        publication_title="Music of the Maidu Indians of California",
        publication_authors="Frances Densmore",
        publication_date="1958",
        collection_date="1937-03",
        collectors="Frances Densmore",
        culture="Maidu",
        culture_dplace_id="Nc12",
        encoders="Daniel Shanahan|Eva Shanahan",
        encoding_date=2014,
        copyright="Copyright 2014 Daniel and Eva Shanahan",
        location="Chico, California",
        latitude=39.74,
        longitude=-121.835556,
        auto_geocoded=False,
        language="Maiduan",
        glottolog_id="maid1262",
    )

    mappings = dict(
        file_path="file.cf_path",
        file_format="file.cf_format",
        file_checksum="file.cf_checksum",
        genres="meta.genre",
        publication_page_num="meta.page_num",
        publication_song_num="meta.song_num",
        # Defaults fields from meta fields:
        lyrics_translation="meta.free_translation",
        description="meta.analysis",
        catalogue_num="meta.catalogue_num",
        tonality="meta.tonality",
        tempo="meta.bpm",
        beat_duration="meta.beat_duration",
        meters="meta.meters",
        performers="meta.performers",
        performer_genders="meta.performer_genders",
        instrument_use="meta.instrument_use",
        percussion_use="meta.percussion_use",
        voice_use="meta.voice_use",
        instrumentation="meta.instrumentation",
    )

    export_unused_fields = True
    used_fields = [
        "file.OTL",
        "file.PDT",
        "file._comments",
        # Ignore
        "meta.title",
        "meta.free_translation",
        "meta.comments",
        "meta.culture_dplace_id",
        "meta.genre",
    ]

    def get_file_url(self):
        fn = self.get("file.cf_name")
        return (
            f"https://github.com/shanahdt/densmore/blob/master/Densmore/maidu/{fn}.krn"
        )

    def get_title(self):
        otl = self.get("file.OTL")
        matches = re.match("(No_+\d+_)?([^\.]+)(.krn)?", otl)
        if matches:
            return matches[2].replace("_", " ")
        else:
            return otl

    def get_publication_preview_url(self):
        page_num = self.get("publication_page_num") + 16
        return f"https://babel.hathitrust.org/cgi/pt?id=wu.89058380726&seq={page_num}"

    def get_comments(self):
        return self.concatenate('file._comments', 'meta.comments')


def generate_index():
    config = Configuration()
    data_dir = Path(config.get("data_dir")) / CORPUS_ID / CORPUS_VERSION
    paths = data_dir.glob("data/*.krn")

    index = Index()
    meta_source = CSVSource(CORPUS_DIR / "src/additional-metadata.csv")
    for path in paths:
        matches = re.match("No_+(\d+)", path.stem)
        entry_id = f"maidu{matches[1]:0>3}"
        sources = dict(file=FileSource(path, root=data_dir), meta=meta_source)
        entry = DensmoreMaiduEntry(entry_id, sources)
        index.add_entry(entry)
    index.export(CORPUS_DIR)


if __name__ == "__main__":
    generate_index()
