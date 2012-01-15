Lemme Check That
================

A crude html resource change checker that's a pleasure to deploy.

Looks for changes in an html resource at a given url. Checks if the number of elements matching a
given css selector in the html has changed. If there's been a change, sends email to that effect to
a set of recipients.    

All the inputs are given via environment variables. They are:

* `BEANSTALK_URL`: The url to connect to beanstalkd with. The schema should be beanstalk, so
  something like `beanstalk://localhost:33333/`.
* `CHECK_URL`: The url to check for changes in. Must point to an html resource.
* `CHECK_SELECTOR`: The css selector to look for changes in.
* `NOTIFY_RECIPIENTS`: A json formatted list of recipients for notification when there's a
  change. Something like `["roderic@example.com", "asshat@example.com"]`
* `SMTP_HOST`: The host to connect to for sending email notification
* `SMTP_PORT`: The port for that same purpose.
* `FROM_ADDRESS`: The address the notification emails should say they're from.

All of these inputs are required.

Implementation Details
----------------------
Uses [Clockwork](https://github.com/tomykaira/clockwork) to schedule periodic
checks. [Beanstalk](http://kr.github.com/beanstalkd/) is used as a message queue. A python worker
listens for Clockwork's messages and performs the checks.

This's meant to be deployed in a [Heroku Cedar](http://devcenter.heroku.com/articles/cedar) like
environment, but isn't actually deployable to Heroku as far as I know, because of the mix of Python
and Ruby. For now, I just use [foreman](https://github.com/ddollar/foreman) locally and in a tiny
prod deployment.
