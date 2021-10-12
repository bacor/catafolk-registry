import yaml
from pathlib import Path
from catafolk.configuration import Configuration
from catafolk.index import Index, IndexEntry

# from catafolk.corpora import EssenEntry
from catafolk.sources import FileSource
from catafolk.operations import unescape_html, replace, map_values, extract_groups
from catafolk.corpora import ESSEN_GENRE_MAPPING

CORPUS_ID = "pinck-verklingende-weisen"
VERSION = "0.0.1"

with open(Path(__file__).parent / "scales-mapping.yml", "r") as stream:
    SCALES_MAPPING = yaml.safe_load(stream)


class PinckVerklingendeWeisenEntry(IndexEntry):

    source_names = ["file"]

    constants = dict(
        dataset_id=CORPUS_ID,
        file_has_music=True,
        file_has_lyrics=False,
        file_has_license=False,
        encoders="Damien Sagrillo",
    )

    mappings = dict(
        file_path="file.cf_path",
        file_format="file.cf_format",
        file_checksum="file.cf_checksum",
        location="file.reg",
    )

    _title_parts = None

    def get_file_url(self):
        id = self.get("id")
        return f"http://verovio.humdrum.org/?file=sagrillo/lorraine/{id}.krn"

    def get_file_preview_url(self):
        id = self.get("id")
        return f"https://kern.humdrum.org/cgi-bin/ksdata?file={id}.krn&l=users/sagrillo/lorraine&format=kern"

    def get_genres(self):
        fkt = unescape_html(self.get("file.fkt"))
        if fkt is None:
            return fkt
        fkt = replace(fkt, old="(yyy|\\?\\?\\??),? ?", new="")
        fkt = replace(fkt, old="\\?", new="")
        fkt = replace(fkt, old="/", new=",")
        genres = [g.strip() for g in fkt.split(",")]
        genres = map_values(genres, mapping=ESSEN_GENRE_MAPPING, return_missing=False)
        if genres is not None:
            genres = list(set([g for g in genres if not g is None]))
        return genres

    def get_other_fields(self):
        return {
            "minrhy": self.get("file.minrhy"),
            "meters": self.get("file.meters"),
            "rhy1": self.get("file.rhy1"),
            "rhy2": self.get("file.rhy2"),
            "key": self.get("file.key"),
            "kad": self.get("file.kad"),
            "akz": self.get("file.akz"),
            "fot": self.get("file.fot"),
            "for": self.get("file.for"),
            "fok": self.get("file.fok"),
            "n7k": self.get("file.n7k"),
        }

    def get_comments(self):
        return self.get("file._comments")

    def get_scale(self):
        mod = self.get("file.mod")
        scale, ambitus = extract_groups(
            mod, "([^\\]\\?]+) ?\\??\\] +AMBITUS\\[(\\w+)", [1, 2]
        )
        scale = scale.lower()
        return map_values(scale, mapping=SCALES_MAPPING, return_missing=True)

    def get_ambitus(self):
        mod = self.get("file.mod")
        scale, ambitus = extract_groups(
            mod, "([^\\]\\?]+) ?\\??\\] +AMBITUS\\[(\\w+)", [1, 2]
        )
        return ambitus

    def get_tonality(self):
        key = self.get("file.key")
        tonality, meters = extract_groups(
            key, "(\\w+) +(\\d+) +([\\w\\#]+) ([ \\w\/]+) ?\\] +ZZ\\[(\\d+)", [3, 4]
        )
        return tonality

    def get_meters(self):
        key = self.get("file.key")
        tonality, meters = extract_groups(
            key, "(\\w+) +(\\d+) +([\\w\\#]+) ([ \\w\/]+) ?\\] +ZZ\\[(\\d+)", [3, 4]
        )
        meters = meters.strip().replace("FREI", "free")
        return meters.split(" ")

    def get_publication_key(self):
        trd = self.get("file.trd")
        mapping = {
            "PINCK, Louis: Verklingende Weisen, Bd 1, Metz 1928": "pinck1926verklingende1",
            "PINCK, Louis: Verklingende Weisen, Bd 2, Metz 1928": "pinck1928verklingende2",
            "PINCK, Louis: Verklingende Weisen, Bd3, Metz 1933": "pinck1933verklingende3",
            "PINCK, Louis: Verklingende Weisen Bd 4, Kassel 1939": "pinck1939verklingende4",
        }
        return map_values(trd, mapping=mapping)

    def parse_title(self):
        if self._title_parts is None:
            parts = [self.get("file.cut"), self.get("file.cut1"), self.get("file.cut2")]
            title_raw = " ".join([p for p in parts if p is not None])
            title_html, song_num, page_num = extract_groups(
                title_raw,
                pattern=r"^(([^\\(]|(\(\?\)))+)(\(Band \d\))?(\(\d+-(\d+)\))?(,? S. ?(\d+))?",
                groups=[1, 6, 8],
            )
            title = unescape_html(title_html.strip())
            self._title_parts = dict(title=title, song_num=song_num, page_num=page_num)
        return self._title_parts

    def get_title(self):
        return self.parse_title()["title"]

    def get_publication_page_num(self):
        return self.parse_title()["page_num"]

    def get_publication_song_num(self):
        return self.parse_title()["song_num"]


corrections = {
    "p0566": {
        "title": "Der Fisch(?) Concelebrant",
        "publication_song_num": "4-5",
        "publication_page_num": "7",
    },
    "p1032": {
        "title": "Ach, Schatz, jetzt mu&szlig; ich wandern",
        "source_song_num": "3-59",
        "source_page_num": "170",
    },
    "p0573": {"publication_song_num": "4-12"},
    "p0574": {"title": "Ich wine wei&szlig;e Spinnerin"},
    "p0575": {"publication_song_num": "4-14", "publication_page_num": "19"},
    "p0580|p0577": {"publication_key": "pinck1939verklingende4"},
    "p0588": {
        "title": "Runckelstube",
        "publication_song_num": "4-27",
        "publication_page_num": "39",
    },
    "p0810": {"title": "Ich ging einmal spazieren", "publication_page_num": "113"},
    "p0965": {
        "title": "Spinn, Spinn",
        "publication_song_num": "2-94",
        "publication_page_num": "275",
    },
}


def generate_index():
    config = Configuration()
    data_dir = Path(config.get("data_dir")) / CORPUS_ID / VERSION
    corpus_dir = Path(__file__).parent.parent
    paths = data_dir.glob("data/*.krn")

    index = Index()
    for path in paths:
        entry_id = path.stem
        sources = dict(file=FileSource(path, root=data_dir, encoding="ISO-8859-1"))
        entry = PinckVerklingendeWeisenEntry(entry_id, sources)
        if entry_id in corrections:
            entry.corrections = corrections[entry_id]
        index.add_entry(entry)

    index.export_csv(corpus_dir / "index.csv")


if __name__ == "__main__":
    generate_index()
