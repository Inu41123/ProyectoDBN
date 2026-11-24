#!/bin/sh
set -eu
umask 077
FECHA=$(date +%Y%m%d_%H%M%S)
ARCHIVO="/backups/mongodb_${FECHA}.archive.gz"
OBJETO="mongodb/mongodb_${FECHA}.archive.gz"
trap 'rm -f "$ARCHIVO"' EXIT
mongodump --host mongodb --port 27017 \
  --username "$MONGO_INITDB_ROOT_USERNAME" \
  --password "$MONGO_INITDB_ROOT_PASSWORD" \
  --authenticationDatabase admin --archive="$ARCHIVO" --gzip
test -s "$ARCHIVO"
aws --endpoint-url http://minio:9000 s3 cp "$ARCHIVO" \
  "s3://respaldosbd/$OBJETO"
SIZE=$(aws --endpoint-url http://minio:9000 s3api head-object \
  --bucket respaldosbd --key "$OBJETO" \
  --query ContentLength --output text)
[ "$SIZE" -gt 0 ]
echo "OK MongoDB: $OBJETO ($SIZE bytes)"
