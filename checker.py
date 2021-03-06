import beanstalkc
from email.mime.text import MIMEText
import os
from pyquery import PyQuery as pq
from simplejson import loads
import smtplib
import sys
from urllib2 import urlopen
from urlparse import urlparse
from uuid import uuid4

BEANSTALK_URL = urlparse(os.environ.get("BEANSTALK_URL"))
BEANSTALK_HOST = BEANSTALK_URL.hostname
BEANSTALK_PORT = BEANSTALK_URL.port
CHECK_URL = os.environ.get("CHECK_URL")
CHECK_SELECTOR = os.environ.get("CHECK_SELECTOR")
SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = os.environ.get("SMTP_PORT")
FROM_ADDRESS = os.environ.get("FROM_ADDRESS")
NOTIFY_RECIPIENTS = loads(os.environ.get("NOTIFY_RECIPIENTS"))

class Checker(object):
  def __init__(self):
    self.old_num = None

  def check(self):
    print "Calling %s." % CHECK_URL
    doc = urlopen(CHECK_URL)
    q = pq(doc.read())
    doc.close()
    num = len(q(CHECK_SELECTOR))
    print "New number is %s. Old number is %s." % (num, self.old_num)

    if (self.old_num is None) or (num == self.old_num):
      print "Nothing's changed"
      self.old_num = num
      return False
    else:
      old_old = self.old_num
      self.old_num = num
      return (num, old_old)

def notify(result):
  s = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
  message = "Change in selector \"%s\" for url \"%s\". Had %s elements, now %s."
  message = MIMEText(message % (CHECK_SELECTOR, CHECK_URL, result[1], result[0]))
  message["Subject"] = "[lemme-check-that] Change in \"%s\"" % CHECK_SELECTOR
  message["From"] = FROM_ADDRESS
  message["To"] = ", ".join(NOTIFY_RECIPIENTS)
  s.sendmail(FROM_ADDRESS, NOTIFY_RECIPIENTS, message.as_string())

if __name__ == "__main__":
  beanstalk = beanstalkc.Connection(host=BEANSTALK_HOST, port=BEANSTALK_PORT)
  beanstalk.watch("lemme-check-that")
  beanstalk.ignore("default")
  checker = Checker()
  running = True

  while running:
    sys.stdout.flush()
    message = beanstalk.reserve()
    body = message.body
    message.delete()

    if body == "stop":
      running = False
      continue

    result = checker.check()
    if result:
      print "Telling the recipients there was a change."
      notify(result)

  print "Shutting down."
  sys.exit()
