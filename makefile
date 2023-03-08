.PHONY: run
run:
	# e.g. make run 2>&1 | ccze -A
	# Make sure output dir is set.
	test -n "$(COMPACT_TN_OUTPUT_DIR)" # $$COMPACT_TN_OUTPUT_DIR
	# Copy styles to output directory.
	cp style.css $${COMPACT_TN_OUTPUT_DIR}
	# Create md files
	python3 main.py
	# Convert md files to PDF
	for FILE in $${COMPACT_TN_OUTPUT_DIR}/*.md; do \
		echo "Converting $${FILE}..."; \
		pandoc \
			--standalone \
			--css style.css \
			--metadata pagetitle=$${FILE} \
			--output $${FILE}.html \
			$${FILE}; \
		wkhtmltopdf \
			--margin-left 0.5in \
			--margin-right 0.5in \
			--margin-top 0.5in \
			--margin-bottom 0.5in \
			--footer-center "$${FILE} - page [page] of [topage]" \
			--enable-local-file-access \
			$${FILE}.html \
			$${FILE}.pdf; \
	done

.PHONY: edit
edit:
	${EDITOR} README.md makefile config.yaml books.json style.css *.py

.PHONY: lint
lint:
	mypy --disallow-untyped-defs *.py
	pylint --output-format=colorized *.py

.PHONY: watch-lint
watch-lint:
	while inotifywait -e close_write,moved_to,create .; do sleep 1; clear; make lint; done

.PHONY: watch-run-dev
watch-run-dev:
	while inotifywait -e close_write,moved_to,create .; do sleep 1; clear; make run-dev 2>&1 | ccze -A; done
