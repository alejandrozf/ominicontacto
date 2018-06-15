# -*- coding: utf-8 -*-

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
        exclude = ()


class RutaSalienteForm(forms.ModelForm):

    class Meta:
        model = RutaSaliente
        exclude = ()
        widgets = {
            "nombre": forms.TextInput(attrs={'class': 'form-control'}),
            "ring_time": forms.NumberInput(attrs={'class': 'form-control'}),
            "dial_options": forms.TextInput(attrs={'class': 'form-control'}),
        }


class OrdenTroncalBaseFormset(BaseInlineFormSet):

    def clean(self):
        """
        Realiza los validaciones relacionadas con los troncales asignados a una ruta saliente
        """
        if any(self.errors):
            return
        troncales = []
        ordenes = []
        deleted_forms = self.deleted_forms
        save_candidates_forms = set(self.forms) - set(deleted_forms)
        for form in save_candidates_forms:
            troncal = form.cleaned_data.get('troncal', None)
            orden = form.cleaned_data.get('orden', None)
            if troncal in troncales:
                raise forms.ValidationError(_("Los troncales deben ser distintos"), code="invalid")
            if orden in ordenes:
                raise forms.ValidationError(
                    _("El valor de orden no debe repetirse"), code="invalid")
            troncales.append(troncal)
            ordenes.append(orden)


PatronDeDiscadoFormset = inlineformset_factory(
    RutaSaliente, PatronDeDiscado, form=PatronDeDiscadoForm, can_delete=True, extra=0, min_num=1)

OrdenTroncalFormset = inlineformset_factory(
    RutaSaliente, OrdenTroncal, fields=('troncal', 'orden'), formset=OrdenTroncalBaseFormset,
    can_delete=True, extra=0, min_num=1)
