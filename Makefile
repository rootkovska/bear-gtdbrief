OUTPUTDIR = output
VPATH = $(OUTPUTDIR)
LATEXOPTS := -interaction batchmode \
						 -halt-on-error \
						 -no-shell-escape \
						 --output-directory $(OUTPUTDIR)

tex_files := $(wildcard $(OUTPUTDIR)/*.tex)
aux_files := $(wildcard $(OUTPUTDIR)/*.aux)

export LC_CTYPE = en_US.UTF-8

brief:
	./gtdbrief.py -v

tmpdir := $(shell mktemp -d)
tests:
	pytest-3 -o cache_dir=$(tmpdir) gtdclasses.py

pdfs: $(tex_files:tex=pdf)

%.pdf: %.tex
	@echo "Rendering PDF from $<"
	@pdflatex $(LATEXOPTS)  $< >/dev/null 2>/dev/null

clean:
	rm -f $(OUTPUTDIR)/*.aux && \
	rm -f $(OUTPUTDIR)/*.log

clean-all: clean
	rm -f $(OUTPUTDIR)/*
