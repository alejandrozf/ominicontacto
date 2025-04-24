# Release Notes
2025-02-21

## Added

- oml-2746 New Disposition form List field with options fetched from CRM.
- oml-2788 Possibility to add Sub-Dispositions.
- oml-2889 Supervisiors can send messages to Agents.
- oml-2924 Massive Users profiles imports.

## Changed

- oml-2750 Whatsapp Line Wizard allows selection of any inbound campaign.
- oml-2892 Enable recordings set by default in Campaign Wizard.
- oml-2891 DB Select input with search capabilities in Campaign Wizard.
- oml-2844 Whatsapp Line Interactive Menu management allows non connected menues.
- oml-2845 Is now not possible to deactivate Whatsapp for Line destination campaigns.
- oml-2934 Inbound Routes language options are now selected from installed asterisk audios.
- oml-2738 Decoupling recording report generation for async processing.
- oml-2887 Change in the way Database Contacts are counted.
- oml-2888 Possibility to select the Agenda telephone.
- oml-2922 Campaign lists views can be ordered by id.

## Fixed

- oml-2859 Fix command for closing conversations.
- oml-2722 Fix External Site Authentication form validation
- Error testing External Site Authentication.
- Error in notification of External Site interaction result.
- Race condition with LlamadaLog log and External Site interaction with 'datetime' parameter.
- oml-2933 Fix uwsgi problem with long uris.
- Fix generation of ActividadAgenteLog "UNPAUSEALL" event when agents receive calls
- oml-686 Fix for backup restores
- oml-2980 Fix Whatsapp Line edit form wizard problems with templates and groups of hours.
- oml-2964 Fix unwanted Whatsapp line deletion when removing associated objects.
- oml-2995 Avoid error 500 on invalid CRM_contact_data parameter json.

## Removed

No removals in this release.
