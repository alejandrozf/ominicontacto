Helping adding more languages
=============================

If you consider helping OMniLeads adding another language please follow the next steps:

Create an issue as described in the file CONTRIBUTING.md

The translation must be performed for the Django component and the VueJs Frontend.

- Add the new language entry in the settings variable LANGUAGES (see ominicontacto/settings/defaults.py)

- In the repository root folder run the commands:

$ ./manage.py makemessages --locale=<your-language-code>

$ ./manage.py makemessages -d djangojs --locale <your-language-code>

Localize and fill the translations in all the files *.po in the following folders:

api_app/locale/LC_MESSAGES/<your-language-code>/
configuracion_telefonia_app/locale/LC_MESSAGES/<your-language-code>/
notificacion_app/locale/LC_MESSAGES/<your-language-code>/
ominicontacto_app/locale/LC_MESSAGES/<your-language-code>/
reciclado_app/locale/LC_MESSAGES/<your-language-code>/
reportes_app/locale/LC_MESSAGES/<your-language-code>/
supervision_app/locale/LC_MESSAGES/<your-language-code>/
whatsapp_app/locale/LC_MESSAGES/<your-language-code>/

- In the repository root folder run the command:

$ ./compilemessages

- Create a file <your-language-code>.js in the folders "forms", "globals", "models" and "views" found at omnileads_ui/src/locales. Each of this files must replicate the content of the other languages js files found in each folder (for example en.js) but with the corresponding translation.

- Create the corresponding file omnileads_ui/src/locales/locales.<your-language-code>.js, you can use locales.en.js as an example but replacing the language code tom import the files created in the previous step.

- Edit omnileads_ui/src/locales/index.js adding the corresponding imports and export entries.

- Check if the system accepts correctly the new language

- Submit your changes, except for the *.mo generated files, according to the issue and create the corresponding merge request.
