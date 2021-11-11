from pathlib import Path
from typing import Union, List, Iterable
import re
import subprocess

from catafolk.utils import sort_versions

def iter_corpus_dir(
    corpora_dir: Union[str, Path] = "corpora",
    latest_only: bool = True,
    include_corpora: List[str] = [],
    exclude_corpora: List[str] = [],
) -> Iterable[Path]:
    """Iterate over all corpus directories. Either visit all corpora or only
    the latest versions

    Parameters
    ----------
    corpora_dir : Union[str, Path], optional
        The directory containing all corpora, by default 'corpora'
    latest_only : bool, optional
        If true yield only the latest version of each corpus, by default True
    include_corpora : List[str], optional
        A list of corpus_ids that are to be included. If this argument is
        specified, all corpora not in this list will be excluded.
    exclude_corpora : List[str], optional
        A list of corpus_ids that are excluded.

    Yields
    -------
    Path
        Path to a corpus directory
    """
    corpora_dir = Path(corpora_dir)
    for corpus_dir in corpora_dir.iterdir():
        if (
            not corpus_dir.is_dir()
            or corpus_dir.name in exclude_corpora
            or (len(include_corpora) > 0 and corpus_dir.name not in include_corpora)
        ):
            continue

        versions = {}
        for version_dir in corpus_dir.iterdir():
            if version_dir.is_dir() and re.match("\d+\.\d+\.\d+", version_dir.name):
                versions[version_dir.name] = version_dir

        if len(versions) == 0:
            continue
        elif latest_only:
            latest = sort_versions(list(versions.keys()))[-1]
            yield versions[latest]
        else:
            for version in versions.values():
                yield version


def generate_index(corpus_dir: Union[Path, str]) -> None:
    """Generate the index for a given corpus directory"""
    index_file = Path(corpus_dir) / "src" / "index.py"
    if index_file.exists():
        print("Running", index_file)
        subprocess.run(["python", index_file.resolve()])


def generate_indices(**kwargs) -> None:
    """Generate indices of all corpora. Optional keyword arguments are passed
    to iter_corpus_dir."""
    for corpus_dir in iter_corpus_dir("corpora", **kwargs):
        generate_index(corpus_dir)


if __name__ == "__main__":
    corpora = [
        # 'boehme-altdeutsches-liederbuch',
        # "boehme-volksthumliche-lieder",
        # "bronson-child-ballads",
        # 'creighton-nova-scotia',
        # 'densmore-choctaw',
        # 'densmore-maidu',
        # 'densmore-menominee',
        # 'densmore-nootka',
        # 'densmore-northern-ute',
        # 'densmore-papago',
        # 'densmore-pawnee'
        # 'densmore-pueblo'
        # 'densmore-teton-sioux'
        # 'erk-deutscher-liederhort'
        'essen-china-han'
    ]
    generate_indices(include_corpora=corpora)
