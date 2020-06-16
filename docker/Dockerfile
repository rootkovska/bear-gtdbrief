FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update -qqy 

# disable exclusion of man pages
RUN sed -i '/path-exclude=\/usr\/share\/man\/*/c\#path-exclude=\/usr\/share\/man\/*' /etc/dpkg/dpkg.cfg.d/excludes
RUN apt-get install -qqy man manpages locales-all > /dev/null
RUN apt --reinstall install -qqy man-db coreutils > /dev/null

RUN apt-get install -qqy \
    fish tree vim less \
    curl wget netcat rsync \
    sudo > /dev/null

RUN apt-get install -qqy \
    git make \
    imagemagick \
    pandoc pandoc-citeproc \
    poppler-utils qpdf \
    texlive-latex-recommended texlive-fonts-recommended texlive-latex-extra \
    jp2a figlet \
    > /dev/null

RUN apt-get install -qqy \
    python3-pygraphviz \
    python3-networkx \
    python3-pygraphviz \
    python3-matplotlib \
    python3-blessings python3-colorama \
    python3-pypdf2 \
    python3-tqdm \
    python3-jinja2 \
    python3-pytest \
    dot2tex \
    > /dev/null

RUN (echo y; echo Y) | unminimize
ADD init.sh /
RUN chmod +x /init.sh

RUN useradd -s /usr/bin/fish -m user

CMD ["/init.sh"]
