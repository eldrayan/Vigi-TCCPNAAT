FROM eclipse-mosquitto:2.0.22

COPY --chmod=755 entrypoint.sh /usr/local/bin/vigi-mosquitto-entrypoint

ENTRYPOINT ["/usr/local/bin/vigi-mosquitto-entrypoint"]
CMD ["/usr/sbin/mosquitto", "-c", "/mosquitto/config/mosquitto.conf"]
