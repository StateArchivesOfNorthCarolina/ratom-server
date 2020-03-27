Administrator's Guide: Version 1.0
=================================

Files
-----

What to do if a file is added to the wrong account
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the event a user adds a file to the wrong account and it ingests
successfully, you must delete the file from the account and re-ingest
the file.

If the file that was ingested is *retired\_governor.pst*

#. Log into your administrator's account at http://RATOM\_DOMAIN/admin
#. Navigate to *Files*
#. Find the file by name in the list *retired\_governor.pst*
#. Select that row with the checkbox
#. From the action menu select **Delete selected files** and select the
   **Go** button
#. Review the Summary
#. Select the **Yes, I'm sure** button

Depending on the number of messages this could take a few minutes as the
elasticsearch index will be updated during this process.
