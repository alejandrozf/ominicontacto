# Release Notes
pre.release

## Added
- oml-2679 New Omnidialer service.
- oml-2923 Order and filtering adding agents in Campaigns Wizard.
- oml-2893 Massive download and deletion of agendas.
- oml-2886 Allow contact database structure definition on campaign wizard.
- oml-2921 Allow configuring Agents as IVR destinations.

## Changed

- oml-2750 Whatsapp Line Wizard allows selection of any inbound campaign.
- oml-3040 The generation of the oml_pjsip_agents.conf file was optimized to search for PJSIP endpoints in Kamailio
- oml-3035 Replacement of slowsql logger.
- oml-3102 Ended campaigns added when filtering Agendas search.
- oml-800  Command regenerar_asterisk no longer regenerates cron tasks.

## Fixed

- oml-2931 Fix "enmodoselect" Incidence rule.
- oml-2997 Fix 'easyaudits' logs ip field.
- oml-3079 Avoid unnecessary regeneration of all Campaigns data in redis.
- oml-3117 Fix On Hold Timer stop condition.

## Removed

No removals in this release.

## Migrations

ominicontacto_app: 0111
