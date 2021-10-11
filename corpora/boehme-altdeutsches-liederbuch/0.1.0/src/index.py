import re
from pathlib import Path
from catafolk.configuration import Configuration
from catafolk.index import IndexEntry, Index
from catafolk.sources import CSVSource, FileSource
import json
from catafolk.utils import is_iterable
import yaml
from catafolk.operations import map_values

with open(Path(__file__).parent / "genre-mapping.yml", "r") as stream:
    GENRE_MAPPING = yaml.safe_load(stream)


class BoehmeAltdeutschEntry(IndexEntry):

    source_names = ["file"]

    constants = dict(
        dataset_id="boehme-altdeutsches-liederbuch",
        file_has_music=True,
        file_has_lyrics=False,
        file_has_license=False,
        language="German",
        glottolog_id="stan1295",
        voice_use=True,
        publication_key="boehme1877altdeutsches",
    )

    mappings = dict(
        file_path="file.cf_path",
        file_format="file.cf_format",
        cf_checksum="file.cf_checksum",
        encoders="file.EED",
        copyright="file.YEM",
        version="file.EEV",
        title="file.OTL",
        metric_classification="file.AMT",
    )

    def get_comments(self):
        # Comments can be either strings or lists; we have to get them in one
        # flat list...
        comments = self.get("file._comments", [])
        if type(comments) == str:
            comments = [comments]
        onb = self.get("file.ONB")
        if type(onb) == str:
            comments += [onb]
        else:
            comments.extend(onb)
        return [c for c in comments if c is not None]

    def get_genres(self):
        agn = self.get("file.AGN")
        if agn is None:
            return []
        genres = [genre.strip() for genre in agn.split()]
        return map_values(*genres, mapping=GENRE_MAPPING, return_missing=False)

    def get_file_url(self):
        id = self.get("id")
        return f"https://kern.humdrum.org/cgi-bin/ksdata?file={id}&l=essen/europa/deutschl/altdeu1&format=kern"

    def get_file_preview_url(self):
        id = self.get("id")
        return (
            f"https://verovio.humdrum.org/?file=essen/europa/deutschl/altdeu1/{id}.krn"
        )

    def get_location(self):
        loc = self.get("file.ARE", "")
        return loc.replace("Europa, Mitteleuropa, Deutschland", "Germany")

    def get_instrumentation(self):
        ain = self.get("file.AIN")
        return ain.replace("vox", "voice")

    def get_catalogue_num(self):
        sct = self.get("file.SCT")
        matches = re.match("A0*((\\d+)(\\w+)?)", sct)
        return matches[0]

    def get_publication_song_num(self):
        sct = self.get("file.SCT")
        matches = re.match("A0*((\\d+)(\\w+)?)", sct)
        return matches[1].lower()

    def get_tune_family_id(self):
        sct = self.get("file.SCT")
        matches = re.match("A0*((\\d+)(\\w+)?)", sct)
        return matches[2]


def generate_index(data_dir):
    index = Index()
    paths = data_dir.glob("data/*.krn")
    for path in paths:
        entry_id = path.stem
        sources = dict(file=FileSource(path, root=data_dir))
        entry = BoehmeAltdeutschEntry(entry_id, sources)
        index.add_entry(entry)

    corpus_dir = Path(__file__).parent.parent
    index.export_csv(corpus_dir / "index.csv")


if __name__ == "__main__":
    config = Configuration()
    data_dir = Path(config.get("data_dir")) / "boehme-altdeutsches-liederbuch" / "0.1.0"
    generate_index(data_dir)
