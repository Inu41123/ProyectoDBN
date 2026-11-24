# RECONSTRUCCION DIDACTICA - NO ES COPIA DEL DOCKERFILE ORIGINAL PROBADO.
# Validar paquetes/repositorios antes de utilizar en clase.
FROM mysql:8.4
USER root
RUN microdnf install -y cronie python3 python3-pip curl ca-certificates tar gzip unzip findutils shadow-utils && microdnf clean all
# Cliente PostgreSQL 18 (repositorio PGDG para EL9)
RUN curl -fsSL -o /tmp/pgdg.rpm https://download.postgresql.org/pub/repos/yum/reporpms/EL-9-x86_64/pgdg-redhat-repo-latest.noarch.rpm \
 && rpm -Uvh /tmp/pgdg.rpm && microdnf install -y postgresql18 && microdnf clean all
# MongoDB Database Tools (repo oficial MongoDB 8.0 para RHEL 9)
RUN printf "[mongodb-org-8.0]\nname=MongoDB Repository\nbaseurl=https://repo.mongodb.org/yum/redhat/9/mongodb-org/8.0/x86_64/\ngpgcheck=0\nenabled=1\n" > /etc/yum.repos.d/mongodb-org-8.0.repo \
 && microdnf install -y mongodb-database-tools && microdnf clean all
# Microsoft SQLCMD 18; repo oficial RHEL9
RUN curl -fsSL https://packages.microsoft.com/config/rhel/9/prod.repo -o /etc/yum.repos.d/mssql-release.repo \
 && ACCEPT_EULA=Y microdnf install -y mssql-tools18 unixODBC && microdnf clean all
# AWS CLI v2, evita problemas de pip con repositorios y entornos gestionados
RUN curl -fsSL https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o /tmp/awscliv2.zip \
 && unzip -q /tmp/awscliv2.zip -d /tmp && /tmp/aws/install \
 && rm -rf /tmp/aws /tmp/awscliv2.zip /tmp/pgdg.rpm /tmp/mongodb-tools.rpm
RUN ln -snf /usr/share/zoneinfo/America/Mexico_City /etc/localtime
CMD ["crond", "-n"]
