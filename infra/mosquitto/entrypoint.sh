#!/bin/sh
set -eu

: "${MQTT_EDGE_USERNAME:?MQTT_EDGE_USERNAME is required}"
: "${MQTT_EDGE_PASSWORD:?MQTT_EDGE_PASSWORD is required}"
: "${MQTT_BACKEND_USERNAME:?MQTT_BACKEND_USERNAME is required}"
: "${MQTT_BACKEND_PASSWORD:?MQTT_BACKEND_PASSWORD is required}"
: "${MQTT_STATION_CODES:=ESTACAO_01}"

auth_directory=/mosquitto/auth
password_file="${auth_directory}/passwords"
acl_file="${auth_directory}/acl"

umask 077
mkdir -p "${auth_directory}"
mosquitto_passwd -b -c "${password_file}" "$MQTT_EDGE_USERNAME" "$MQTT_EDGE_PASSWORD"
mosquitto_passwd -b "${password_file}" "$MQTT_BACKEND_USERNAME" "$MQTT_BACKEND_PASSWORD"

cat >"${acl_file}" <<EOF
user ${MQTT_EDGE_USERNAME}
EOF

for station_code in $(printf '%s' "${MQTT_STATION_CODES}" | tr ',' ' '); do
cat >>"${acl_file}" <<EOF
topic write vigi/estacoes/${station_code}/#
topic write vigi/dispositivos/${station_code}/status
topic read vigi/dispositivos/${station_code}/configuracao
EOF
done

cat >>"${acl_file}" <<EOF

user ${MQTT_BACKEND_USERNAME}
topic read vigi/estacoes/#
topic read vigi/dispositivos/#
topic read \$SYS/#
topic write vigi/dispositivos/+/configuracao
EOF

exec /docker-entrypoint.sh "$@"
