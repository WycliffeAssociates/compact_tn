.PHONY: run
run:
	python3 main.py
	for FILE in *.md; do \
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
			$${FILE}.html $${FILE}.pdf; \
	done

.PHONY: edit
edit:
	${EDITOR} README.md makefile config.yaml style.css *.py

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

.PHONY: clean
clean:
	rm -f *.md
	rm -f *.html
	rm -f *.pdf
