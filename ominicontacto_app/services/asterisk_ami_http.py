# -*- coding: utf-8 -*-

"""Parser de XML que devuelve Asterisk"""

from __future__ import unicode_literals

import collections
import os
import re
import tempfile
from xml.parsers.expat import ExpatError

from django.conf import settings
from ominicontacto_app.errors import OmlError
import logging as _logging
import requests
import xml.etree.ElementTree as ET


logger = _logging.getLogger(__name__)


def get_response_on_first_element(root):
    """Returns attributes of tag 'generic' if an 'response' attribute
    exists in the first child of root.

    For example, for the folowing response
    # <ajax-response>
    # <response type='object' id='unknown'>
    #    <generic response='Error' message='Permission denied' />
    # </response>
    # </ajax-response>

    this method should return a dict with:

    { response:'Error', message='Permission denied'}

    Returns: a dict (if 'response' found) or `None`
    """
    elements = root.findall("./response/generic")
    if not elements:
        return None

    if 'response' in elements[0].attrib:
        return dict(elements[0].attrib)
    else:
        return None


#==============================================================================
# Parser of XML responses
#==============================================================================

class AsteriskXmlParser(object):
    """Base class for parsing various responses from Asterisk"""

    def __init__(self):
        """The root element of element-tree XML"""
        self.root = None

        """The dict with the attributes of the first elements
        The first element usually has response='Success' or
        response='Error' and a 'message'

        This dict is setted by _parse_and_check()
        """
        self.response_dict = None

        """The LOWERCASE value of the 'response' attribute, of the first
        element of the XML respones (taken from `self.response_dict`)

        This attribute is setted by _parse_and_check()
        """
        self.response_value = None

    def parse(self, xml):
        raise NotImplementedError()

    def _parse_and_check(self, xml, check_errors=True,
        exception_for_error=None,
        check_success=False):
        """Parses the XML string, and do basic checks.
        The root is saved on `self.root`.
        The response dict is saved on `self.response_dict`

        Parameters:

        - xml: the XML string
        - check_errors: if True (default) check if the response
          has been set as 'Error' (and raises exception)
        - check_success: if True, raises the exception if the
          response isn't a 'success'.

        Raises:
            - AsteriskHttpResponseWithError: if an error is detected
            - exception_for_error: if an error is detected
        """

        # https://docs.python.org/2.6/library/xml.etree.elementtree.html
        logger.debug("Iniciando parseo... XML:\n%s", xml)
        try:
            self.root = ET.fromstring(xml)
        except ExpatError as e:
            logger.exception("Error al parsear XML. "
                "ExpatError.code: {0.code}. XML:\n{1}".format(e, xml))
            raise
        logger.debug("Parseo finalizado")

        self.response_dict = get_response_on_first_element(self.root)
        exception_for_error = exception_for_error or\
            AsteriskHttpResponseWithError

        if self.response_dict:
            self.response_value = self.response_dict.get('response', '').\
                lower()

            if self.response_value == 'error':
                logger.info("_parse_and_check(): found 'response' == 'Error'. "
                    " response_dict: '%s' - XML:\n%s", str(self.response_dict),
                    xml)
                if check_errors:
                    raise exception_for_error()
            elif self.response_value == 'success':
                pass
            else:
                logger.warn("_parse_and_check(): unknown 'response'. "
                    "response_dict: '%s' - XML:\n%s", str(self.response_dict),
                    xml)

        # if check_success is True, check `response_value`
        # and raise exception in case of error
        if check_success and self.response_value != 'success':
            raise exception_for_error()


class AsteriskXmlParserForPing(AsteriskXmlParser):
    """Parses the XML returned by Asterisk when
    requesting `/mxml?action=ping`
    """

    def parse(self, xml):
        """Parses XML and returns `response_dict`
        Raises:
            - AsteriskHttpPingError: if ping failed
        """
        # <generic response='Success' ping='Pong'
        #    timestamp='1398544611.316607'/>

        self._parse_and_check(xml, check_success=True)
        if not self.response_dict.get('timestamp', ''):
            raise AsteriskHttpPingError("Attribute 'timestamp' "
                "not found in XML response")


