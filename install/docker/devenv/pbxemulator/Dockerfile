FROM alpine:latest
ENV LANG en_US.utf8

RUN apk update \
    && apk add vim sngrep asterisk openrc openntpd sipp
COPY conf/*.conf /etc/asterisk/
COPY interfaces /etc/network/
COPY audios/* /var/lib/asterisk/sounds/

EXPOSE 6060/udp 5060/udp 10000-10020/udp
ADD docker-entrypoint.sh /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
