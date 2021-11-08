from pathlib import Path
from catafolk.configuration import Configuration
from catafolk.index import Index, IndexEntry
from catafolk.sources import FileSource
from catafolk.utils import load_corpus_metadata
import re

CORPUS_DIR = Path(__file__).parent.parent
CORPUS_METADATA = load_corpus_metadata(CORPUS_DIR / "corpus.yml")
CORPUS_VERSION = CORPUS_METADATA["version"]
CORPUS_ID = CORPUS_METADATA["dataset_id"]


class CreightonNovaScotiaEntry(IndexEntry):

    source_names = ["file"]

    constants = dict(
        dataset_id=CORPUS_ID,
        corpus_version=CORPUS_VERSION,
        file_has_music=True,
        file_has_lyrics=False,
        file_has_license=False,
        publication_key="creighton1932nova",
        publication_type="book",
        publication_title="Songs and Ballads from Nova Scotia",
        publication_authors="Helen Creighton",
        publidation_date=1932,
        latitude=45,
        longitude=-63,
        auto_geocoded=False,
        language="English",
        glottolog_id="atla1283",
        voice_use=True,
    )

    mappings = dict(
        file_path="file.cf_path",
        file_format="file.cf_format",
        file_checksum="file.cf_checksum",
        location="file.ARE",
        title="file.OTL",
        encoding_date="file.END",
        culture="file.CNT",
        collectors="file.OCL",
        scale="file.AMD",
        genres="file.AGN",
        comments="file.ONB",
        copyright="file.YEC",
        version="file.EEV",
        publication_page_num="file.PPG",
    )

    def get_other_fields(self):
        return dict(verses=self.get("file.verses"), VTS=self.get("file.VTS"))

    def get_file_url(self):
        id = self.get("id")
        return f"https://github.com/craigsapp/creighton-nova-scotia/blob/master/kern/{id}.krn"

    def get_file_preview_url(self):
        id = self.get("id")
        return f"https://verovio.humdrum.org/?file=users/craig/songs/creighton/nova/{id}.krn"

    def get_collection_date_earliest(self):
        mrd = self.get("file.MRD")
        matches = re.match("(\d+)///-(\d+)///", mrd)
        return matches[1]

    def get_collection_date_latest(self):
        mrd = self.get("file.MRD")
        matches = re.match("(\d+)///-(\d+)///", mrd)
        return matches[2]

    def get_encoders(self):
        encoders = [self.get(f"file.ENC{i}") for i in range(1, 5)]
        encoders = [e.strip() for e in encoders if e is not None]
        return encoders

    def get_performers(self):
        performers = self.get("file.mpn")
        if performers is not None:
            return performers.split(" and ")
        else:
            return None

    def get_publication_song_num(self):
        onm = self.get("file.ONM")
        matches = re.match("(\d+(\w)?)\.", onm)
        if matches:
            return matches[1]
        else:
            return None


def generate_index():
    config = Configuration()
    data_dir = Path(config.get("data_dir")) / CORPUS_ID / CORPUS_VERSION
    paths = data_dir.glob("data/kern/*.krn")

    index = Index()
    for path in paths:
        entry_id = path.stem
        sources = dict(file=FileSource(path, root=data_dir))
        entry = CreightonNovaScotiaEntry(entry_id, sources)
        index.add_entry(entry)
    index.export(CORPUS_DIR)


if __name__ == "__main__":
    generate_index()
