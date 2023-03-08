#! /usr/bin/env python3

""" Create compact TN """


import glob
import json
import logging
import os
import pathlib
import re
import resource
import time

from typing import Dict, List
from typing_extensions import TypedDict

import yaml

# Types for mypy
BookInfo = TypedDict("BookInfo", { 'name': str, 'num': int, 'anth': str })
BookInfoDict = Dict[str, BookInfo]
Config = TypedDict("Config", {"tn_dir": str, "book_ids": List[str]})

# Constants
HEADER_1 = re.compile(r"(^|\n)# ", re.MULTILINE)
SEE_WORDS = ["See", "Ser", "Ver", "Vea", "Véase"]
SEE_PHRASE = re.compile(
    r"\(\s*(" + "|".join(SEE_WORDS) + r"):?[^)]*\)", re.IGNORECASE
)
MARKDOWN_LINK = re.compile(r"\(?\[([^]]*)\]\([^)]*\)\)?")


def main() -> None:
    """Main function"""

    # Set up logging
    logging_level = logging.DEBUG
    logging.basicConfig(
        format=(
	        # Timestamp
            "%(asctime)s "
            # DEBUG, INFO, etc.
            "%(levelname)s "
            # module/function:25:
            "%(module)s/%(funcName)s:%(lineno)d: "
            # Message
            "%(message)s"
        ),
        # Set minimum level (logging.WARNING if not given)
        level=logging.DEBUG,
    )

    # Load config
    with open("config.yaml", encoding="utf-8") as config_stream:
        config: Config = yaml.load(config_stream, Loader=yaml.SafeLoader)
    logging.debug("Config: %s", config)

    # Get output dir
    output_dir = os.getenv("COMPACT_TN_OUTPUT_DIR")
    if not output_dir:
        raise ValueError("Please set $COMPACT_TN_OUTPUT_DIR")
    logging.debug("Output dir: %s", output_dir)

    # Load Bible books
    with open("books.json", encoding="utf-8") as books_stream:
        books_info: BookInfoDict = json.load(books_stream)
    logging.debug("Loaded %d books.", len(books_info))

    # Track runtime
    start_time = time.time()
    base_mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    # Get to work
    process_tn(config["tn_dir"], config["book_ids"], output_dir, books_info)

    # Report on performance
    total_mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    logging.debug(
        "Done. Elapsed: %.2f s, obj: %.2f MB, script: %.2f MB",
        time.time() - start_time,
        (total_mem - base_mem) / 1000.0,
        total_mem / 1000.0,
    )


def process_tn(
        tn_dir: str,
        book_ids: List[str],
        output_dir: str,
        books_info: BookInfoDict) -> None:
    """Create compact TN"""

    # Read manifest
    with open(tn_dir + "/manifest.yaml", encoding="utf-8") as manifest_stream:
        manifest = yaml.load(manifest_stream, Loader=yaml.SafeLoader)
        books = manifest["projects"]

    # Process books
    for book in books:

        book_slug = book["identifier"]

        # Skip book if necessary
        if book_ids and book_slug not in book_ids:
            logging.info("Skipping %s, not in config", book_slug)
            continue

        # Get book info
        if book_slug not in books_info:
            raise ValueError(f"Book '{book_slug}' not found in books.json.")
        book_info = books_info[book_slug]

        # Process book
        output = process_book(book["title"], tn_dir + "/" + book["path"])

        # Write output
        filename = f"{output_dir}/{book_info['num']:02}-{book_slug}.md"
        with open(filename, "w", encoding="utf-8") as output_stream:
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
        contents = pathlib.Path(md_file).read_text(encoding="utf-8")
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
