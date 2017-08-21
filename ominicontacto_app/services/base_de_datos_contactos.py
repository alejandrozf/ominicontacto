# -*- coding: utf-8 -*-

"""
Servicio encargado de validar y crear las bases de datos.
"""

from __future__ import unicode_literals

from __builtin__ import callable, enumerate
import json
import logging
import pprint
import os
import re
from django.utils.encoding import smart_text

from ominicontacto_app.errors import OmlArchivoImportacionInvalidoError, \
    OmlError, OmlParserMaxRowError, OmlParserCsvImportacionError
from ominicontacto_app.models import BaseDatosContacto, \
    MetadataBaseDatosContactoDTO, Contacto
from ominicontacto_app.parser import ParserCsv, validate_telefono, validate_fechas, \
    validate_horas
from ominicontacto_app.utiles import elimina_tildes


logger = logging.getLogger(__name__)


class CreacionBaseDatosService(object):

    def genera_base_dato_contacto(self, base_datos_contacto):
        """
        Primer paso de la creación de una BaseDatoContacto.

        Este método se encarga de validar los datos para la creación del
        del objeto y llevar a cabo el guardado del mismo.

        Valida:
            Que el archivo subido para importar la base de datos de contactos
            sea y tenga las características válidas.
            Si el archivo es válido, hace el save del objeto y si no los es
            lanza la excepción correspondiente.
        """
        assert (base_datos_contacto.estado in
                (BaseDatosContacto.ESTADO_EN_DEFINICION,
                 BaseDatosContacto.ESTADO_DEFINIDA_ACTUALIZADA))

        csv_extensions = ['.csv']

        filename = base_datos_contacto.nombre_archivo_importacion
        extension = os.path.splitext(filename)[1].lower()
        if extension not in csv_extensions:
            logger.warn("La extensión %s no es CSV. ", extension)
            raise(OmlArchivoImportacionInvalidoError("El archivo especificado "
                  "para realizar la importación de contactos no es válido"))

        base_datos_contacto.save()

    def importa_contactos(self, base_datos_contacto):
        """
        Tercer paso de la creación de una BaseDatosContacto.
        Este método se encarga de generar los objectos Contacto por cada linea
        del archivo de importación especificado para la base de datos de
        contactos.
        """
        assert (base_datos_contacto.estado in
                (BaseDatosContacto.ESTADO_EN_DEFINICION,
                 BaseDatosContacto.ESTADO_DEFINIDA_ACTUALIZADA))

        metadata = base_datos_contacto.get_metadata()

        # FIXME: este metodo valida la consistencia de los metadatos, y
        #  lanza una excepcion ante cualquier problema. OJO! Esto no implica
        #  que los metadatos sean correctos y consistentes con los datos,
        #  pero al menos validan la consistencia "interna" de los metadatos
    #     metadata.validar_metadatos()

        # Antes que nada, borramos los contactos preexistentes
        #base_datos_contacto.elimina_contactos()

        parser = ParserCsv()

        try:
            estructura_archivo = parser.get_estructura_archivo(base_datos_contacto)
            encoding = parser.detectar_encoding_csv(estructura_archivo)
            cantidad_contactos = 0
            if base_datos_contacto.cantidad_contactos:
                cantidad_contactos = base_datos_contacto.cantidad_contactos
            for lista_dato in estructura_archivo[1:]:
                if len(lista_dato) > 2:
                    item = [value.decode(encoding) for value in lista_dato[1:]]
                    datos = json.dumps(item)
                else:
                    datos = ""
                cantidad_contactos += 1
                Contacto.objects.create(
                    telefono=lista_dato[0],
                    datos=datos,
                    bd_contacto=base_datos_contacto,
                )
        except OmlParserMaxRowError:
            base_datos_contacto.elimina_contactos()
            raise

        except OmlParserCsvImportacionError:
            base_datos_contacto.elimina_contactos()
            raise

        base_datos_contacto.cantidad_contactos = cantidad_contactos
        base_datos_contacto.save()

    def define_base_dato_contacto(self, base_datos_contacto):
        """
        Último paso de la creación de una BaseDatosContacto.

        Este método se encarga de marcar como definida y lista para su uso a
        la BaseDatosContacto.
        """
        base_datos_contacto.define()

    # def inferir_metadata(self, base_datos_contacto):
    #     """Devuelve instancia de MetadataBaseDatosContactoDTO que describe
    #     la metadata del archivo desde el cual se creará la BD.
    #
    #     :raises: NoSePuedeInferirMetadataError: si no se pudo inferir. Esto
    #              es algo grave, ya que si se lanza es porque no se encontro
    #              ninguna columan con datos que validen como telefono!
    #     """
    #     lineas = [
    #               ["Nombre", "Contacto", "Email"],
    #               ["juan", "549351444444", "juan@example.com"],
    #               ["juan", "549351444444", "juan@example.com"],
    #               ["juan", "549351444444", "juan@example.com"],
    #               ]
    #     service = PredictorMetadataService()
    #     return service.inferir_metadata_desde_lineas(lineas)

    def valida_contactos(self, base_datos_contacto):
        """
        Validacion para ver si existe en la base de datos el contacto
        """
        assert (base_datos_contacto.estado in
                (BaseDatosContacto.ESTADO_EN_DEFINICION,
                 BaseDatosContacto.ESTADO_DEFINIDA_ACTUALIZADA))

        parser = ParserCsv()

        try:
            estructura_archivo = parser.get_estructura_archivo(
                base_datos_contacto)
            cantidad_contactos = 0
            for lista_dato in estructura_archivo[1:]:
                if len(lista_dato) > 5:
                    datos = json.dumps(lista_dato[5:])
                else:
                    datos = ""
                cantidad_contactos += 1
                contacto = Contacto.objects.filter(
                   # id_cliente=int(lista_dato[1]),
                    bd_contacto=base_datos_contacto
                )
                if len(contacto) > 0:
                    raise (ContactoExistenteError("ya existe el contacto con el"
                                                  "  de id de cliente: {0}"
                                                  " la base de datos ".format(
                        int(lista_dato[1])))
                           )

        except OmlParserMaxRowError:
            base_datos_contacto.elimina_contactos()
            raise

        except OmlParserCsvImportacionError:
            base_datos_contacto.elimina_contactos()
            raise


