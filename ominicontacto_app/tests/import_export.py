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

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from ominicontacto_app.models import User
from ominicontacto_app.tests.factories import GrupoFactory
from ominicontacto_app.tests.utiles import OMLBaseTest


class AuthExportTests(OMLBaseTest):
    ejecutar_actualizar_permisos = True

    def setUp(self):
        super().setUp()
        GrupoFactory.reset_sequence()
        self.agente = self.crear_agente_profile()
        self.supervisor = self.crear_supervisor_profile(rol=User.SUPERVISOR)

    def test_authorized_export_succeed(self):
        self.client.force_login(self.supervisor.user)
        self.assertEqual(
            self.client.post(
                reverse("descargar_usuarios_csv"),
                {},
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.post(
                reverse("descargar_usuarios_csv"),
                {
                    "search": "user_test",
                },
            ).status_code,
            200,
        )

    def test_unauthorized_export_fails(self):
        self.client.force_login(self.agente.user)
        self.assertEqual(
            self.client.post(
                reverse("descargar_usuarios_csv"),
                {},
            ).status_code,
            403,
        )
        self.assertEqual(
            self.client.post(
                reverse("descargar_usuarios_csv"),
                {
                    "search": "user_test",
                },
            ).status_code,
            403,
        )


class AuthImportTests(OMLBaseTest):
    ejecutar_actualizar_permisos = True

    def setUp(self):
        super().setUp()
        GrupoFactory.reset_sequence()
        self.agente = self.crear_agente_profile()
        self.supervisor = self.crear_supervisor_profile(rol=User.SUPERVISOR)

    def test_authorized_import_succeed(self):
        self.client.force_login(self.supervisor.user)
        self.assertEqual(
            self.client.post(
                reverse("importar_usuarios_csv"),
                {
                    "archivo": SimpleUploadedFile("users-import.csv", "", content_type="text/csv"),
                },
            ).status_code,
            302,
        )

    def test_unauthorized_import_fails(self):
        self.client.force_login(self.agente.user)
        self.assertEqual(
            self.client.post(
                reverse("importar_usuarios_csv"),
                {
                    "archivo": SimpleUploadedFile("users-import.csv", "", content_type="text/csv"),
                },
            ).status_code,
            403,
        )


class ExportCsvUsuariosTests(OMLBaseTest):
    def setUp(self):
        super().setUp()
        GrupoFactory.reset_sequence()
        self.agente = self.crear_agente_profile()
        self.supervisor = self.crear_supervisor_profile(rol=User.SUPERVISOR)
        self.csv_row_0 = "username,first_name,last_name,profile,email,password,group,auth"
        self.csv_row_1 = "user_test_agente_0,User_0,Test,Agente,user_agente@gmail.com,,grupo_0.dat,"
        self.csv_row_2 = "user_test_supervisor_1,,,Supervisor,user_supervisor@gmail.com,,,"
        self.client.force_login(self.supervisor.user)

    def _assertResponseIsCSV(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["content-type"], "text/csv")

    def test_filtered_export_succeed(self):
        response_with_all = self.client.post(
            reverse("descargar_usuarios_csv"),
            {
                "search": "user_test",
            },
        )
        self._assertResponseIsCSV(response_with_all)
        self.assertEqual(
            response_with_all.getvalue().decode().splitlines(),
            [
                self.csv_row_0,
                self.csv_row_1,
                self.csv_row_2,
            ],
        )
        response_with_agent = self.client.post(
            reverse("descargar_usuarios_csv"),
            {
                "search": "agente",
            },
        )
        self._assertResponseIsCSV(response_with_agent)
        self.assertEqual(
            response_with_agent.getvalue().decode().splitlines(),
            [
                self.csv_row_0,
                self.csv_row_1,
            ],
        )

    def test_unfiltered_export_succeed(self):
        response = self.client.post(reverse("descargar_usuarios_csv"), {})
        self._assertResponseIsCSV(response)
        self.assertEqual(
            response.getvalue().decode().splitlines(),
            [
                self.csv_row_0,
                self.csv_row_1,
                self.csv_row_2,
            ],
        )


class ImportCsvUsuariosTests(OMLBaseTest):
    def setUp(self):
        super().setUp()
        GrupoFactory.reset_sequence()
        self.supervisor = self.crear_supervisor_profile(rol=User.SUPERVISOR)
        self.csv_row_0 = "username,first_name,last_name,profile,email,password,group,auth"
        self.csv_row_1 = "user_agente,,,Agente,agente@example.com,,grupo_0.dat,LDAP"
        self.csv_row_2 = "user_supervisor,,,Supervisor,,,,Normal"
        self.csv_row_3 = "user_administrator,,,Administrador,,,,Normal"
        self.csv_row_4 = "user_gerente,,,Gerente,,,,Normal"
        self.csv_row_5 = "user_referente,,,Referente,,,,"
        self.client.force_login(self.supervisor.user)

    def test_import_succeed(self):
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username="user_agente")
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username="user_supervisor")
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username="user_administrator")
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username="user_gerente")
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username="user_referente")

        GrupoFactory(auto_unpause=0)
        response = self.client.post(
            reverse("importar_usuarios_csv"),
            {
                "archivo": SimpleUploadedFile(
                    "users-import.csv",
                    "\r\n".join(
                        [
                            self.csv_row_0,
                            self.csv_row_1,
                            self.csv_row_2,
                            self.csv_row_3,
                            self.csv_row_4,
                            self.csv_row_5,
                        ]
                    ).encode(),
                    content_type="text/csv",
                ),
            },
        )
        self.assertEqual(response.status_code, 302)
        user_agente = User.objects.get(username="user_agente")
        self.assertTrue(user_agente.rol)
        self.assertEqual(user_agente.rol.name, "Agente")
        self.assertTrue(hasattr(user_agente, "agenteprofile"))
        self.assertTrue(user_agente.agenteprofile.destinos_entrantes.exists())
        self.assertTrue(hasattr(user_agente, "autenticacion_externa"))
        user_supervisor = User.objects.get(username="user_supervisor")
        self.assertTrue(user_supervisor.rol)
        self.assertEqual(user_supervisor.rol.name, "Supervisor")
        self.assertTrue(hasattr(user_supervisor, "supervisorprofile"))
        self.assertEqual(user_supervisor.supervisorprofile.is_administrador, False)
        self.assertEqual(user_supervisor.supervisorprofile.is_customer, False)
        self.assertTrue(hasattr(user_supervisor, "autenticacion_externa"))
        user_administrator = User.objects.get(username="user_administrator")
        self.assertTrue(user_administrator.rol)
        self.assertEqual(user_administrator.rol.name, "Administrador")
        self.assertTrue(hasattr(user_administrator, "supervisorprofile"))
        self.assertEqual(user_administrator.supervisorprofile.is_administrador, True)
        self.assertEqual(user_administrator.supervisorprofile.is_customer, False)
        self.assertTrue(hasattr(user_administrator, "autenticacion_externa"))
        user_gerente = User.objects.get(username="user_gerente")
        self.assertTrue(user_gerente.rol)
        self.assertEqual(user_gerente.rol.name, "Gerente")
        self.assertTrue(hasattr(user_gerente, "supervisorprofile"))
        self.assertEqual(user_gerente.supervisorprofile.is_administrador, False)
        self.assertEqual(user_gerente.supervisorprofile.is_customer, False)
        self.assertTrue(hasattr(user_gerente, "autenticacion_externa"))
        user_referente = User.objects.get(username="user_referente")
        self.assertTrue(user_referente.rol)
        self.assertEqual(user_referente.rol.name, "Referente")
        self.assertTrue(hasattr(user_referente, "supervisorprofile"))
        self.assertEqual(user_referente.supervisorprofile.is_administrador, False)
        self.assertEqual(user_referente.supervisorprofile.is_customer, True)
        self.assertFalse(hasattr(user_referente, "autenticacion_externa"))
