FROM postgres:9.6

RUN apt-get update
RUN apt-get -y install python postgresql-plpython-9.6

RUN  apt-get clean && \
     rm -rf /var/cache/apt/* /var/lib/apt/lists/*

COPY install_language.sh /docker-entrypoint-initdb.d

ENTRYPOINT ["/docker-entrypoint.sh"]

EXPOSE 5432
CMD ["postgres"]
