import logging
from getpass import getpass
from argparse import ArgumentParser

import slixmpp


class EchoBot(slixmpp.ClientXMPP):
  def __init__(self, jid, password):
    super().__init__(jid, password)
    self.add_event_handler('session_start', self.start)
    self.add_event_handler('message', self.message)
  
  async def start(self, event):
    self.send_presence()
    await self.get_roster()


  def message(self, msg):
      if msg['type'] in ('normal', 'chat'):
          msg.reply("Thanks for sending:\n%s" % msg['body']).send()

  def repond(sef):
    #sends xmpp message to the user
    pass
