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


class DensmoreMenomineeEntry(IndexEntry):

    source_names = ["file", "meta"]
    default_source = "meta"

    constants = dict(
        dataset_id=CORPUS_ID,
        corpus_version=CORPUS_VERSION,
        file_has_music=True,
        file_has_lyrics=False,
        file_has_license=False,
        publication_key="densmore1932menominee",
        publication_type="book",
        publication_title="Menominee Music",
        publication_authors="Frances Densmore",
        publication_date="1932",
        collectors="Frances Densmore",
        collection_date_earliest="1925",
        collection_date_latest="1929",
        culture="Menominee",
        culture_dplace_id="Nf9",
        encoders='Daniel Shanahan|Eva Shanahan',
        encoding_date=2014,
        copyright='Copyright 2014 Daniel and Eva Shanahan',
        location="Menominee County, Wisconsin, U.S.A.",
        latitude=45.02,
        longitude=-88.70,
        auto_geocoded=False,
        language="Menominee",
        glottolog_id="meno1252",
    )

    mappings = dict(
        file_path="file.cf_path",
        file_format="file.cf_format",
        file_checksum="file.cf_checksum",
        genres="file.SUPERFUNCTION",
        
        # Defaults fields from meta fields:
        publication_song_num='meta.song_num',
        publication_page_num='meta.page_num',
        lyrics="meta.lyrics",
        lyrics_translation="meta.free_translation",
        catalogue_num="meta.catalogue_num",
        tonality = "meta.tonality",
        tempo="meta.bpm",
        beat_duration="meta.beat_duration",
        meters="meta.meters",
        performers="meta.performers",
        performer_genders="meta.performer_genders",
        instrumentation="meta.instrumentation",
        instrument_use="meta.instrument_use",
        percussion_use="meta.percussion_use",
        voice_use="meta.voice_use",
    )

    export_unused_fields=True
    used_fields = [
        "file.OTL",
        "file.PDT",
        "file._comments",
        "file.SUPERFUNCTION",

        # # Ignore
        "meta.comments",
        "meta.catalogue_num",
    ]

    def get_file_url(self):
        fn = self.get('file.cf_name')
        return f'https://github.com/shanahdt/densmore/blob/master/Densmore/menominee/{fn}.krn'
    

    def get_title(self):
        otl = self.get('file.OTL')
        matches = re.match('(No_+\d+_)?([^\.]+)(.krn)?', otl)
        if matches:
            return matches[2].replace('_', ' ')
        else:
            return otl
    
    def get_publication_preview_url(self):
        page_num = self.get('publication_page_num') + 38
        return f'https://babel.hathitrust.org/cgi/pt?id=mdp.39015024872874&seq={page_num}'

    def get_comments(self):
        comments = [self.get('file._comments'), self.get('meta.comments')]
        comments = [c for c in comments if c is not None and c != '']
        if len(comments) == 0:
            return None
        else:
            return comments


def generate_index():
    config = Configuration()
    data_dir = Path(config.get("data_dir")) / CORPUS_ID / CORPUS_VERSION
    paths = data_dir.glob("data/*.krn")

    index = Index()
    meta_source = CSVSource(CORPUS_DIR / "src/additional-metadata.csv")
    flute_melody_ids = {
        'Flute_Melody_No_1': 141,
        'Flute_Melody_No_2': 142,
        'Flute_Melody_No_3': 143,
        'Flute_Melody_No_4': 144,
    }
    for path in paths:
        if path.stem not in flute_melody_ids:
            matches = re.match('No_+(\d+)', path.stem)
            song_num = matches[1]
        else:
            song_num = flute_melody_ids[path.stem]
        
        entry_id = f'menominee{song_num:0>3}'
        sources = dict(file=FileSource(path, root=data_dir), meta=meta_source)
        entry = DensmoreMenomineeEntry(entry_id, sources)
        index.add_entry(entry)
    index.export(CORPUS_DIR)


if __name__ == "__main__":
    generate_index()
