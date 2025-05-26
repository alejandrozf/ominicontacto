import contextlib
import dataclasses
import os
import sys
import time
import typing

import django.db
import pygments
import pygments.formatters
import pygments.lexers
import sqlparse


class QueryLogger:

    def __init__(self):
        self.queries = []

    def __call__(
        self,
        execute: typing.Callable[[str, typing.Any, bool, dict[str, typing.Any]], typing.Any],
        sql: str,
        params: typing.Any,
        many: bool,
        context: dict[str, typing.Any],
    ):
        if "FROM pg_type" in sql:
            return execute(sql, params, many, context)
        query = QueryRecord(sql, params, many)
        start = time.monotonic()
        try:
            results = execute(sql, params, many, context)
        except Exception as error:
            query.results = error
            raise
        else:
            query.results = results
            return results
        finally:
            query.duration = time.monotonic() - start
            self.queries.append(query)

    def __str__(self):
        return os.linesep.join(str(query) for query in self.queries)


@dataclasses.dataclass
class QueryRecord:

    class Request(typing.NamedTuple):
        sql: str
        params: typing.Any
        many: bool

    request: Request
    results: typing.Union[None, typing.Any, Exception] = None
    duration: typing.Optional[float] = None

    def __init__(self, sql: str, params: typing.Any, many: bool):
        self.request = self.Request(sql, params, many)

    def __str__(
        self,
        lexer=pygments.lexers.get_lexer_by_name("sql"),
        fmter=pygments.formatters.get_formatter_by_name("terminal16m", style="one-dark"),
    ):
        output = self.request.sql
        if self.request.params:
            output = output % tuple(
                repr(param) if isinstance(param, str) else param for param in self.request.params
            )
        output = sqlparse.format(
            output,
            keyword_case="upper",
            reindent_aligned=True,
            wrap_after=10,
        )
        output = pygments.highlight(
            output,
            lexer,
            fmter,
        )
        return output


@contextlib.contextmanager
def query_logger(outfile=sys.stdout):
    wrapper = QueryLogger()
    django.db.connection.execute_wrappers.append(wrapper)
    try:
        yield wrapper
    finally:
        django.db.connection.execute_wrappers.pop()
        if outfile:
            outfile.write(str(wrapper))
