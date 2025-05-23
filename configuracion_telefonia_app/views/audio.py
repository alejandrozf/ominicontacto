# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3, as published by
# the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

from __future__ import unicode_literals

import logging
import os

from django.urls import reverse
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, ListView, CreateView, DeleteView
from api_app.services.storage_service import StorageService

from configuracion_telefonia_app.forms import AudiosAsteriskForm, PlaylistForm, MusicaDeEsperaForm
from configuracion_telefonia_app.models import MusicaDeEspera, Playlist
from configuracion_telefonia_app.services.audio_asterisk import AsteriskSoundsInstaller

from ominicontacto_app.services.asterisk.playlist import PlaylistDirectoryManager
from ominicontacto_app.views_archivo_de_audio import ArchivoDeAudioMixin
from ominicontacto_app.asterisk_config import AudioConfigFile, PlaylistsConfigCreator

from utiles_globales import obtener_paginas

logger = logging.getLogger(__name__)


class AdicionarAudioAsteriskView(FormView):
    """Vista que adiciona dinámicamente audios de asterisk (desde el sitio oficial)
    al sistema.
    """
    template_name = 'adicionar_audios_asterisk.html'
    form_class = AudiosAsteriskForm

    def form_valid(self, form):
        # download asterisk file
        language = form.cleaned_data['audio_idioma']
        instalador = AsteriskSoundsInstaller()
        error = instalador.install(language)
        if not error:
            messages.add_message(
                self.request, messages.SUCCESS,
                _('Se ha instalado el paquete de idioma satisfactoriamente.'))
        else:
            messages.add_message(
                self.request, messages.ERROR,
                _('Ha ocurrido un error al instalar el paquete de idioma'))
        return redirect('adicionar_audios_asterisk')


class PlaylistListView(ListView):
    """Vista para listar las Playlists"""
    model = Playlist
    paginate_by = 40
    template_name = 'playlist/lista_playlists.html'

    def get_context_data(self, **kwargs):
        context = super(PlaylistListView, self).get_context_data(**kwargs)
        obtener_paginas(context, 7)
        return context


class PlaylistCreateView(CreateView):
    model = Playlist
    form_class = PlaylistForm
    template_name = 'playlist/crear_playlist.html'

    def form_valid(self, form):
        self.object = form.save()
        playlist_config_creator = PlaylistsConfigCreator()
        playlist_config_creator.create_config_asterisk()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('editar_playlist', kwargs={'pk': self.object.pk})


class PlaylistDeleteView(DeleteView):
    model = Playlist
    template_name = 'playlist/eliminar_playlist.html'

    def get_success_url(self):
        return reverse('lista_playlist', kwargs={'page': 1})

    def dispatch(self, request, *args, **kwargs):
        playlist = self.get_object()

        # Si La playlist tiene musicas, no se puede borrar
        if playlist.musicas.exists():
            message = (_('No se puede eliminar una Playlist que tiene Músicas en Espera.'
                         ' Elimine las Músicas en Espera primero'))
            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            return redirect(self.get_success_url())

        # Si alguna campaña la tiene seleccionada No se puede borrar
        if playlist.campanas.exists():
            message = (_('No se puede eliminar una Playlist que está '
                         'siendo usada en una Campaña'))
            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            return redirect(self.get_success_url())
        return super(PlaylistDeleteView, self).dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        playlist = self.get_object()
        playlist_directory = PlaylistDirectoryManager()
        eliminacion_ok = playlist_directory.eliminar_directorio(playlist.nombre)

        if not eliminacion_ok:
            message = (_('Hubo un problema al eliminar la Playlist.'
                         ' Por Favor notifique a su Administrador.'))
            messages.add_message(
                self.request,
                messages.ERROR,
                message,
            )
            return redirect(self.get_success_url())

        message = (_('Playlist eliminada con éxito'))
        messages.add_message(
            self.request,
            messages.SUCCESS,
            message,
        )
        super(PlaylistDeleteView, self).delete(request, *args, **kwargs)

        playlist_config_creator = PlaylistsConfigCreator()
        playlist_config_creator.create_config_asterisk()

        return redirect(self.get_success_url())

    def get_object(self, queryset=None):
        return Playlist.objects.get(pk=self.kwargs['pk'])


class MusicaDeEsperaCreateView(ArchivoDeAudioMixin, CreateView):
    """ Vista que funciona como detalle de una playlist pero sirve para agregar Musica en Espera"""
    model = Playlist
    form_class = MusicaDeEsperaForm
    template_name = 'playlist/editar_playlist.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            self.playlist = Playlist.objects.get(id=kwargs.get('pk'))
        except Playlist.DoesNotExist:
            return redirect(reverse('lista_playlist', kwargs={'page': 1}))
        return super(MusicaDeEsperaCreateView, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super(MusicaDeEsperaCreateView, self).get_initial()
        initial['playlist'] = self.playlist
        return initial

    def get_context_data(self, **kwargs):
        context = super(MusicaDeEsperaCreateView, self).get_context_data()
        playlist_tmp = []

        for pl in self.playlist.musicas.all():

            if os.getenv('S3_STORAGE_ENABLED'):
                s3_handler = StorageService()
                playlist_tmp.append({'nombre': pl.nombre,
                                     'pk': pl.pk,
                                     'url': s3_handler.get_file_url(
                                         f'/media_root/{pl.audio_asterisk.name}')
                                     })
            else:
                base_url = "%s://%s" % (self.request.scheme,
                                        self.request.get_host())
                playlist_tmp.append({'nombre': pl.nombre,
                                     'pk': pl.pk,
                                     'url': f'{base_url}{pl.audio_original.url}'})

        context['playlist'] = playlist_tmp
        # TODO: Ver como hacer para que este form tenga info de is_valid.

        return context

    def form_valid(self, form):
        form.save()
        self._procesar_archivo_de_audio(form)

        return super(MusicaDeEsperaCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('editar_playlist', kwargs={'pk': self.playlist.id})


class MusicaDeEsperaDeleteView(DeleteView):
    model = Playlist
    template_name = 'playlist/eliminar_playlist.html'

    def get_success_url(self):
        return reverse('editar_playlist', kwargs={'pk': self.playlist_id})

    def dispatch(self, request, *args, **kwargs):
        musica = self.get_object()
        self.playlist_id = musica.playlist.id
        return super(MusicaDeEsperaDeleteView, self).dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        # Borro el archivo de la carpeta de asterisk
        musica = self.get_object()
        audio_file_asterisk = AudioConfigFile(musica)
        audio_file_asterisk.delete_asterisk()
        if os.getenv('S3_STORAGE_ENABLED'):
            s3_handler = StorageService()
            s3_handler.delete_file(musica.audio_asterisk.name, 'media_root')

        if musica.audio_original:
            if os.path.isfile(musica.audio_original.path):
                os.remove(musica.audio_original.path)

        super(MusicaDeEsperaDeleteView, self).delete(request, *args, **kwargs)

        message = (_('Musica de Espera eliminada con éxito'))
        messages.add_message(
            self.request,
            messages.SUCCESS,
            message,
        )
        return redirect(self.get_success_url())

    def get_object(self, queryset=None):
        return MusicaDeEspera.objects.get(pk=self.kwargs['pk'])
