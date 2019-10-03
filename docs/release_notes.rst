Release Notes
*************

*Octuber 3, 2019*

Release 1.3.2 details
=========================

What's new
=========================

- You can now add your custom Asterisk code in OMniLeads!
- OML now can be reached behind NAT
- Registration of OML instances now sends an email with the key to the admin when registration is successful
- Documentation was translated to English
- CI/CD now got improved with jobs that tests all kind of installations we support
- Asterisk audios can be now be added dinamically from UI


Installation tasks
---------------------------------------------------------------
- Fixed  error on identification audio files routes
- When upgrading the system installation avoids current inventory modification
- Hostname is not needed now for host node installations
- User can add its own certificate in inventory
- Added retries for long downloading time tasks that could failed by connection
- Redis container persistence was improved (for dev-env & prod-env environments)
- Dev-env was improved to read environment variables from .env file like prod-env.
- A change in variable PGPASSWORD on its .env fike, apply also this change on postgres container
- Uninstallation script was added


OML admin
-------------------------
- Abandon average, waiting average and number of waiting calls reports were added for inbound campaigns
- Fixed error that didn't allow to recycle more than one time a dialer campaign
- Fixed error when tried to access daily agents report
- Fixed error in IVR forms validation when uploading external audio files
- Fixed error on dialer campaign update wizard that didn't allow to modify its engaged disposition options forms
- Fixed error that didn't allow to edit campaigns with external field attribute setted
- Fixed exception generated when accessing to campaign reports
- Contact databases names must be differents now
- Agent Groups must be differents now


OML agent view
------------------------
- Fixed error that ocurred when user visualized call registry, more information were added also
- Recalling option was added for every call registered


Asterisk dialplan
------------------------
- More descriptive logs were added
- Fixed error on Blacklist events when saving to database
- Fixed error on IVR delay
- Fix error when handling IVR incorrect option

Misc
------------------------
- First integration tests were introduced, integrated with CI/CD jobs
- A cron job to clean table 'queue_log' daily was added
- Javascript code was separated from Django templates
- Static files were moved to its related project apps
- Redirection to an internal url when logged to the system was added
