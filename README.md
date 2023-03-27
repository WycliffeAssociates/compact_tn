# How to use

1. `git pull` source repo in e.g. .../en_tn_lite
2. `source default_env.sh` to set common env vars
3. Update config.yaml:
    - Set `tn_dir` to the directory where the tN repo is.
    - set `book_ids` to contain the books you want to convert, or empty for
      all books.
4. `make run`
5. This directory should now contain the `*.md.pdf` files.
