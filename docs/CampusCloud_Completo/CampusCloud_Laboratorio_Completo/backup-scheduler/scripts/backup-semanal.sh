#!/bin/sh
set -u
umask 077
LOCK=/backups/backup-semanal.lock
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "ERROR: respaldo en curso o bloqueo pendiente"
  exit 1
fi
trap 'rmdir "$LOCK"' EXIT
ERRORES=0
echo "INICIO: $(date '+%Y-%m-%d %H:%M:%S %Z')"
ejecutar() {
  NOMBRE="$1"; SCRIPT="$2"
  if /bin/sh "$SCRIPT"; then
    echo "CORRECTO: $NOMBRE"
  else
    echo "ERROR: $NOMBRE"
    ERRORES=$((ERRORES + 1))
  fi
}
ejecutar MySQL /scripts/backup-mysql.sh
ejecutar PostgreSQL /scripts/backup-postgres.sh
ejecutar MongoDB /scripts/backup-mongodb.sh
ejecutar SQLServer /scripts/backup-sqlserver.sh
echo "FIN: $(date '+%Y-%m-%d %H:%M:%S %Z'); errores=$ERRORES"
[ "$ERRORES" -eq 0 ]
