#!/bin/sh
set -eu
umask 077
FECHA=$(date +%Y%m%d_%H%M%S)
BD=${MYSQL_DATABASE:-campuscloud}
ARCHIVO="/backups/mysql_${FECHA}.sql"
OBJETO="mysql/mysql_${FECHA}.sql"
trap 'rm -f "$ARCHIVO"' EXIT
mysqldump -h mysql -u root -p"$MYSQL_ROOT_PASSWORD" \
  --single-transaction --quick --routines --triggers \
  --events --databases "$BD" > "$ARCHIVO"
test -s "$ARCHIVO"
aws --endpoint-url http://minio:9000 s3 cp "$ARCHIVO" \
  "s3://respaldosbd/$OBJETO"
SIZE=$(aws --endpoint-url http://minio:9000 s3api head-object \
  --bucket respaldosbd --key "$OBJETO" \
  --query ContentLength --output text)
[ "$SIZE" -gt 0 ]
echo "OK MySQL: $OBJETO ($SIZE bytes)"
