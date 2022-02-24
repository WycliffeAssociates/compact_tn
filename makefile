.PHONY: run run-dev edit lint watch-lint watch-run-dev clean

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

run-dev:
	export FILE=40-mat.md \
	&& python3 main.py \
	&& pandoc \
		--standalone \
		--css style.css \
		--metadata pagetitle=$${FILE} \
		--output $${FILE}.html \
		$${FILE} \
	&& wkhtmltopdf \
		--margin-left 0.5in \
		--margin-right 0.5in \
		--margin-top 0.5in \
		--margin-bottom 0.5in \
		--footer-center "$${FILE} - page [page] of [topage]" \
		--enable-local-file-access \
		$${FILE}.html $${FILE}.pdf \
	&& xdg-open $${FILE}.pdf

edit:
	${EDITOR} main.py makefile config.yaml style.css books.json

lint:
	mypy --disallow-untyped-defs *.py
	pylint --output-format=colorized *.py

watch-lint:
	while inotifywait -e close_write,moved_to,create .; do sleep 1; clear; make lint; done

watch-run-dev:
	while inotifywait -e close_write,moved_to,create .; do sleep 1; clear; make run-dev 2>&1 | ccze -A; done

clean:
	rm -f *.md
	rm -f *.html
	rm -f *.pdf
