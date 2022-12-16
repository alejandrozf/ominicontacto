import json
import time

import django.core.serializers.json
import sqlparse


class LoggingFormatter(object):
    """
    Python logging formatter intended to be used with records emitted by
    "django.db.backends" logger.
    Those records contains the following extra attributes:
    - duration
    - params
    - sql
    """

    def __init__(self, format="json"):
        self.format = getattr(self, "format_{}".format(format))

    def format_json(self, record):
        created = time.strftime(
            "%Y-%m-%dT%H:%M:%S",
            time.gmtime(record.created),
        )
        sql = " ".join(line.strip() for line in sqlparse.format(
            record.sql,
            keyword_case="upper",
        ).split())
        return json.dumps(
            {
                "created": created,
                "duration": record.duration,
                "sql": sql,
                "params": record.params,
            },
            cls=django.core.serializers.json.DjangoJSONEncoder,
            indent=2,
        )

    def format_text(self, record):
        return "created={}\n{}\nduration={:.3f}\nparams={}\n".format(
            time.strftime(
                "%Y-%m-%dT%H:%M:%S",
                time.gmtime(record.created),
            ),
            sqlparse.format(
                record.sql,
                keyword_case="upper",
                reindent_aligned=True,
            ),
            record.duration,
            record.params,
        )


class LoggingFilter(object):

    def __init__(self, duration=0):
        self.duration = duration

    def filter(self, record):
        # return getattr(record, "duration", -1) >= self.duration
        return record.duration >= self.duration
