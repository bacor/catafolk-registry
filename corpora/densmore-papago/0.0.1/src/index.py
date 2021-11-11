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


class DensmorePapagoEntry(IndexEntry):

    source_names = ["meta", "file"]
    default_source = "meta"

    constants = dict(
        dataset_id=CORPUS_ID,
        corpus_version=CORPUS_VERSION,
        file_has_music=True,
        file_has_lyrics=True,
        file_has_license=False,
        collectors="Frances Densmore",
        collection_date_earliest=1920,
        collection_date_latest=1921,
        culture="Tohono Oʼodham",
        culture_hraf_id="WNAI146",
        encoders=["Daniel Shanahan", "Eva Shanahan"],
        encoding_date="2014",
        copyright="Copyright 2014 Daniel and Eva Shanahan",
        auto_geocoded=False,
        language="Tohono O'odam",
        glottolog_id="toho1246",
        publication_key="densmore1929papago",
        publication_type="book",
        publication_authors="Frances Densmore",
        publication_title="Papago Music",
        publication_date=1929,
    )

    mappings = dict(
        file_path="file.cf_path",
        file_format="file.cf_format",
        file_checksum="file.cf_checksum",
        genres="file.SUPERFUNCTION",
        location="meta.location",
        latitude="meta.latitude",
        longitude="meta.longitude",
        # description="meta.analysis",
        # culture_dplace_id="meta.culture_dplace_id",
        # catalogue_num="meta.catalogue_num",
        tonality="meta.tonality",
        # tempo="meta.bpm",
        beat_duration="meta.beat_duration",
        meters="meta.meters",
        performers="meta.performers",
        performer_genders="meta.performer_genders",
        instrumentation="meta.instrumentation",
        instrument_use="meta.instrument_use",
        percussion_use="meta.percussion_use",
        voice_use="meta.voice_use",
        publication_page_num="meta.page_num",
        publication_song_num="meta.song_num",
        lyrics="meta.lyrics",
        lyrics_translation="meta.free_translation"
    )

    export_unused_fields = True
    used_fields = [
        "file.OTL",
        "file.PDT",
        # "file._comments",
        # "file.SUPERFUNCTION",
        # "meta.title",
        "meta.comments",
        "meta.catalogue_num"
        "meta.location",
        "meta.longitude",
        "meta.latitude"
    ]

    def get_file_url(self):
        fn = self.get("filename")
        return f"https://github.com/shanahdt/densmore/blob/master/Densmore/papago/{fn}.krn"

    def get_title(self):
        otl = self.get('file.OTL')
        matches = re.match('(No_+\d+_)?([^\.]+)(.krn)?', otl)
        if matches is not None:
            return matches[2].replace('_', ' ')
        else:
            return None

    def get_publication_preview_url(self):
        seq = self.get('publication_page_num') + 36
        return f"https://babel.hathitrust.org/cgi/pt?id=mdp.39015010760851&seq={seq}"
    
    def get_catalogue_num(self):
        num = self.get('meta.catalogue_num')
        return f'{num:.0f}'

    def get_comments(self):
        comments = [self.get("file._comments"), self.get("meta.comments")]
        comments = [c for c in comments if c is not None and c != ""]
        if len(comments) == 0:
            return None
        else:
            return comments
    
    def get_tempo(self):
        bpm = self.get('meta.bpm')
        return f'{bpm:.0f}'

def generate_index():
    config = Configuration()
    data_dir = Path(config.get("data_dir")) / CORPUS_ID / CORPUS_VERSION
    corpus_dir = Path(__file__).parent.parent
    index = Index()
    paths = data_dir.glob("data/*.krn")
    meta_source = CSVSource(corpus_dir / "src/additional-metadata.csv")
    special_song_nums = {
        "Flute_Melody_1": 168,
        "Flute_Melody_2": 169,
    }
    for path in paths:
        if path.stem not in special_song_nums:
            matches = re.match("No_+(\d+)", path.stem)
            song_num = matches[1]
        else:
            song_num = special_song_nums[path.stem]

        entry_id = f"papago{song_num:0>3}"
        sources = dict(file=FileSource(path, root=data_dir), meta=meta_source)
        entry = DensmorePapagoEntry(entry_id, sources)
        index.add_entry(entry)

    index.export(CORPUS_DIR)


if __name__ == "__main__":
    generate_index()
