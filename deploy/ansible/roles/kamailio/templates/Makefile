#
# WARNING: do not run this directly, it should be run by the master Makefile

include ../../Makefile.defs
auto_gen=
NAME=db_postgres.so

# set CROSS_COMPILE to true if you want to skip
# the autodetection
# CROSS_COMPILE=true

ifeq ($(CROSS_COMPILE),)
#PGCFG=$(shell which pg_config)
{% if ansible_os_family == "RedHat" %}
PGCFG=/usr/pgsql-9.6/bin/pg_config
{% else %}
PGCFG=/usr/bin/pg_config
{% endif %}
endif

ifneq ($(PGCFG),)
	# use autodetection
	DEFS += -I$(shell $(PGCFG) --includedir)
	LIBS += -L$(shell $(PGCFG) --libdir) -lpq
#	LIBS += /usr/pgsql-9.6/include/libpq-fe.h
else
	# use standard know paths
	# libpq-fe.h locations
	DEFS +=-I$(LOCALBASE)/include -I$(LOCALBASE)/pgsql/include \
		-I$(SYSBASE)/include/pgsql -I$(SYSBASE)/include/postgresql \
		-I$(SYSBASE)/include/postgresql/8.0
	LIBS +=-L$(LOCALBASE)/lib -L$(LOCALBASE)/pgsql/lib \
		-L$(LOCALBASE)/lib/pgsql /usr/pgsql-9.6/include/libpq-fe.h -lpq
endif

#DEFS += -DPG_TEST
DEFS += -DSER_MOD_INTERFACE

SERLIBPATH=../../lib
SER_LIBS=$(SERLIBPATH)/srdb2/srdb2 $(SERLIBPATH)/srdb1/srdb1

include ../../Makefile.modules

ifeq ($(INSTALL_FLAVOUR),kamailio)
# extra install for kamailio

install-pgsql-scripts: $(bin_prefix)/$(bin_dir)
		PGSQLON=yes $(MAKE) -C ../../utils/kamctl/ install-modules

install-scripts: install-pgsql-scripts

endif # INSTALL_FLAVOUR
