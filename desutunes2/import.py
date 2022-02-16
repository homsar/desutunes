#!/usr/bin/env python

import logging
from pathlib import Path

from .processitunes import handleXML
from .processfile import getMetadataForFileList
from .metadata_to_records import add_records_from_metadata


def import_files(filenames: list[str]) -> None:
    records = []
    for filename in filenames:
        suffix = Path(filename).suffix.lower()
        if suffix in ['.xml', '.plist']:
            records.extend(handleXML(filename))
        else:
            records.extend(getMetadataForFileList([filename]))

    add_records_from_metadata(records)


def main() -> None:
    from argparse import ArgumentParser

    parser = ArgumentParser()

    parser.add_argument('filenames', metavar='filename', nargs='+')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    import_files(args.filenames)


if __name__ == '__main__':
    main()