class AsteriskXmlParserForLogin(AsteriskXmlParser):
    """Parses the XML returned by Asterisk when
    requesting `/mxml?action=login`
    """

    def parse(self, xml):
        """Parsea XML.
        Lanza `AsteriskHttpAuthenticationFailedError` si el login fallo.
        """
        # <ajax-response>
        #     <response type='object' id='unknown'>
        #        <generic response='Success'
        #            message='Authentication accepted' />
        #    </response>
        # </ajax-response>

        # <generic response="Error" message="Authentication failed"/>

        self._parse_and_check(xml,
            exception_for_error=AsteriskHttpAuthenticationFailedError,
            check_success=True)


class AsteriskXmlParserForOriginate(AsteriskXmlParser):
    """Parses the XML returned by Asterisk when
    requesting `/mxml?action=originate`
    """

    def parse(self, xml):
        """Parsea XML."""
        # Busy, noanswer, channel-unavailable:
        #  - <generic response='Error' message='Originate failed' />
        # Answer:
        #  - <generic response='Success'
        #        message='Originate successfully queued' />

        self._parse_and_check(xml,
            exception_for_error=AsteriskHttpOriginateError,
            check_success=True)


class AsteriskXmlParserForStatus(AsteriskXmlParser):
    """Parses the XML returned by Asterisk when
    requesting `/mxml?action=status`
    """

    def __init__(self):
        super(AsteriskXmlParserForStatus, self).__init__()
        self.calls_dicts = []

    def _element_is_respones_status(self, elem):
        # <generic>.attrib -> {
        #    'message': 'Channel status will follow',
        #    'response': 'Success'
        # }
        if elem.attrib.get('response', '') == 'Success' and \
            'message' in elem.attrib:
            return True
        return False

    def _element_is_event_status_complete(self, elem):
        # <generic event='StatusComplete' items='2' />
        if elem.attrib.get('event', '') == 'StatusComplete':
            return True
        return False

    def _element_is_call_status(self, elem):
        # <generic>.attrib -> {
        #    'event': 'Status',
        #    'privilege': 'Call',
        #
        #    'bridgedchannel': 'SIP/test_user1-00000002',
        #    'connectedlinenum': '<unknown>',
        #    'bridgeduniqueid': '1398522103.5',
        #    'uniqueid': '1398522103.4',
        #    'extension': '319751355727335',
        #    'accountcode': '',
        #    'channelstate': '6',
        #    'calleridnum': '<unknown>',
        #    'priority': '2',
        #    'seconds': '10',
        #    'connectedlinename': '<unknown>',
        #    'context': 'from_test_server',
        #    'calleridname': '<unknown>',
        #    'channel': 'IAX2/asterisk-d-1179',
        #    'channelstatedesc': 'Up'
        # }
        # <generic>.attrib -> {
        #    'event': 'Status',
        #    'privilege': 'Call',
        #
        #    'account': '',
        #    'bridgedchannel': 'IAX2/asterisk-d-1179',
        #    'bridgeduniqueid': '1398522103.4',
        #    'calleridname': '<unknown>',
        #    'calleridnum': '319751355727335',
        #    'channel': 'SIP/test_user1-00000002',
        #    'connectedlinename': '<unknown>',
        #    'connectedlinenum': '<unknown>',
        #    'state': 'Up',
        #    'uniqueid': '1398522103.5'
        # }

        if elem.attrib.get('event', '') == 'Status' and \
            elem.attrib.get('privilege', '') == 'Call':
            return True
        return False

    def _filter_generic_tags(self, elements):
        # response='Success' message='Channel status will follow'
        elem_respones_status = []

        # event='StatusComplete' items='0'
        elem_status_complete = []

        # event='Status' privilege='Call' channel='SIP/test_user1-00000002' ...
        elem_calls = []

        # otros elementos
        elem_unknown = []

        for elem in elements:
            if self._element_is_call_status(elem):
                elem_calls.append(elem)
            elif self._element_is_respones_status(elem):
                elem_respones_status.append(elem)
            elif self._element_is_event_status_complete(elem):
                elem_status_complete.append(elem)
            else:
                elem_unknown.append(elem)

        # TODO: chequear q' haya la cantidad correcta de elementos
        #  en las distintas listas

        assert len(elem_unknown) == 0
        assert len(elem_respones_status) == 1
        assert len(elem_status_complete) == 1

        status_complete_items = int(elem_status_complete[0].attrib.get(
            'items', '-1'))

        assert status_complete_items == len(elem_calls)

        for elem in elem_calls:
            a_dict = dict(elem.attrib)
            self.calls_dicts.append(a_dict)

    def parse(self, xml):
        """Parsea XML. Guarda resultado en `self.calls_dicts`
        """
        self._parse_and_check(xml)

        # ~~ Lo siguiente NO esta soportado en Python 2.6, asi q' no lo usamos
        # calls = root.findall("./response/generic[@privilege='Call']")

        try:
            self._filter_generic_tags(
                self.root.findall("./response/generic"))
        except AssertionError:
            logger.warn("AsteriskXmlParserForStatus.parser(): AssertionError. "
                "XML: %s", xml)
            raise


