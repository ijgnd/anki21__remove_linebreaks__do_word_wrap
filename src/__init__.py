from .config import anki_point_version

if anki_point_version <= 49:
    from . import remove_linebreaks
else:
    from . import remove_linebreaks_50
