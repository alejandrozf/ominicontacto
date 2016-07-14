# -*- coding: utf-8 -*-

"""
Excepciones base del sistema.
"""

from __future__ import unicode_literals
from django.utils.encoding import force_text


class OmlError(Exception):
    """Excepcion base para FTS"""

    def __init__(self, message=None, cause=None):
        """Crea excepcion.
        Parametros:
            message: mensaje (opcional)
            cause: excepcion causa (opcional)
        """
        if message is None:
            super(OmlError, self).__init__()
        else:
            super(OmlError, self).__init__(message)

        self.cause = cause

        # chain_current_exception: (opcional) si es verdadero, toma
        #    el traceback actual `traceback.format_exc()` y lo guarda
        #    como texto para ser impreso en `__str__()`
        # if chain_current_exception:
        #    self.curr_exception_traceback = traceback.format_exc()
        # else:
        #    self.curr_exception_traceback = None

    def __str__(self):
        try:
            if self.cause is None:
                return super(OmlError, self).__str__()
            else:
                return "{0} (caused by {1}: {2})".format(
                    super(OmlError, self).__str__(),
                    type(self.cause),
                    str(self.cause),
                )
        except:
            return super(OmlError, self).__str__()


class OmlAudioConversionError(OmlError):
    """Error al intentar convertir audio"""
    pass


class OmlParserCsvImportacionError(OmlError):
    """
    Error en la importación de los datos del archivo csv.
    No valida alguno de los datos.

    :param fila: la fila del CSV que ha generado el problema. Esta fila puede
                 ser una fila ya convertida en unicode, o puede ser una fila
                 donde cada elemento es un string/byte sin convertir.
    """
    def __init__(self, numero_fila, numero_columna, fila, valor_celda, *args,
                 **kwargs):
        super(FtsParserCsvImportacionError, self).__init__(*args, **kwargs)
        self._numero_fila = numero_fila
        self._numero_columna = numero_columna

        # Transformamos en unicode, ignorando errores ('replace')
        fila_unicode = [force_text(item, errors='ignore') for item in fila]
        self._fila = u', '.join(fila_unicode)

        # Transformamos en unicode, ignorando errores ('replace')
        self._valor_celda = force_text(valor_celda, errors='ignore')

    @property
    def numero_fila(self):
        return self._numero_fila

    @property
    def numero_columna(self):
        return self._numero_columna

    @property
    def fila(self):
        return self._fila

    @property
    def valor_celda(self):
        return self._valor_celda

    def __str__(self):
        return (u"Fila con problema: '{0}'. "
                "Celda: '{1}'").format(self._fila,
                                       self._valor_celda)


class OmlParserCsvDelimiterError(OmlError):
    """
    Error al intentar determinar el delimitador en
    el ParserCsv.
    """
    pass


class OmlParserMinRowError(OmlError):
    """
    El archivo querido Parsear tiene menos de 3 filas.
    """
    pass


class OmlParserMaxRowError(OmlError):
    """
    El archivo querido Parsear tiene mas filas de las permitidas.
    """
    pass


class OmlParserOpenFileError(OmlError):
    """
    No se pudo abrir el archivo a Parsear
    """
    pass


class OmlRecicladoBaseDatosContactoError(OmlError):
    """
    No se pudo obtener la base de datos en el reciclado de la campana.
    """
    pass


class OmlRecicladoCampanaError(OmlError):
    """
    No se pudo generar el reciclado de la campana.
    """
    pass


class OmlDepuraBaseDatoContactoError(OmlError):
    """
    No se pudo depurar la base datos de contactos.
    """
    pass


class OmlArchivoImportacionInvalidoError(OmlError):
    """
    El archivo para realizar la importación de Contactos no es válido.
    """
    pass


class OMLOptimisticLockingError(OmlError):
    """Se intentó actualizar un objeto modificado por otro thread/proceso"""
    pass