#==============================================================================
# Asterisk Http Ami Client
#==============================================================================

class AsteriskHttpClient(object):
    """Class to interact with Asterisk using it's http interface"""

    def __init__(self):
        self.session = requests.Session()
        self.session.trust_env = False

    def _request(self, url, params, timeout=5):
        """Make requests to the Asterisk.
        Parameters:
            - url
            - params: (dict) query parameters for the GET request
            - timeout: (int) timeout in seconds, > 0

        Returns tuple with:
            - response_body (contents returned by the server, ie: XML)
            - response object
        """
        # https://docs.python.org/2.6/library/httplib.html

        # Generamos URL para poder loguearla al principio
        assert url.startswith('/'), \
            "Url no comienza con /: {0}".format(url)
        assert type(timeout) == int, \
            "timeout no es entero: {0}".format(type(timeout))
        assert timeout > 0, \
            "Timeout must be GREATER than 0. Timeout: {0}".format(timeout)

        query_as_string = "&".join(["{0}={1}".format(k, v)
            for k, v in params.iteritems()])
        full_url = "{0}{1}".format(settings.ASTERISK['HTTP_AMI_URL'], url)
        logger.debug("AsteriskHttpClient: request a '%s?%s'",
            full_url, query_as_string)
        response = self.session.get(full_url, params=params, timeout=timeout)
        logger.debug("AsteriskHttpClient - Status: %s", response.status_code)
        logger.debug("AsteriskHttpClient - Got http response:\n%s",
            response.content)

        if settings.FTS_DUMP_HTTP_AMI_RESPONSES:
            prefix = "http-ami-respones-"
            try:
                tmp_fd, tmp_filename = tempfile.mkstemp(".xml",
                    prefix=prefix)
                tmp_file_obj = os.fdopen(tmp_fd, 'w')
                tmp_file_obj.write(response.content)
                logger.info("AsteriskHttpClient - Dump: %s", tmp_filename)
            except:
                logger.exception("No se pudo hacer dump de respuesta "
                    "a archivo")

        return response.content, response

    def login(self):
        response_body, _ = self._request("/mxml", {
            'action': 'login',
            'username': settings.ASTERISK['USERNAME'],
            'secret': settings.ASTERISK['PASSWORD'],
        })
        parser = AsteriskXmlParserForLogin()
        parser.parse(response_body)
        return parser

    def get_status(self):
        response_body, _ = self._request("/mxml", {
            'action': 'status',
        })

        parser = AsteriskXmlParserForStatus()
        parser.parse(response_body)
        return parser

    def ping(self):
        response_body, _ = self._request("/mxml", {
            'action': 'ping',
        })

        parser = AsteriskXmlParserForPing()
        parser.parse(response_body)
        return parser

    def originate(self, channel, context, es_aplication, variables_de_canal, async,
                  aplication=None, exten=None, priority=None, timeout=None):
        """
        Send an ORIGINATE action.
        Parameters:
            - channel, context, exten, priority: ORIGINATE parameters
            - timeout: (int) timeout of the originate action (in ms)
            - async: (bool)

        Returns:
            - the parser instance

        Raises:
            - AsteriskHttpOriginateError: if originate failed
        """
        #assert type(timeout) == int

        # FIXME: esto se hizo asi para detectar intentos de realizacion de
        #  originates con async=False. Una vez q' finalicemos la refactori-
        #  zacion, hay que eliminar el argumento de la funcoin, y todos estos
        #  asserts.
        assert type(async) == bool
        assert async

        request_timeout = 5
        logger.debug("AsteriskHttpClient.originate(): async=True - "
            "timeout: %s - request_timeout: %s", timeout, request_timeout)

        logger.info("originate(): channel: '%s' - context: '%s' "
            "- exten: '%s' - priority: '%s' - timeout: '%s'",
            channel, context, exten, priority, timeout)

        # variables: separadas por ',', con formato NOMBRE=VALOR
        # Asterisk 11 soporta HASTA 64 variables. Si hay mas de 64,
        #  todos los valores, desde la 64 hasta las ultimas, quedan
        #  guardados bajo el nombre de la variable 64
        #
        # DumpChan():
        #
        # Dumping Info For Channel: Local/11223344 (...)
        # ==============================================
        # Info:
        #
        # var1=x1
        #  (...)
        # var58=x58
        # var59=x59
        # var60=x60
        # var61=x61
        # var62=x62
        # var63=x63
        # var64=x64,var65=x65,var66=x66,var67=x67,(...)

        lista_de_variables = []
        for key, value in variables_de_canal.iteritems():
            lista_de_variables.append(key + "=" + value)
        print lista_de_variables
        print ",".join(lista_de_variables)
        response_body, _ = self._request("/mxml", {
            'action': 'originate',
            'channel': channel,
            'context': context,
            #'exten': exten,
            'application': aplication,
            #'priority': priority,
            #'timeout': timeout,
            'async': async,
            'variable': ",".join(lista_de_variables),
            #'variable': 'AGENTE=1003, AGENTNAME=federico peker',
        }, timeout=request_timeout)

        parser = AsteriskXmlParserForOriginate()
        parser.parse(response_body)
        return parser


