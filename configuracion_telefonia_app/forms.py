# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.utils.translation import ugettext as _

from configuracion_telefonia_app.models import (PatronDeDiscado, RutaSaliente,
                                                TroncalSIP, OrdenTroncal)


class TroncalSIPForm(forms.ModelForm):

    class Meta:
        model = TroncalSIP
        exclude = ()
        widgets = {
            "nombre": forms.TextInput(attrs={'class': 'form-control'}),
            "canales_maximos": forms.NumberInput(attrs={'class': 'form-control'}),
            "caller_id": forms.TextInput(attrs={'class': 'form-control'}),
            "register_string": forms.TextInput(attrs={'class': 'form-control'}),
            "text_config": forms.Textarea(attrs={'class': 'form-control'}),
        }


class PatronDeDiscadoForm(forms.ModelForm):

    class Meta:
        model = PatronDeDiscado
        exclude = ('orden',)
        labels = {
            "match_pattern": _("Patrón de discado"),
            "prefix": _("Prefijo"),
        }


class RutaSalienteForm(forms.ModelForm):

    class Meta:
        model = RutaSaliente
        exclude = ()
        widgets = {
            "nombre": forms.TextInput(attrs={'class': 'form-control'}),
            "ring_time": forms.NumberInput(attrs={'class': 'form-control'}),
            "dial_options": forms.TextInput(attrs={'class': 'form-control'}),
        }


class PatronDeDiscadoBaseFormset(BaseInlineFormSet):

        def clean(self):
            """
            Realiza los validaciones relacionadas con los patrones de discado asignados a una ruta
            saliente
            """
            if any(self.errors):
                return
            deleted_forms = self.deleted_forms
            save_candidates_forms = set(self.forms) - set(deleted_forms)
            if len(save_candidates_forms) == 0:
                raise forms.ValidationError(
                    _("Debe ingresar al menos un patrón de discado"), code="invalid")

            patrones_discado = []
            for form in save_candidates_forms:
                patron_discado = form.cleaned_data.get('match_pattern', False)
                if patron_discado in patrones_discado:
                    raise forms.ValidationError(
                        _("Los patrones de discado deben ser diferentes"), code="invalid")
                patrones_discado.append(patron_discado)

        def save(self):
            """Salva el formset de los troncales actualizando el orden de acuerdo a los
            cambios realizados en la interfaz
            """
            if not self.instance.patrones_de_discado.exists():
                max_orden = 0
            else:
                max_orden = self.instance.patrones_de_discado.last().orden
            forms = self.forms
            for i, form in enumerate(forms, max_orden + 1):
                # asignamos nuevos ordenes a partir del máximo número de orden para
                # evitar clashes de integridad al salvar los formsets
                form.instance.orden = i
            super(PatronDeDiscadoBaseFormset, self).save()


class OrdenTroncalBaseFormset(BaseInlineFormSet):

    def clean(self):
        """Realiza los validaciones relacionadas con los troncales asignados a una ruta saliente
        """
        if any(self.errors):
            return

        deleted_forms = self.deleted_forms
        save_candidates_forms = set(self.forms) - set(deleted_forms)
        if len(save_candidates_forms) == 0:
            raise forms.ValidationError(
                _("Debe ingresar al menos un troncal"), code="invalid")

        troncales = []
        for form in save_candidates_forms:
            troncal = form.cleaned_data.get('troncal', None)
            if troncal in troncales:
                raise forms.ValidationError(_("Los troncales deben ser distintos"), code="invalid")
            troncales.append(troncal)

    def save(self):
        """Salva el formset de los troncales actualizando el orden de acuerdo a los
        cambios realizados en la interfaz
        """
        if not self.instance.secuencia_troncales.exists():
            max_orden = 0
        else:
            max_orden = self.instance.secuencia_troncales.last().orden
        forms = self.forms
        for i, form in enumerate(forms, max_orden + 1):
            # asignamos nuevos ordenes a partir del máximo número de orden para
            # evitar clashes de integridad al salvar los formsets
            form.instance.orden = i
        super(OrdenTroncalBaseFormset, self).save()


PatronDeDiscadoFormset = inlineformset_factory(
    RutaSaliente, PatronDeDiscado, form=PatronDeDiscadoForm,
    formset=PatronDeDiscadoBaseFormset, can_delete=True, extra=0, min_num=1)

OrdenTroncalFormset = inlineformset_factory(
    RutaSaliente, OrdenTroncal, fields=('troncal',), formset=OrdenTroncalBaseFormset,
    can_delete=True, extra=0, min_num=1)
