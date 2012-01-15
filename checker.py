import beanstalkc
import os
from pyquery import PyQuery as pq
from simplejson import loads
import smtplib
import sys
from urllib2 import urlopen
from uuid import uuid4

BEANSTALK_HOST = os.environ.get("BEANSTALK_HOST")
BEANSTALK_PORT = int(os.environ.get("BEANSTALK_PORT"))
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

class Notifier(object):
  def __init__(self):
    self.s = smtplib.SMTP(SMTP_HOST, SMTP_PORT)

  def notify(self, result):
    message = "Change in selector \"%s\" for url \"%s\". Had %s elements, now %s."
    message = message % (CHECK_SELECTOR, CHECK_URL, result[1], result[0])
    self.s.sendmail(FROM_ADDRESS, NOTIFY_RECIPIENTS, message)

if __name__ == "__main__":
  beanstalk = beanstalkc.Connection(host=BEANSTALK_HOST, port=BEANSTALK_PORT)
  beanstalk.watch("lemme-check-that")
  beanstalk.ignore("default")
  checker = Checker()
  notifier = Notifier()
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
      notifier.notify(result)

  print "Shutting down."
  sys.exit()