#==============================================================================
# AmiStatusTracker
#==============================================================================

class AmiStatusTracker(object):

    REGEX = re.compile("^Local/([0-9]+)-([0-9]+)-([0-9]+)@"
        "FTS_local_campana_([0-9]+)")

    REGEX_NO_LOCAL_CHANNEL_CONTEXT = re.compile("^campania_([0-9]+)$")

    REGEX_NO_LOCAL_CHANNEL_EXTEN = re.compile(
        "^fts-([0-9]+)-([0-9]+)-([0-9]+)$")

    def __init__(self):
        pass

    def _parse(self, calls_dicts):
        """
        Devuelve:
        1. dict, cuyo key es un string, con 3 elementos, separados por
           espacios: [contacto_id, numero, campana_id], y el
           valor es la lista de registros asociados a este key
        2. lista, con registros no parseados
        """
        parseados = collections.defaultdict(lambda: list())
        no_parseados = []
        for item in calls_dicts:

            #
            # Chequeamos si 'channel' matchea
            #

            # Local/83723-03514761123-2@FTS_local_campana
            match_obj = AmiStatusTracker.REGEX.match(
                item.get("channel", ""))

            #
            # Si no matcheo, chequeamos 'bridgedchannel'
            #

            if not match_obj:
                match_obj = AmiStatusTracker.REGEX.match(
                    item.get("bridgedchannel", ""))

            if match_obj:
                contacto_id = match_obj.group(1)
                numero = match_obj.group(2)
                intento = match_obj.group(3)
                campana_id = match_obj.group(4)
                key = " ".join([contacto_id, numero, campana_id, intento])
                parseados[key].append(item)
                continue

            #
            # Si llegamos aca, es porque ni 'channel' ni 'bridgedchannel'
            #  tienen informacion. Por lo tanto, ahora chequeamos
            #
            # Ej:
            # {
            #    'context': 'campania_157',
            #    'extension': 'fts-2933998-1000000001-1',
            #    'calleridnum': '2933998-1000000001-1',
            #    'channel': 'IAX2/asterisk-a-1897',
            #    'channelstatedesc': 'Up'
            #    (...)
            # }

            # Primero intentamos con `campana_id`
            match_obj = AmiStatusTracker.REGEX_NO_LOCAL_CHANNEL_CONTEXT.\
                match(item.get("context", ""))

            if not match_obj:
                no_parseados.append(item)
                continue

            # Matcheo!
            campana_id = match_obj.group(1)

            # Ahora buscamos los demoas datos en `extension`
            match_obj = AmiStatusTracker.REGEX_NO_LOCAL_CHANNEL_EXTEN.\
                match(item.get("extension", ""))

            if not match_obj:
                no_parseados.append(item)
                continue

            # Matcheo!
            contacto_id = match_obj.group(1)
            numero = match_obj.group(2)
            intento = match_obj.group(3)

            # Tenemos todos los datos :-D
            key = " ".join([contacto_id, numero, campana_id, intento])
            parseados[key].append(item)
            continue

        return parseados, no_parseados

    def get_status_por_campana(self):
        """Devuelve diccionario, cuyos KEYs son los ID de campana,
        y VALUEs son listas. Cada lista es una lista con:
        [contacto_id, numero, campana_id, intentos]
        """

        logger.info("get_status_por_campana(): realizando request HTTP")
        # FIXME: crear cliente, loguear y reutilizar!
        client = AsteriskHttpClient()
        client.login()
        client.ping()
        calls_dicts = client.get_status().calls_dicts
        parseados, no_parseados = self._parse(calls_dicts)
        if no_parseados:
            logger.warn("get_status_por_campana(): %s registros de %s "
                "no fueron parseados", len(no_parseados),
                len(no_parseados) + len(parseados))

            # info(), porque son potenciales problemas... Y para quedarnos
            # tranquilos, tambien mostramos los que SI se parsearon...
            for item in no_parseados:
                logger.info("NO parseado: %s", item)

        campanas = collections.defaultdict(lambda: list())
        for key in parseados:
            contacto_id, numero, campana_id, intentos = key.split()
            campanas[int(campana_id)].append([
                int(contacto_id), numero, int(campana_id), int(intentos)
            ])

        if no_parseados:
            for campana_id, datos in campanas.iteritems():
                contactos = [x[0] for x in datos]
                logger.info("SI parseado - campana: %s - contactos: %s",
                    campana_id, contactos)

        return campanas


#==============================================================================
# Errors
#==============================================================================

class AsteriskHttpAmiError(OmlError):
    """Base class for exceptions related to the retrieval of information
    from Asterisk using http + xml
    """


class AsteriskHttpResponseWithError(AsteriskHttpAmiError):
    """The 'response' element (the first child, if has a 'response' attribute)
    was 'Error'.
    """


# class AsteriskHttpPermissionDeniedError(AsteriskHttpAmiError):
#    """The Asterisk Http interface returned 'permission denied'"""


class AsteriskHttpAuthenticationFailedError(AsteriskHttpAmiError):
    """The authentication failed"""


class AsteriskHttpPingError(AsteriskHttpAmiError):
    """The ping failed"""


class AsteriskHttpOriginateError(AsteriskHttpAmiError):
    """The originate command failed"""
