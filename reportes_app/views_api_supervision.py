# -*- coding: utf-8 -*-

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count

from django.views.generic import View
from django.http import JsonResponse

from ominicontacto_app.utiles import datetime_hora_minima_dia
from ominicontacto_app.models import Campana, CalificacionCliente
from reportes_app.reporte_llamadas import ReporteTipoDeLlamadasDeCampana


@method_decorator(csrf_exempt, name='dispatch')
class LlamadasDeCampanaView(View):
    """
    Devuelve un JSON con cantidades de tipos de llamadas de la campaña para el dia de la fecha
    """
    TIPOS = {
        "t_abandono": _(u'Tiempo de Abandono(prom.)'),
        "atendidas": _(u'Llamadas Atendidas'),
        "abandonadas": _(u'Llamadas Abandonadas'),
        "expiradas": _(u'Llamadas Expiradas'),
        "recibidas": _(u'Llamadas Recibidas'),
        "t_espera_conexion": _(u'Tiempo de Espera de Conexión(prom.)'),
        't_espera_atencion': _(u'Tiempo de Espera de Atención(prom.)'),
        "efectuadas_manuales": _(u'Llamadas Efectuadas Manuales'),
        "conectadas_manuales": _(u'Llamadas Conectadas Manuales'),
        "no_conectadas_manuales": _(u'Llamadas No Conectadas Manuales'),
        "t_espera_conexion_manuales": _(u'Tiempo de Espera de Conexión Manuales(prom.)'),
        'conectadas': _(u'Llamadas Conectadas'),
        'efectuadas': _(u'Llamadas Efectuadas'),
        'no_conectadas': _(u'Llamadas No Conectadas'),
    }

    def get(self, request, pk_campana):
        hoy_ahora = now()
        hoy_inicio = datetime_hora_minima_dia(hoy_ahora)
        try:
            reporte = ReporteTipoDeLlamadasDeCampana(hoy_inicio, hoy_ahora, pk_campana)
            reporte.estadisticas.pop('nombre')
            data = {'status': 'OK'}
            for nombre_campo, value in reporte.estadisticas.iteritems():
                data[self.TIPOS[nombre_campo]] = value

        except ObjectDoesNotExist:
            data = {'status': 'Error', 'error_message': _(u'No existe la campaña')}

        return JsonResponse(data=data)


class CalificacionesDeCampanaView(View):
    """
    Devuelve un JSON con cantidades de cada tipo de calificación de una campaña del dia de la fecha
    """
    def get(self, request, pk_campana):

        try:
            campana = Campana.objects.get(id=pk_campana)
        except Campana.DoesNotExist:
            return JsonResponse(data={'status': 'Error',
                                      'error_message': _(u'No existe la campaña')})

        data = {'status': 'OK'}
        for opcion in campana.opciones_calificacion.all():
            data[opcion.nombre] = 0
        calificaciones = CalificacionCliente.objects.filter(
            fecha__gt=datetime_hora_minima_dia(now()),
            opcion_calificacion__campana_id=pk_campana)
        cantidades = calificaciones.values('opcion_calificacion__nombre').annotate(
            cantidad=Count('opcion_calificacion__nombre'))

        for opcion in cantidades:
            data[opcion['opcion_calificacion__nombre']] = opcion['cantidad']

        return JsonResponse(data=data)
