from pathlib import Path
from catafolk.configuration import Configuration
from catafolk.index import Index, IndexEntry
from catafolk.sources import CSVSource, FileSource
from catafolk.utils import load_corpus_metadata
import re

CORPUS_DIR = Path(__file__).parent.parent
CORPUS_METADATA = load_corpus_metadata(CORPUS_DIR / "corpus.yml")
CORPUS_VERSION = CORPUS_METADATA["version"]
CORPUS_ID = CORPUS_METADATA["dataset_id"]


class DensmoreChoctawEntry(IndexEntry):

    source_names = ["file", "meta"]
    default_source = "meta"

    constants = dict(
        dataset_id=CORPUS_ID,
        corpus_version=CORPUS_VERSION,
        file_has_music=True,
        file_has_lyrics=False,
        file_has_license=False,
        publication_key="densmore1943choctaw",
        publication_type="book",
        publication_title="Choctaw music",
        publication_authors="Frances Densmore",
        publication_date="1943",
        collection_date="1933-01",
        collectors="Frances Densmore",
        culture="Choctaw",
        culture_dplace_id="Ng12",
        location="Philadelphia, Mississippi, United States of America",
        latitude=32.774167,
        longitude=-89.112778,
        auto_geocoded=False,
        language="Choctaw",
        glottolog_id="choc1276",
        lyrics_translation="meta.free_translation",
    )

    mappings = dict(
        file_path="file.cf_path",
        file_format="file.cf_format",
        file_checksum="file.cf_checksum",
        title="file.OTL",
        encoders="file.ENC",
        encoding_date="file.END",
        genres="file.SUPERFUNCTION",
        copyright="file.YEC",
        version="file.EEV",
        description="meta.analysis",
        warnings="file.RWG",
        metric_classification="file.AMT",
        tempo="meta.bpm",
        comments="file._comments",
        
        # Defaults fields from meta fields:
        tonality = "meta.tonality",
        beat_duration="meta.beat_duration",
        meters="meta.meters",
        performers="meta.performers",
        performer_genders="meta.performer_genders",
        instrument_use="meta.instrument_use",
        percussion_use="meta.percussion_use",
        voice_use="meta.voice_use",
        instrumentation="meta.instrumentation",
        catalogue_number="meta.catalog_num"
    )

    export_unused_fields=True
    used_fields = [
        "file.OTL",
        "file.ENC",
        "file.END",
        "file.SUPERFUNCTION",
        "file.YEC",
        "file.EEV",
        "file.RWG",
        "file.AMT",
        "file.YOR",
        "file.ODT",
        "file.mpn",
        "file._comments",

        # Constants
        "file.CNT",
        "file.TXO",
        "file.OCL",
        "file.PPR",
        "file.PPP",
        "file.OCY",
        
        # Ignore
        "meta.title",
        "meta.publication_page_num",
        "meta.publication_song_num",
    ]
    
    def get_publication_page_num(self):
        yor = self.get("file.YOR")
        matches = re.match("Bulletin 136, page (\\d+), No. (.+)", yor[-1])
        if matches is not None:
            return matches[1]
        else:
            return None

    def get_publication_song_num(self):
        yor = self.get("file.YOR")
        matches = re.match("Bulletin 136, page (\\d+), No. (.+)", yor[-1])
        if matches is not None:
            return matches[2]
        else:
            return None


def generate_index():
    config = Configuration()
    data_dir = Path(config.get("data_dir")) / CORPUS_ID / CORPUS_VERSION
    paths = data_dir.glob("data/*.krn")

    index = Index()
    meta_source = CSVSource(CORPUS_DIR / "src/additional-metadata.csv")
    for path in paths:
        entry_id = path.stem
        sources = dict(file=FileSource(path, root=data_dir), meta=meta_source)
        entry = DensmoreChoctawEntry(entry_id, sources)
        index.add_entry(entry)
    index.export(CORPUS_DIR)


if __name__ == "__main__":
    generate_index()