class NoSePuedeInferirMetadataError(OmlError):
    """Indica que no se puede inferir los metadatos"""
    pass


class NoSePuedeInferirMetadataErrorEncabezado(OmlError):
    """Indica que no se puede inferir los metadatos"""
    pass


class ContactoExistenteError(OmlError):
    """este contacto con este id de cliente ya existe"""
    pass


DOUBLE_SPACES = re.compile(r' +')


class PredictorMetadataService(object):
    """
    Obtener/Adivinar/Predecir/Inferir cuál es la columna con el teléfono,
    fecha, hora.
    Generar la metadata que representara esto datos de la BDC.
    """

    def _inferir_columnas(self, lineas, func_validadora):
        assert callable(func_validadora)

        matriz = []
        for linea in lineas:
            matriz.append([
                           func_validadora(celda)
                           for celda in linea
                           ])

        # https://stackoverflow.com/questions/4937491/\
        #    matrix-transpose-in-python
        matriz_transpuesta = zip(*matriz)
        resultado_validacion_por_columna = [all(lista)
                                            for lista in matriz_transpuesta]

        return [index
                for index, value in enumerate(resultado_validacion_por_columna)
                if value]

    def sanear_nombre_de_columna(self, nombre):
        """Realiza saneamiento básico del nombre de la columna. Con basico
        se refiere a:
        - eliminar trailing spaces
        - pasar a mayusculas
        - reemplazar espacios por '_'
        - eliminar tildes

        Los caracteres invalidos NO son borrados.
        """
        nombre = smart_text(nombre)
        nombre = nombre.strip().upper()
        nombre = DOUBLE_SPACES.sub("_", nombre)
        nombre = elimina_tildes(nombre)
        return nombre

    def inferir_metadata_desde_lineas(self, lineas_unsafe, encoding):
        """Infiere los metadatos desde las lineas pasadas por parametros.

        Devuelve instancias de MetadataBaseDatosContactoDTO.
        """
        assert isinstance(lineas_unsafe, (list, tuple))

        lineas = []
        for linea in lineas_unsafe:
            lineas.append(
                [smart_text(col.decode(encoding)) for col in linea]
            )
        del lineas_unsafe

        logger.debug("inferir_metadata_desde_lineas(): %s", lineas)

        if len(lineas) < 2:
            logger.debug("Se deben proveer al menos 2 lineas: %s", lineas)
            raise(NoSePuedeInferirMetadataError("Se deben proveer al menos 2 "
                                                "lineas para poder inferir "
                                                "los metadatos"))

        # Primero chequeamos q' haya igual cant. de columnas
        set_cant_columnas = set([len(linea) for linea in lineas])
        if len(set_cant_columnas) != 1:
            logger.debug("Distintas cantidades "
                         "de columnas: %s", set_cant_columnas)
            raise(NoSePuedeInferirMetadataError("Las lineas recibidas "
                                                "poseen distintas cantidades "
                                                "de columnas"))

        primer_linea = lineas[0]
        otras_lineas = lineas[1:]
        metadata = MetadataBaseDatosContactoDTO()

        # Ahora chequeamos que haya al menos 1 columna
        if len(primer_linea) == 0:
            logger.debug("Las lineas no poseen ninguna "
                         "columna: %s", primer_linea)
            raise(NoSePuedeInferirMetadataError("Las lineas no poseen ninguna "
                                                "columna"))

        metadata.cantidad_de_columnas = len(primer_linea)

        # chequeamos que el nombre de la primera columna sea telefono
        if primer_linea[0] != 'telefono':
            raise (NoSePuedeInferirMetadataErrorEncabezado("El nombre de la primera "
                                                 "columna debe ser telefono"))



        # ======================================================================
        # Primero detectamos columnas de datos
        # ======================================================================

        columnas_con_telefonos = self._inferir_columnas(
            otras_lineas, validate_telefono)

        logger.debug("columnas_con_telefonos: %s", columnas_con_telefonos)

        columnas_con_fechas = self._inferir_columnas(
            otras_lineas, lambda x: validate_fechas([x]))

        logger.debug("columnas_con_fechas: %s", columnas_con_fechas)

        columnas_con_horas = self._inferir_columnas(
            otras_lineas, lambda x: validate_horas([x]))

        logger.debug("columnas_con_horas: %s", columnas_con_horas)

        columna_con_telefono = None
        if len(columnas_con_telefonos) == 0:
            logger.debug("No se encontro columna con telefono")

        else:
            # Se detecto 1 o mas columnas con telefono. Usamos la 1ra.
            logger.debug("Se detecto: columnas_con_telefonos: %s",
                         columnas_con_telefonos)

            if columnas_con_telefonos[0] in columnas_con_fechas:
                logger.warn("La columna con telefono tambien esta entre "
                            "las columnas detectadas como fecha")

            elif columnas_con_telefonos[0] in columnas_con_horas:
                logger.warn("La columna con telefono tambien esta entre "
                            "las columnas detectadas como hora")
            else:
                columna_con_telefono = columnas_con_telefonos[0]

        if columna_con_telefono is not None:
            metadata.columna_con_telefono = columna_con_telefono

        metadata.columnas_con_fecha = columnas_con_fechas
        metadata.columnas_con_hora = columnas_con_horas

        # Si no hemos inferido nada, salimos
        if columna_con_telefono is None:
            # En realidad, al menos el numero de columans debio ser
            # inferido. Pero si ni siquiera se detecto numero de
            # telefono, se debe a que (a) hay un bug en esta logica
            # (b) la BD es invalida. Asi que, de cualquire manera,
            # no creo q' valga la pena devolver la instancia de mentadata,
            # me parece mas significativo reportar el hecho de que
            # no se pudo inferir el metadato.
            raise(NoSePuedeInferirMetadataError("No se pudo inferir ningun "
                                                "tipo de dato"))

        #======================================================================
        # Si detectamos telefono, fecha u hora podemos verificar si la
        #  primer linea es encabezado o dato
        #======================================================================

        validaciones_primer_linea = []

        if columna_con_telefono is not None:
            validaciones_primer_linea.append(
                validate_telefono(primer_linea[columna_con_telefono]))

        for col_fecha in metadata.columnas_con_fecha:
            validaciones_primer_linea.append(
                validate_fechas([
                                 primer_linea[col_fecha]
                                 ]))

        for col_hora in metadata.columnas_con_hora:
            validaciones_primer_linea.append(
                validate_horas([
                                primer_linea[col_hora]
                                ]))

        assert validaciones_primer_linea
        logger.debug("validaciones_primer_linea: %s",
                     validaciones_primer_linea)

        primera_fila_es_dato = all(validaciones_primer_linea)
        metadata.primer_fila_es_encabezado = not primera_fila_es_dato

        nombres = []
        if metadata.primer_fila_es_encabezado:
            nombres_orig = [x.strip() for x in primer_linea]
            for num, nombre_columna in enumerate(nombres_orig):
                nombre_columna = self.sanear_nombre_de_columna(nombre_columna)

                # si no hay nombre, le asignamos un nombre generico
                if not nombre_columna:
                    nombre_columna = self.sanear_nombre_de_columna(
                        "COLUMNA_{0}".format(num + 1))

                # revisamos q' no se repita con los preexistentes
                while nombre_columna in nombres:
                    nombre_columna = self.sanear_nombre_de_columna(
                        nombre_columna + "_REPETIDO")

                nombres.append(nombre_columna)

        else:
            nombres = [
                self.sanear_nombre_de_columna("Columna {0}".format(num + 1))
                for num in range(metadata.cantidad_de_columnas)
            ]

        metadata.nombres_de_columnas = nombres

        return metadata

    def inferir_metadata_desde_lineas_base_existente(self, base_datos_contacto,
                                                     lineas_unsafe):
        """Infiere los metadatos desde las lineas pasadas por parametros.
            con base de datos exitente
        Devuelve instancias de MetadataBaseDatosContactoDTO.
        Copiado desde self.inferir_metadata_desde_lineas()
        """
        assert isinstance(lineas_unsafe, (list, tuple))

        lineas = []
        for linea in lineas_unsafe:
            lineas.append(
                [smart_text(col) for col in linea]
            )
        del lineas_unsafe

        logger.debug("inferir_metadata_desde_lineas(): %s", lineas)

        if len(lineas) < 2:
            logger.debug("Se deben proveer al menos 2 lineas: %s", lineas)
            raise(NoSePuedeInferirMetadataError("Se deben proveer al menos 2 "
                                                "lineas para poder inferir "
                                                "los metadatos"))

        # Primero chequeamos q' haya igual cant. de columnas
        set_cant_columnas = set([len(linea) for linea in lineas])
        if len(set_cant_columnas) != 1:
            logger.debug("Distintas cantidades "
                         "de columnas: %s", set_cant_columnas)
            raise(NoSePuedeInferirMetadataError("Las lineas recibidas "
                                                "poseen distintas cantidades "
                                                "de columnas"))

        primer_linea = lineas[0]
        otras_lineas = lineas[1:]
        metadata = base_datos_contacto.get_metadata()

        # Ahora chequeamos que haya al menos 1 columna
        if len(primer_linea) == 0:
            logger.debug("Las lineas no poseen ninguna "
                         "columna: %s", primer_linea)
            raise(NoSePuedeInferirMetadataError("Las lineas no poseen ninguna "
                                                "columna"))

        if metadata.cantidad_de_columnas != len(primer_linea):
            logger.debug("Distintas cantidades "
                         "de columnas: %s", set_cant_columnas)
            raise (NoSePuedeInferirMetadataError("Las lineas recibidas "
                                                 "poseen distintas cantidades "
                                                 "de columnas"))
        metadata.cantidad_de_columnas = len(primer_linea)

        # chequeamos que el nombre de las columnas sean los mismo cargado previamente
        for columna_base, columna_csv in zip(metadata.nombres_de_columnas, primer_linea):
            if columna_base != columna_csv:
                raise (NoSePuedeInferirMetadataErrorEncabezado("El nombre de la"
                       " columna {0} no coincide con el guardado en la base ".
                                                               format(columna_base)))


        # ======================================================================
        # Primero detectamos columnas de datos
        # ======================================================================

        columnas_con_telefonos = self._inferir_columnas(
            otras_lineas, validate_telefono)

        logger.debug("columnas_con_telefonos: %s", columnas_con_telefonos)

        columnas_con_fechas = self._inferir_columnas(
            otras_lineas, lambda x: validate_fechas([x]))

        logger.debug("columnas_con_fechas: %s", columnas_con_fechas)

        columnas_con_horas = self._inferir_columnas(
            otras_lineas, lambda x: validate_horas([x]))

        logger.debug("columnas_con_horas: %s", columnas_con_horas)

        columna_con_telefono = None
        if len(columnas_con_telefonos) == 0:
            logger.debug("No se encontro columna con telefono")

        else:
            # Se detecto 1 o mas columnas con telefono. Usamos la 1ra.
            logger.debug("Se detecto: columnas_con_telefonos: %s",
                         columnas_con_telefonos)

            if columnas_con_telefonos[0] in columnas_con_fechas:
                logger.warn("La columna con telefono tambien esta entre "
                            "las columnas detectadas como fecha")

            elif columnas_con_telefonos[0] in columnas_con_horas:
                logger.warn("La columna con telefono tambien esta entre "
                            "las columnas detectadas como hora")
            else:
                columna_con_telefono = columnas_con_telefonos[0]

        if columna_con_telefono is not None:
            metadata.columna_con_telefono = columna_con_telefono

        metadata.columnas_con_fecha = columnas_con_fechas
        metadata.columnas_con_hora = columnas_con_horas

        # Si no hemos inferido nada, salimos
        if columna_con_telefono is None:
            # En realidad, al menos el numero de columans debio ser
            # inferido. Pero si ni siquiera se detecto numero de
            # telefono, se debe a que (a) hay un bug en esta logica
            # (b) la BD es invalida. Asi que, de cualquire manera,
            # no creo q' valga la pena devolver la instancia de mentadata,
            # me parece mas significativo reportar el hecho de que
            # no se pudo inferir el metadato.
            raise(NoSePuedeInferirMetadataError("No se pudo inferir ningun "
                                                "tipo de dato"))

        #======================================================================
        # Si detectamos telefono, fecha u hora podemos verificar si la
        #  primer linea es encabezado o dato
        #======================================================================

        validaciones_primer_linea = []

        if columna_con_telefono is not None:
            validaciones_primer_linea.append(
                validate_telefono(primer_linea[columna_con_telefono]))

        for col_fecha in metadata.columnas_con_fecha:
            validaciones_primer_linea.append(
                validate_fechas([
                                 primer_linea[col_fecha]
                                 ]))

        for col_hora in metadata.columnas_con_hora:
            validaciones_primer_linea.append(
                validate_horas([
                                primer_linea[col_hora]
                                ]))

        assert validaciones_primer_linea
        logger.debug("validaciones_primer_linea: %s",
                     validaciones_primer_linea)

        primera_fila_es_dato = all(validaciones_primer_linea)
        metadata.primer_fila_es_encabezado = not primera_fila_es_dato

        nombres = []
        if metadata.primer_fila_es_encabezado:
            nombres_orig = [x.strip() for x in primer_linea]
            for num, nombre_columna in enumerate(nombres_orig):
                nombre_columna = self.sanear_nombre_de_columna(nombre_columna)

                # si no hay nombre, le asignamos un nombre generico
                if not nombre_columna:
                    nombre_columna = self.sanear_nombre_de_columna(
                        "COLUMNA_{0}".format(num + 1))

                # revisamos q' no se repita con los preexistentes
                while nombre_columna in nombres:
                    nombre_columna = self.sanear_nombre_de_columna(
                        nombre_columna + "_REPETIDO")

                nombres.append(nombre_columna)

        else:
            nombres = [
                self.sanear_nombre_de_columna("Columna {0}".format(num + 1))
                for num in range(metadata.cantidad_de_columnas)
            ]

        metadata.nombres_de_columnas = nombres

        return metadata

    def inferir_columnas_telefono(self, otras_lineas, encoding):
        lineas = []
        for linea in otras_lineas:
            lineas.append(
                [smart_text(col.decode(encoding)) for col in linea]
            )
        columnas_con_telefonos = self._inferir_columnas(
            lineas, validate_telefono)

        logger.debug("columnas_con_telefonos: %s", columnas_con_telefonos)
        return columnas_con_telefonos


