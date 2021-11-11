from pathlib import Path
from catafolk.configuration import Configuration
from catafolk.index import Index
from catafolk.corpora import EssenEntry
from catafolk.sources import FileSource
from catafolk.utils import load_corpus_metadata
import re

CORPUS_DIR = Path(__file__).parent.parent
CORPUS_METADATA = load_corpus_metadata(CORPUS_DIR / "corpus.yml")
CORPUS_VERSION = CORPUS_METADATA["version"]
CORPUS_ID = CORPUS_METADATA["dataset_id"]

class EssenHanEntry(EssenEntry):

    constants = dict(
        dataset_id=CORPUS_ID,
        corpus_version=CORPUS_VERSION,
        file_has_music=True,
        file_has_lyrics=False,
        file_has_license=False,
    )

    mappings = dict(
        location="file.ARE",
    )

    used_fields = [
        "file._comments",
        "file.ONB"
    ]

    def get_file_url(self):
        id = self.get("id")
        return f"https://verovio.humdrum.org/?file=essen/asia/china/han/{id}.krn"

    def get_file_preview_url(self):
        id = self.get("id")
        return f"https://verovio.humdrum.org/?file=essen/asia/china/han/{id}.krn"

    def get_culture(self):
        comments = self.get('file._comments')
        if comments is None: 
            return None
        elif type(comments) != list: 
            comments = [comments]

        for comment in comments:
            if comment.startswith('Ethnic Group: '):
                return comment.replace('Ethnic Group: ', '')

    def get_comments(self):
        comments = self.get('file._comments')
        if comments is None: 
            return None
        elif type(comments) != list:
            comments = [comments]
        
        comments = [c for c in comments if not c.startswith('Ethnic Group:')]
        nota_bene = self.get('file.onb')
        if type(nota_bene) == list:
            return comments + nota_bene
        elif type(nota_bene) == str:
            comments.append(nota_bene)
            return comments
        else:
            return comments

def generate_index():
    config = Configuration()
    data_dir = Path(config.get("data_dir")) / CORPUS_ID / CORPUS_VERSION

    index = Index()
    paths = data_dir.glob("data/*.krn")
    for path in list(paths)[:10]:
        entry_id = path.stem
        sources = dict(file=FileSource(path, root=data_dir, encoding="ISO-8859-1"))
        entry = EssenHanEntry(entry_id, sources)
        index.add_entry(entry)

    index.export(CORPUS_DIR)


if __name__ == "__main__":
    generate_index()
