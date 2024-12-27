FROM ubuntu:22.04
ENV ODOO_VERSION=16.0 \
    OPENEDUCAT_VERSION=16.0 \
    DEBIAN_FRONTEND=noninteractive \
    PATH=$PATH:/usr/local/bin

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    postgresql-client \
    nodejs \
    npm \
    git \
    wget \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    libfreetype6-dev \
    libpq-dev \
    build-essential \
    libldap2-dev \
    libsasl2-dev \
    libssl-dev \
    libffi-dev \
    iputils-ping \
    curl \
    netcat \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Create Odoo user and add to sudo group
RUN useradd -m -d /opt/odoo -U -r -s /bin/bash odoo && \
    usermod -aG sudo odoo && \
    echo "odoo ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Create necessary directories with correct permissions
RUN mkdir -p /var/run/postgresql && \
    chmod 777 /var/run/postgresql && \
    mkdir -p /etc/odoo \
    /opt/ivcs_repos \
    /var/lib/odoo \
    /var/log/odoo \
    /opt/odoo/.local/share/Odoo/filestore \
    /opt/odoo/.local/share/Odoo/sessions \
    /run/odoo && \
    chown -R odoo:odoo \
    /opt/odoo \
    /etc/odoo \
    /opt/ivcs_repos \
    /var/lib/odoo \
    /var/log/odoo \
    /run/odoo \
    /var/run/postgresql

# Clone Odoo and OpenEduCat as odoo user
USER odoo
RUN git clone https://github.com/odoo/odoo.git --depth 1 --branch ${ODOO_VERSION} /opt/odoo/odoo && \
    git clone https://github.com/openeducat/openeducat_erp.git --depth 1 --branch ${OPENEDUCAT_VERSION} /opt/odoo/openeducat

# Add passlib to the pip install command
RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir -r /opt/odoo/odoo/requirements.txt && \
    pip3 install cryptography pyopenssl==22.1.0 psycopg2-binary bs4 BeautifulSoup4 gitpython bech32 websocket-client websockets && \
    pip3 install nostr && \
    pip3 install python-gitlab && \
    pip3 install passlib

# Copy OpenEduCat addons
RUN cp -r /opt/odoo/openeducat/* /opt/odoo/odoo/addons/

# Copy custom files
COPY --chown=odoo:odoo ./nostr_auth.py /opt/odoo/
COPY --chown=odoo:odoo ./custom_odoo_server.py /opt/odoo/
COPY --chown=odoo:odoo ./odoo_custom_addons /opt/odoo/custom_addons
COPY --chown=odoo:odoo ./check_nostr_bridge.sh /opt/odoo/
COPY --chown=odoo:odoo ./docker-entrypoint.sh /opt/odoo/

COPY --chown=odoo:odoo fix_mail_setup.py /opt/odoo/

# Create wait-for-psql script
RUN echo '#!/bin/bash\n\
while ! PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "\q" 2>/dev/null; do\n\
    echo "Postgres is unavailable - sleeping"\n\
    sleep 1\n\
done\n\
echo "PostgreSQL is ready!"' > /opt/odoo/wait-for-psql.sh

# Set execute permissions
RUN chmod +x \
    /opt/odoo/check_nostr_bridge.sh \
    /opt/odoo/custom_odoo_server.py \
    /opt/odoo/wait-for-psql.sh \
    /opt/odoo/docker-entrypoint.sh

# Patch OpenSSL
USER root
RUN echo "from OpenSSL import crypto" > /tmp/patch_openssl.py && \
    echo "if not hasattr(crypto, 'X509_V_FLAG_EXPLICIT_POLICY'):" >> /tmp/patch_openssl.py && \
    echo "    crypto.X509_V_FLAG_EXPLICIT_POLICY = 0x8000" >> /tmp/patch_openssl.py && \
    echo "exec(open('/tmp/patch_openssl.py').read())" >> /opt/odoo/odoo/odoo/addons/base/models/ir_mail_server.py

USER odoo
WORKDIR /opt/odoo

VOLUME ["/var/lib/odoo", "/opt/odoo/odoo/addons", "/opt/odoo/custom_addons"]
EXPOSE 8069 8072

ENTRYPOINT ["/opt/odoo/docker-entrypoint.sh"]
CMD ["python3", "/opt/odoo/odoo/odoo-bin", "-c", "/etc/odoo/odoo.conf"]
