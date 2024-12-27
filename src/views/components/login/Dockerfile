FROM ubuntu:22.04
ENV ODOO_VERSION 16.0
ENV OPENEDUCAT_VERSION 16.0
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y     python3 python3-pip python3-dev python3-venv     postgresql-client     nodejs npm     git     wget     libxml2-dev libxslt1-dev     libjpeg-dev libfreetype6-dev     libpq-dev     build-essential     libldap2-dev libsasl2-dev     libssl-dev     libffi-dev     && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y iputils-ping postgresql-client
RUN mkdir -p /var/lib/apt/lists/partial && chmod 755 /var/lib/apt/lists/partial
RUN useradd -m -d /opt/odoo -U -r -s /bin/bash odoo
RUN git clone https://github.com/odoo/odoo.git --depth 1 --branch ${ODOO_VERSION} /opt/odoo/odoo
RUN git clone https://github.com/openeducat/openeducat_erp.git --depth 1 --branch ${OPENEDUCAT_VERSION} /opt/odoo/openeducat
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r /opt/odoo/odoo/requirements.txt
RUN pip3 install cryptography==3.4.7 pyopenssl==20.0.1 psycopg2-binary bs4 BeautifulSoup4 gitpython bech32 nostr
RUN cp -r /opt/odoo/openeducat/* /opt/odoo/odoo/addons/
COPY ./odoo.conf /etc/odoo/odoo.conf
COPY ./nostr_auth.py /opt/odoo/
COPY ./custom_odoo_server.py /opt/odoo/custom_odoo_server.py
COPY ./odoo_custom_addons /opt/odoo/custom_addons
RUN chown -R odoo:odoo /opt/odoo /etc/odoo
RUN chmod +x /opt/odoo/custom_odoo_server.py
USER root
EXPOSE 8069 8072
USER odoo
#ENTRYPOINT ["python3", "/opt/odoo/custom_odoo_server.py", "-c", "/etc/odoo/odoo.conf"]
ENTRYPOINT ["tail", "-f", "/dev/null"]
