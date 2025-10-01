FROM almalinux:9.6

# Repos + Python 3.11 (AppStream)
RUN dnf -y install epel-release dnf-plugins-core && \
    dnf -y module reset python && \
    dnf -y module enable python:3.11 && \
    dnf -y update

# MySQL 8.4 Community client (mysql, mysqldump)
RUN dnf -y install https://dev.mysql.com/get/mysql84-community-release-el9-1.noarch.rpm && \
    dnf -y config-manager --enable mysql-8.4-community && \
    dnf -y update

# Paquets
RUN dnf -y install \
      python3 python3-devel python3-pip \
      binutils glibc-devel \
      which openssh-clients \
      httpd mod_ssl \
      sshpass unoconv libreoffice-headless \
      logrotate \
      wkhtmltopdf \
      mysql-community-client \
  && dnf clean all

# permanent files (manuals, reports, logo ...)
COPY storage /storage

# copy some resource
COPY labbook_BE/alembic/resource /storage/resource
RUN mkdir -p /storage/resource/connect/analyzer/mapping \
             /storage/resource/connect/analyzer/plugin \
             /storage/resource/connect/analyzer/setting

# symlink resources to Apache docroot
RUN ln -s /storage/resource /var/www/html/

# bash aliases
RUN echo  "alias ls='ls --color=auto'" >> /root/.bashrc && \
    echo  "alias l.='ls -d .* --color=auto'" >> /root/.bashrc && \
    echo  "alias l='ls -CF'" >> /root/.bashrc && \
    echo  "alias la='ls -A'" >> /root/.bashrc && \
    echo  "alias ll='ls -alF'" >> /root/.bashrc

# Apache config
COPY etc/httpd/build/conf/httpd.conf /etc/httpd/conf/
COPY etc/httpd/build/conf.d/ssl.conf /etc/httpd/conf.d/

# supervisor + pipenv
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install supervisor pipenv
ENV PIPENV_VENV_IN_PROJECT=1 PIPENV_NOSPIN=1

# dirs
RUN mkdir -p /home/supervisor/log /home/supervisor/tmp \
             /home/apps/labbook_FE/labbook_FE \
             /home/apps/labbook_BE/labbook_BE

COPY supervisor/etc /home/supervisor/etc

# ===== FE =====
WORKDIR /home/apps/labbook_FE/labbook_FE
COPY labbook_FE/Pipfile ./
RUN /bin/bash -lc "python3 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install pipenv && pipenv install --deploy"
COPY labbook_FE /home/apps/labbook_FE/labbook_FE

# ===== BE =====
WORKDIR /home/apps/labbook_BE/labbook_BE
COPY labbook_BE/Pipfile ./
RUN /bin/bash -lc "python3 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install pipenv && pipenv install --deploy"
COPY labbook_BE /home/apps/labbook_BE/labbook_BE

# optional helper
RUN mkdir -p /home/apps/apache
COPY apache/apache.sh /home/apps/apache/

CMD ["supervisord",
     "-c", "/home/supervisor/etc/supervisor.conf",
     "--pidfile", "/home/supervisor/tmp/supervisor.pid",
     "--user", "root"]

