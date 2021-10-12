from pathlib import Path
from catafolk.configuration import Configuration
from catafolk.index import Index
from catafolk.corpora import EssenEntry
from catafolk.sources import FileSource

CORPUS_ID = "erk-deutscher-liederhort"
VERSION = "0.0.1"


class ErkDeutscherLiederhorstEntry(EssenEntry):

    constants = dict(
        dataset_id=CORPUS_ID,
        file_has_music=True,
        file_has_lyrics=False,
        file_has_license=False,
        collectors="Ludwig Erk",
        collection_date_earliest=1807,
        collection_date_latest=1883,
        culture="German",
        language="German",
        glottolog_id="stan1295",
        encoding_date="1982–1995",
        voice_use=True,
    )

    sct_pattern = "E0*((\\d+)(\\w+)?)"

    def get_file_url(self):
        id = self.get("id")
        return f"https://kern.humdrum.org/cgi-bin/ksdata?file={id}.krn&l=essen/europa/deutschl/erk&format=kern"

    def get_file_preview_url(self):
        id = self.get("id")
        return f"https://verovio.humdrum.org/?file=essen/europa/deutschl/erk/{id}.krn"

    def get_publication_key(self):
        tune_family_id = self.get("tune_family_id")
        if tune_family_id is None:
            return None

        if 0 <= int(tune_family_id) < 220:
            return "erk1893liederhort1"
        elif 220 <= int(tune_family_id) < 1060:
            return "erk1983liederhort2"
        else:
            return "erk1983liederhort3"


# Location
# —————————————————————————————————————————————————————————————————
# - replace:
#   - file.ARE
#   - location_1
#   - old: "Europa, Mitteleuropa, Deutschland; "
#     new: ""
# - replace:
#   - location_1
#   - location
#   - old: "Europa, Mitteleuropa, Deutschland, "
#     new: ""


def generate_index():
    config = Configuration()
    data_dir = Path(config.get("data_dir")) / CORPUS_ID / VERSION

    index = Index()
    paths = data_dir.glob("data/*.krn")
    for path in paths:
        entry_id = path.stem
        sources = dict(file=FileSource(path, root=data_dir, encoding="ISO-8859-1"))
        entry = ErkDeutscherLiederhorstEntry(entry_id, sources)
        index.add_entry(entry)

    corpus_dir = Path(__file__).parent.parent
    index.export_csv(corpus_dir / "index.csv")


if __name__ == "__main__":
    generate_index()
