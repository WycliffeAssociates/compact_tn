run:
	python3 main.py
	for FILE in *.md; do \
		echo "Converting $${FILE}..."; \
		pandoc \
			--metadata pagetitle=$${FILE} \
			--standalone \
			--css style.css \
			--output $${FILE}.html \
			$${FILE}; \
		wkhtmltopdf \
			--margin-left 0.5in \
			--margin-right 0.5in \
			--margin-top 0.5in \
			--margin-bottom 0.5in \
			$${FILE}.html $${FILE}.pdf; \
		done

run-dev:
	python3 main.py
	pandoc --standalone --css style.css --output 50-tit.md.html 50-tit.md
	wkhtmltopdf \
		--margin-left 0.5in \
		--margin-right 0.5in \
		--margin-top 0.5in \
		--margin-bottom 0.5in \
		50-tit.md.html 50-tit.md.pdf

lint:
	mypy --disallow-untyped-defs *.py
	pylint --output-format=colorized *.py

watch-lint:
	while inotifywait -e close_write,moved_to,create .; do clear; make lint; done

watch-run-dev:
	while inotifywait -e close_write,moved_to,create .; do clear; make run-dev 2>&1 | ccze -A; done

clean:
	rm -f *.md
	rm -f *.html
	rm -f *.pdf
