#!/bin/sh
set -eu
umask 077
FECHA=$(date +%Y%m%d_%H%M%S)
BD=${MSSQL_DATABASE:-tiendauttt}
ARCHIVO="/sqlserver-backups/${BD}_${FECHA}.bak"
OBJETO="sqlserver/${BD}_${FECHA}.bak"
# Ajustar MSSQL_BACKUP_PATH si el servidor monta el volumen
# compartido en una ruta diferente.
RUTA_SQL="${MSSQL_BACKUP_PATH:-/var/opt/mssql/backup}/${BD}_${FECHA}.bak"
SQLCMD=${SQLCMD_PATH:-/opt/mssql-tools18/bin/sqlcmd}
"$SQLCMD" -S sqlserver -U sa -P "$MSSQL_SA_PASSWORD" \
  -C -b -Q "BACKUP DATABASE [$BD] TO DISK = N'$RUTA_SQL' \
  WITH INIT, CHECKSUM, STATS = 10;"
"$SQLCMD" -S sqlserver -U sa -P "$MSSQL_SA_PASSWORD" \
  -C -b -Q "RESTORE VERIFYONLY FROM DISK = N'$RUTA_SQL' \
  WITH CHECKSUM;"
test -s "$ARCHIVO"
aws --endpoint-url http://minio:9000 s3 cp "$ARCHIVO" \
  "s3://respaldosbd/$OBJETO"
SIZE=$(aws --endpoint-url http://minio:9000 s3api head-object \
  --bucket respaldosbd --key "$OBJETO" \
  --query ContentLength --output text)
[ "$SIZE" -gt 0 ]
rm -f "$ARCHIVO"
echo "OK SQL Server: $OBJETO ($SIZE bytes)"
