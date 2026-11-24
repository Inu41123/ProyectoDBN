#!/bin/sh
set -eu
umask 077
FECHA=$(date +%Y%m%d_%H%M%S)
ARCHIVO="/backups/postgresql_${FECHA}.dump"
OBJETO="postgresql/postgresql_${FECHA}.dump"
trap 'rm -f "$ARCHIVO"' EXIT
export PGPASSWORD="$POSTGRES_PASSWORD"
pg_dump -h postgres -U "$POSTGRES_USER" \
  -d "$POSTGRES_DB" -Fc -f "$ARCHIVO"
test -s "$ARCHIVO"
pg_restore --list "$ARCHIVO" >/dev/null
aws --endpoint-url http://minio:9000 s3 cp "$ARCHIVO" \
  "s3://respaldosbd/$OBJETO"
SIZE=$(aws --endpoint-url http://minio:9000 s3api head-object \
  --bucket respaldosbd --key "$OBJETO" \
  --query ContentLength --output text)
[ "$SIZE" -gt 0 ]
echo "OK PostgreSQL: $OBJETO ($SIZE bytes)"