class CreacionBaseDatosApiService(object):

    def crear_base_datos_api(self, nombre_base_datos):
        """
            Primer paso de la creación de una BaseDatoContacto via api.

            Crea la base de datos con el nombre pasado por parametro
            omitiendo archivo_importacion y nombre_archivo_importacion
            Retornado un objecto de BaseDatoContacto
            :return base_datos
        """
        base_datos = BaseDatosContacto(
            nombre=nombre_base_datos,
            archivo_importacion="-",
            nombre_archivo_importacion="-",
            estado=BaseDatosContacto.ESTADO_EN_DEFINICION
        )
        base_datos.save()
        return base_datos

    def _inferir_columnas(self, lineas, func_validadora):
        assert callable(func_validadora)

        matriz = []
        for linea in lineas:
            matriz.append([
                           func_validadora(celda)
                           for celda in linea
                           ])

        # https://stackoverflow.com/questions/4937491/\
        #    matrix-transpose-in-python
        matriz_transpuesta = zip(*matriz)
        resultado_validacion_por_columna = [all(lista)
                                            for lista in matriz_transpuesta]

        return [index
                for index, value in enumerate(resultado_validacion_por_columna)
                if value]

    def sanear_nombre_de_columna(self, nombre):
        """Realiza saneamiento básico del nombre de la columna. Con basico
        se refiere a:
        - eliminar trailing spaces
        - pasar a mayusculas
        - reemplazar espacios por '_'
        - eliminar tildes

        Los caracteres invalidos NO son borrados.
        """
        nombre = smart_text(nombre)
        nombre = nombre.strip().upper()
        nombre = DOUBLE_SPACES.sub("_", nombre)
        nombre = elimina_tildes(nombre)
        return nombre

    def inferir_metadata_desde_lineas(self, primer_linea, otras_lineas):
        """Infiere los metadatos desde las lineas pasadas por parametros.

        Devuelve instancias de MetadataBaseDatosContactoDTO.
        """
        #assert isinstance(lineas_unsafe, (list, tuple))



        # Primero chequeamos q' haya igual cant. de columnas
        cantidad_columnas = len(primer_linea)
        cantidad_contacto = len(otras_lineas[0])
        print cantidad_columnas
        print cantidad_contacto
        if cantidad_columnas != cantidad_contacto:
            logger.debug("Distintas cantidades "
                         "de columnas: %s", cantidad_columnas)
            raise(NoSePuedeInferirMetadataError("Las lineas recibidas "
                                                "poseen distintas cantidades "
                                                "de columnas"))


        metadata = MetadataBaseDatosContactoDTO()

        # Ahora chequeamos que haya al menos 1 columna
        if len(primer_linea) == 0:
            logger.debug("Las lineas no poseen ninguna "
                         "columna: %s", primer_linea)
            raise(NoSePuedeInferirMetadataError("Las lineas no poseen ninguna "
                                                "columna"))

        metadata.cantidad_de_columnas = len(primer_linea)

        # chequeamos que el nombre de la primera columna sea telefono
        if primer_linea[0] != 'telefono':
            raise (NoSePuedeInferirMetadataErrorEncabezado("El nombre de la primera "
                                                 "columna debe ser telefono"))



        # ======================================================================
        # Primero detectamos columnas de datos
        # ======================================================================

        columnas_con_telefonos = self._inferir_columnas(
            otras_lineas, validate_telefono)

        logger.debug("columnas_con_telefonos: %s", columnas_con_telefonos)

        columnas_con_fechas = self._inferir_columnas(
            otras_lineas, lambda x: validate_fechas([x]))

        logger.debug("columnas_con_fechas: %s", columnas_con_fechas)

        columnas_con_horas = self._inferir_columnas(
            otras_lineas, lambda x: validate_horas([x]))

        logger.debug("columnas_con_horas: %s", columnas_con_horas)

        columna_con_telefono = None
        if len(columnas_con_telefonos) == 0:
            logger.debug("No se encontro columna con telefono")

        else:
            # Se detecto 1 o mas columnas con telefono. Usamos la 1ra.
            logger.debug("Se detecto: columnas_con_telefonos: %s",
                         columnas_con_telefonos)

            if columnas_con_telefonos[0] in columnas_con_fechas:
                logger.warn("La columna con telefono tambien esta entre "
                            "las columnas detectadas como fecha")

            elif columnas_con_telefonos[0] in columnas_con_horas:
                logger.warn("La columna con telefono tambien esta entre "
                            "las columnas detectadas como hora")
            else:
                columna_con_telefono = columnas_con_telefonos[0]

        if columna_con_telefono is not None:
            metadata.columna_con_telefono = columna_con_telefono

        metadata.columnas_con_fecha = columnas_con_fechas
        metadata.columnas_con_hora = columnas_con_horas

        # Si no hemos inferido nada, salimos
        if columna_con_telefono is None:
            # En realidad, al menos el numero de columans debio ser
            # inferido. Pero si ni siquiera se detecto numero de
            # telefono, se debe a que (a) hay un bug en esta logica
            # (b) la BD es invalida. Asi que, de cualquire manera,
            # no creo q' valga la pena devolver la instancia de mentadata,
            # me parece mas significativo reportar el hecho de que
            # no se pudo inferir el metadato.
            raise(NoSePuedeInferirMetadataError("No se pudo inferir ningun "
                                                "tipo de dato"))

        #======================================================================
        # Si detectamos telefono, fecha u hora podemos verificar si la
        #  primer linea es encabezado o dato
        #======================================================================

        validaciones_primer_linea = []

        if columna_con_telefono is not None:
            validaciones_primer_linea.append(
                validate_telefono(primer_linea[columna_con_telefono]))

        for col_fecha in metadata.columnas_con_fecha:
            validaciones_primer_linea.append(
                validate_fechas([
                                 primer_linea[col_fecha]
                                 ]))

        for col_hora in metadata.columnas_con_hora:
            validaciones_primer_linea.append(
                validate_horas([
                                primer_linea[col_hora]
                                ]))

        assert validaciones_primer_linea
        logger.debug("validaciones_primer_linea: %s",
                     validaciones_primer_linea)

        primera_fila_es_dato = all(validaciones_primer_linea)
        metadata.primer_fila_es_encabezado = not primera_fila_es_dato

        nombres = []
        if metadata.primer_fila_es_encabezado:
            nombres_orig = [x.strip() for x in primer_linea]
            for num, nombre_columna in enumerate(nombres_orig):
                nombre_columna = self.sanear_nombre_de_columna(nombre_columna)

                # si no hay nombre, le asignamos un nombre generico
                if not nombre_columna:
                    nombre_columna = self.sanear_nombre_de_columna(
                        "COLUMNA_{0}".format(num + 1))

                # revisamos q' no se repita con los preexistentes
                while nombre_columna in nombres:
                    nombre_columna = self.sanear_nombre_de_columna(
                        nombre_columna + "_REPETIDO")

                nombres.append(nombre_columna)

        else:
            nombres = [
                self.sanear_nombre_de_columna("Columna {0}".format(num + 1))
                for num in range(metadata.cantidad_de_columnas)
            ]

        metadata.nombres_de_columnas = nombres

        return metadata

    def inferir_columnas_telefono(self, otras_lineas):
        lineas = []
        for linea in otras_lineas:
            lineas.append(
                [smart_text(col) for col in linea]
            )
        columnas_con_telefonos = self._inferir_columnas(
            lineas, validate_telefono)

        logger.debug("columnas_con_telefonos: %s", columnas_con_telefonos)
        return columnas_con_telefonos


class BaseDatosService(object):
    """Servicio de base de datos usado para eliminar contactos duplicados
       se podria eliminar este servicio ya que el filtro se está haciendo por la pk
       jamas habria una pk duplicada
    """

    def eliminar_contactos_duplicados(self, base_datos):

        contactos = Contacto.objects.filter(bd_contacto=base_datos)
        cantidad_contactos = base_datos.cantidad_contactos
        for contacto in contactos:
            if contactos.filter(pk=contacto.pk).count() > 1:
                contacto.delete()
                cantidad_contactos -= 1

        base_datos.cantidad_contactos = cantidad_contactos
        base_datos.save()
