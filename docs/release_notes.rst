Release Notes
*************

*July 15, 2019*

Release 1.3.0 details
=========================

What's new
=========================

- New phone configuration option to specify custom identification on inbound calls
- Asterisk version was updated to 16.4.0
- Supervision version was rewritten from scratch in Python/Django
- CRM integrations are completely implemented to interact from-to OML
- Added installation option to have a production environment based on docker



Installation tasks
---------------------------------------------------------------
- Added .pgpass file for root user on bare-metal installations
- Fixed bug that inhibits to specify a hostname containing the digit "0" on inventory
- Added pip upgrade task on bare-metal installations, only for post-installations tasks
- Fixed bug that made user to execute sometimes twice deploy script on bare-metal installations
- Fixed permission error when uploading audio files
- Kamailio now is configured to not generate debug logs on bare metal installations
- Docker develop enviroment was refined to follow Docker best practices
- Kamailio now uses redis for its DB backend, now it's fully independent from OML DB


OML admin
-------------------------
- Fixed aesthetical error on contactation report
- Added validation in first campaign creation step to prevent fill external url field if user has not selected this interaction type
- Added callid-based for calls recordings filter
- The admin view now shows current release on "About" section
- A section to register an OML installation was added
- A section to allow user to send feedback about OML was added
- Agent interface information (on view that adds agents to campaign) was modified in
order to make it more clear to users
- Better colors were added for inbound campaigns reports
- Fav icon was added
- Validations on campaign forms creation were added

OML agent view
------------------------
- Fixed error that prevents tag call recordings
- Added posibility that agents can make calls outside of any campaign assigned
- Tripartite conference was added in calls

Asterisk dialplan
------------------------
- Fixed sintax error on DB insertion
- Fixed bug on expired call on failover
- Fixed bug that keeps agents on BUSY state when she doesn't attend an inbound or transfer call
- Fixed bug that makes insertions on recording DB table even for dialer campaigns even if the campaing wasn't configured to make recordings
- Fixed inconsistency on 'queue_log' logs table when a client hangs in a middle of a consultative transfer call

Misc
------------------------
- Fixed trigger error that doesn't allow to insert certain asterisk logs in queue_log table
- Fixed bug that doesn't allow to insert some asterisk on queue_log table due to field length
- Ignored AMI errors logged when Asterisk regeration command is executed
- A Restfull API with a few initial endpoint was added
- A django command for update system components settings was added
- Django settings were refactored to allow distinct configurations in an easy way
