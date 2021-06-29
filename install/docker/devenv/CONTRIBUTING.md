#########################################################
### DevEnv. Omnileads Docker container for developers ###
#########################################################

For any question or contribution you want to do in these environment don't hesitate you open an issue in the Gitlab's project:

https://gitlab.com/omnileads/ominicontacto/issues

Thank you for your cooperation!

*********************************
* OMniLeads for Windows and Mac *
*********************************

We know that Docker opens the door to have our product working in Windows or Mac. That would be awesome, but, we are Linux guys, so the testing in these platforms haven't been done yet. If you are a Docker advanced user in Windows or Mac and want to help us with this testing please take this in mind:

  * The folders recordings and sounds that are created need to be chowned by a user with UID and GID 1000. This is necessary to have the correct user chowned inside containers: (asterisk user UID 1000 in asterisk container and omnileads user UID 1000 in omniapp container)

This is very important because recordings are essential data for a call center. Taking this in mind, consider helping us with knowledge about Docker volume drivers usage for Windows and Mac.
https://www.reddit.com/r/docker/comments/8heetn/docker_for_win_how_to_find_windows_usergroup_id/

You can contact us through our social networks (facebook, instagram or twitter) or raising up an issue in Gitlab.

https://gitlab.com/omnileads/ominicontacto/issues