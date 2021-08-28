#!/usr/bin/env python

from pathlib import Path

from .processitunes import handleXML
from .processfile import processFile
from .metadata_to_records import add_records_from_metadata


def import_files(filenames: list[str]) -> None:
    records = []
    for filename in filenames:
        suffix = Path(filename).suffix.lower()
        if suffix in ['.xml', '.plist']:
            records.extend(handleXML(filename))
        else:
            records.extend(processFile(filename))

    add_records_from_metadata(records)


def main() -> None:
    from argparse import ArgumentParser

    parser = ArgumentParser()

    parser.add_argument('filenames', metavar='filename', nargs='+')
    args = parser.parse_args()

    import_files(args.filenames)


if __name__ == '__main__':
    main()
