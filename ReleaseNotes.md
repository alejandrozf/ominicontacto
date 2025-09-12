# Release Notes
pre.release

## Added
- oml-3000 Add Agent Group setting to restrict password update.
- oml-3002 User bulk remove.
- oml-3115 Add Campaign setting to allow showing callid in disposition form.
- oml-3116 DTMF input form for agent's softphone (allowing copying long DTMF codes).

## Changed

- oml-2996 Disposition form is always displayed for Inbound calls.

## Fixed

- oml-2999 Fix phone validation regex.
- oml-3037 Fix recording search tests.
- oml-3028 Fix recording search pagination buttons.
- oml-3048 Fix Respect call autoattend configuration for transfers to campaigns (OOS)
- oml-3145 Fix error Show Campaigns modal in agents list.
- oml-3127 Fix observation column missing when blank in dispositions report.
- oml-3146 Fix agent dropdown menu placement.
- oml-3154 Fix custom contact DB validation in campaign wizard.

## Removed

No removals in this release.

## Migrations

ominicontacto_app: 0112, 0113
