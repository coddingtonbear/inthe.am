Response Codes
==============

All endpoints share the following list of common response codes:

+---------------+-------------------------------------------------------------------------------+
| Response Code | Description                                                                   |
+===============+===============================================================================+
| 200           | Success                                                                       |
+---------------+-------------------------------------------------------------------------------+
| 201           | Successfully created                                                          |
+---------------+-------------------------------------------------------------------------------+
| 400           | Your request was malformed, or the requested operation was impossible. A      |
|               | description of the problem will be included in the response.                  |
+---------------+-------------------------------------------------------------------------------+
| 401           | Your request did not include proper authentication headers. Make sure that    |
|               | you have properly sent the Authorization header described in                  |
|               | :ref:`authentication`.                                                        |
+---------------+-------------------------------------------------------------------------------+
| 403           | Your request was not properly authenticated or you have requested an entity   |
|               | for which you do not have access. Make sure that you have properly sent the   |
|               | Authorization header described in :ref:`authentication`.                      |
+---------------+-------------------------------------------------------------------------------+
| 404           | The entity you requested does not exist.                                      |
+---------------+-------------------------------------------------------------------------------+
| 405           | The request method used is not allowed for the endpoint you are sending it    |
|               | to. Please review the below documentation and alter your request to use an    |
|               | acceptable method.                                                            |
+---------------+-------------------------------------------------------------------------------+
| 409           | Your repository is currently locked. See :ref:`repository_locking` for more   |
|               | details.                                                                      |
+---------------+-------------------------------------------------------------------------------+
| 500           | A server error occurred while processing your request. An error was logged    |
|               | and the administrators of the site have been notified. Please try your        |
|               | request again later.                                                          |
+---------------+-------------------------------------------------------------------------------+

