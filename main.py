#! /usr/bin/env python3

""" Create compact TN """

from typing import List

import glob
import json
import logging
import os
import pathlib
import re
import resource
import time

import yaml

HEADER_1 = re.compile(r"(^|\n)# ", re.MULTILINE)
SEE_WORDS = ["See", "Ser", "Ver", "Vea", "Véase"]
SEE_PHRASE = re.compile(
    r"\(\s*(" + "|".join(SEE_WORDS) + "):?[^)]*\)", re.IGNORECASE
)
MARKDOWN_LINK = re.compile(r"\(?\[([^]]*)\]\([^)]*\)\)?")


def main() -> None:
    """Main function"""

    # Set up logging
    logging_level = logging.DEBUG
    logging.basicConfig(
        format="%(levelname)s: %(module)s/%(funcName)s:%(lineno)d: %(message)s",
        level=logging_level,
    )

    # Load config
    with open("config.yaml") as config_stream:
        config = yaml.load(config_stream, Loader=yaml.SafeLoader)
    logging.debug("Config: %s", config)

    # Load Bible books
    with open("books.json") as books_stream:
        books = json.load(books_stream)
    logging.debug("Books: %s", books)

    # Track runtime
    start_time = time.time()
    base_mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    # Get to work
    process_tn(config["tn_dir"], config["book_ids"])

    # Report on performance
    total_mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    logging.debug(
        "Done. Elapsed: %.2f s, obj: %.2f MB, script: %.2f MB",
        time.time() - start_time,
        (total_mem - base_mem) / 1000.0,
        total_mem / 1000.0,
    )


def process_tn(tn_dir: str, book_ids: List[str]) -> None:
    """Create compact TN"""

    # Read manifest
    with open(tn_dir + "/manifest.yaml") as manifest_stream:
        manifest = yaml.load(manifest_stream, Loader=yaml.SafeLoader)
        books = manifest["projects"]

    # Process books
    for book in books:

        book_slug = book["identifier"]
        book_sort = book["sort"]

        # Skip book if necessary
        if book_ids and book_slug not in book_ids:
            logging.info("Skipping %s, not in config", book_slug)
            continue

        # Process book
        output = process_book(book["title"], tn_dir + "/" + book["path"])

        # Write output
        filename = f"{book_sort:02}-{book_slug}.md"
        with open(filename, "w") as output_stream:
            logging.debug("Writing %s...", filename)
            output_stream.write(output)


def process_book(book_name: str, book_dir: str) -> str:
    """Process a book directory"""

    logging.debug("Processing %s in %s...", book_name, book_dir)

    # Abort on error
    if not os.path.isdir(book_dir):
        logging.error("Error: %s is not a directory.", book_dir)
        raise FileNotFoundError(book_dir)

    # Read files
    output = f"\n# {book_name}\n\n"
    verse_file_regex = re.compile(
        "^" + book_dir + r"/([0-9]+)/([0-9]+)\.md"
    )
    for md_file in sorted(
        glob.glob(book_dir + "/**/*.md", recursive=True)
    ):
        match = verse_file_regex.match(md_file)
        if not match:
            continue
        chapter_num = int(match[1])
        verse_num = int(match[2])
        contents = pathlib.Path(md_file).read_text()
        output += process_contents(chapter_num, verse_num, contents)
        # output += "<br/>\n\n"

    # Done
    return output


def process_contents(
    chapter_num: int, verse_num: int, contents: str
) -> str:
    """Process single verse file."""

    # Init
    output = ""

    # Add reference
    output += f"\n# {chapter_num}:{verse_num}\n"

    # Increment headers
    contents = HEADER_1.sub("\n## ", contents)

    # Remove references
    contents = SEE_PHRASE.sub("", contents)

    # Remove markdown links
    contents = MARKDOWN_LINK.sub("\\1", contents)

    # Add contents
    output += contents

    # Done
    return output


if __name__ == "__main__":
    main()
