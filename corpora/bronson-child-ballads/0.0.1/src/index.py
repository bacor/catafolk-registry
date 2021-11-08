from pathlib import Path
from catafolk.configuration import Configuration
from catafolk.index import Index, IndexEntry
from catafolk.sources import FileSource
import re

CORPUS_ID = "bronson-child-ballads"
VERSION = "0.0.1"


class BronsonChildBalladsEntry(IndexEntry):

    source_names = ["file"]

    constants = dict(
        dataset_id=CORPUS_ID,
        corpus_version=VERSION,
        file_has_music=True,
        file_has_lyrics=False,
        publication_key="bronson1959child",
    )

    mappings = dict(
        file_path="file.cf_path",
        file_format="file.cf_format",
        file_checksum="file.cf_checksum",
        location="file.ARE",
        encoder="file.ENC",
        culture="file.CNT",
        collection_date="file.MRD",
        collectors="file.OCL",
        performers="file.MPN",
        genres="file.AGN",
        copyright="file.YEC",
    )

    def get_file_url(self):
        id = self.get("id")
        return f"https://kern.humdrum.org/cgi-bin/ksdata?file={id}.krn&l=osu/monophony/british&format=kern"

    def get_file_preview_url(self):
        id = self.get("id")
        return f"https://verovio.humdrum.org/?file=osu/monophony/british/{id}.krn"

    def get_publication_page_num(self):
        page_num = self.get("file.PPG")
        matches = re.match("p\\. (\\d+)", page_num)
        return matches[1]

    def get_title(self):
        onm = self.get("file.ONM")
        matches = re.match("((Child Ballad No\. (\d+), .+))", onm)
        return matches[1]

    def get_publication_song_num(self):
        onm = self.get("file.ONM")
        matches = re.match("((Child Ballad No\. (\d+), .+))", onm)
        return matches[3]


def generate_index():
    config = Configuration()
    data_dir = Path(config.get("data_dir")) / CORPUS_ID / VERSION
    corpus_dir = Path(__file__).parent.parent
    paths = data_dir.glob("data/*.krn")

    index = Index()
    for path in paths:
        entry_id = path.stem
        sources = dict(file=FileSource(path, root=data_dir))
        entry = BronsonChildBalladsEntry(entry_id, sources)
        index.add_entry(entry)
    index.export(corpus_dir)


if __name__ == "__main__":
    generate_index()
