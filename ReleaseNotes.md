# Release Notes
260406.01

## Added

- oml-3158 New Channel: Messenger Meta
- oml-3175 Added new Whatsapp template type support.
- oml-3243 Bulk Messages: Added several Whatsapp template types support.
- oml-3042 UI Improvements: Sidebar, Dark mode, Icons, Vue transitions, Supervision.

## Changed

- oml-3169 Edit Interactive menues from Line Options.
- oml-3280 Change IdentificadorCliente url field max_length=512
- oml-3294 Add inbound/outbound tags to agents conversations.

## Fixed

- oml-2972 Fix agent blocked dispositioning with force unpause.
- oml-3171 Fix: Do not show hidden disposition options in Whatsapp disposition menu.
- oml-3275 Fix slow load time for new Whatsapp conversations.
- oml-3269 Fix add asterisk queue member with correct pause state.
- oml-3047 Fix do not show "contact not saved" on identified inbound contacts transfers.
- oml-3279 Fix Consultative transfer for campaigns with survey error.
- oml-3286 Fix External Site Authentication form validation.
- oml-3287 Improved Whatsapp usability and fixes attachments and transfers problems.
- oml-3288 Handle Whatsapp fowarded messages safely.
- oml-3289 Fix Whatsapp time validation logic.
- oml-3294 Fix Whatsapp conversation and transfers issues.
- oml-3293 Fix Whatsapp attachment files uploading issues. 

## Removed

- No removals in this release.

## Migrations

2.6.0 whatsapp_app: 0015
2.6.1 ominicontacto_app: 0114, 0115
2.6.2 ominicontacto_app: 0116
2.6.3 whatsapp_app: 0016
2.6.4 ominicontacto_app: 0117
      facebook_meta_app: 0001
      configuracion_telefonia_app: 0024, 0025
