FROM python:3.8.4  AS dependencies


RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    postgresql-client \
    locales \
    libsasl2-dev \
    libldap2-dev \
    libssl-dev \
    && curl -o wkhtmltox.deb -sSL https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.stretch_amd64.deb \
    && echo '7e35a63f9db14f93ec7feeb0fce76b30c08f2057 wkhtmltox.deb' | sha1sum -c - \
    && apt-get install -y --no-install-recommends ./wkhtmltox.deb \
    && rm -rf /var/lib/apt/lists/* wkhtmltox.deb \
    && sed -i -e 's/# fr_FR.UTF-8 UTF-8/fr_FR.UTF-8 UTF-8/' /etc/locale.gen \
    && locale-gen

COPY requirements.txt  ./

RUN pip install -U pip wheel \
    && pip install -r requirements.txt

FROM dependencies  AS dev

WORKDIR /usr/src/clocky/

COPY requirements.test.txt  ./

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    imagemagick \
    pdftk \
    ghostscript \
    && rm -rf /var/lib/apt/lists/*

ENV LANG fr_FR.UTF-8
ENV LANGUAGE fr_FR:fr
ENV LC_ALL fr_FR.UTF-8

RUN pip install -r requirements.test.txt

COPY . .

RUN pip install -e . \
    &&  python setup.py sdist bdist_wheel
