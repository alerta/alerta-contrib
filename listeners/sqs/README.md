Amazon SQS Listeners
====================



Example
-------

To run the example:

1. Create an SNS Topic called "notify" and ensure the `sns` plug-in is listed in the enabled `PLUGINS` in the `alertad` configuration file.

2. Then create an SQS Queue called `example` and subscribe it to the SNS topic `notify`.

3. Ensure AWS access and secret keys for both `alertad` and this example script are configured.


!! Tip: Subscribe an email address to the `notify` topic to verify, via email, that alerts are being sent to the topic.


