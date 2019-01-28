Helping adding more languages
=============================

If you consider helping OMniLeads adding another language please follow the next steps:

Create an issue as described in the file CONTRIBUTING.md

- In the repository root folder run the commands:

$ ./manage.py makemessages --locale=<your-language-code>

$ ./manage.py makemessages -d djangojs --locale <your-language-code>

Localize and fill the translations in all the files *.po in the following folders:

configuracion_telefonia_app/locale/LC_MESSAGES/<your-language-code>/
ominicontacto_app/locale/LC_MESSAGES/<your-language-code>/
reportes_app/locale/LC_MESSAGES/<your-language-code>/
reciclado_app/locale/LC_MESSAGES/<your-language-code>/

- In the repository root folder run the command:

$ ./compilemessages

- Check if the system accepts correctly the new language

- Add the new language entry in the settings variable LANGUAGES (see ominicontacto/settings.py)

- Submit your changes, except for the *.mo generated files, according to the issue and create the corresponding merge request.
