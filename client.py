import logging
from getpass import getpass
from argparse import ArgumentParser

import slixmpp
from slixmpp import ClientXMPP
from slixmpp.exceptions import IqError, IqTimeout
from slixmpp.xmlstream.asyncio import asyncio

class SendMessageBot(slixmpp.ClientXMPP):
  def __init__(self, jid, password, receipient, msg):
    try:
      super().__init__(jid, password)
    except:
      logging.error("login fail")
    self.recipient = receipient
    self.msg = msg
    self.add_event_handler('session_start', self.start)
    self.add_event_handler('failed_auth', self.loginFail)
    # self.add_event_handler('auth_success', self.loginSuccess)

  async def start(self, event):
    self.send_presence()
    roster = await self.get_roster()
    print('\n\nROSTER:\n',roster, '\n\n')
    self.send_message(mto=self.recipient, mbody=self.msg)
    self.disconnect()

  async def loginFail(self, event):
    print('\n\n\nCREDENCIALES INCORRECTAS\n\n\n')

  # def loginSuccess(self, event  ):
  #   print('\n\n\nCREDENCIALES CORRECTAS!!!!!!\n\n\n')

class Client(slixmpp.ClientXMPP):
  def __init__(self, jid, password):
    try:
      super().__init__(jid, password)
    except:
      pass
    self.add_event_handler('session_start', self.start)
    self.add_event_handler('failed_auth', self.loginFail)
    self.add_event_handler('register', self.userRegister)
    self.received = set()


  async def start(self, event):
    self.send_presence()
    try:
      await self.get_roster()
      response1 = input("""
      Ingresa la opción que desees:
      1. Mostrar usuarios conectados
      2. Agregar usuario a contactos
      3. Mostrar detalles de un usuario
      4. Chatear con alguien
      5. Unirse a chat grupal
      6. Enviar mensaje de presencia

      """)
      if response1 == '1':
        user.presences_received = asyncio.Event()
    except IqError as err:
      print('Error: %s' % err.iq['error']['condition'])
    except IqTimeout:
      print('Error: Request timed out')
    
  async def userRegister(self, event):
    resp = self.Iq()
    resp['type'] = 'set'
    resp['register']['username'] = self.boundjid.user
    resp['register']['password'] = self.password

    try:
        await resp.send()
        logging.info("Account created for %s!" % self.boundjid)
    except IqError as e:
        logging.error("Could not register account: %s" %
                      e.iq['error']['text'])
        self.disconnect()
    except IqTimeout:
        logging.error("No response from server.")
        self.disconnect()

  def wait_for_presences(self, pres):
    """
      Track how many roster entries have received presence updates.
      """
    self.received.add(pres['from'].bare)
    if len(self.received) >= len(self.client_roster.keys()):
      self.presences_received.set()
    else:
      self.presences_received.clear()

  async def loginFail(self, event):
    print('CREDENCIALES INCORRECTAS')
    self.disconnect()

# if __name__ == '__main__':
#     # Setup the command line arguments.
#     parser = ArgumentParser(description=SendMessageBot.__doc__)

#     # Output verbosity options.
#     parser.add_argument("-q", "--quiet", help="set logging to ERROR",
#                         action="store_const", dest="loglevel",
#                         const=logging.ERROR, default=logging.INFO)
#     parser.add_argument("-d", "--debug", help="set logging to DEBUG",
#                         action="store_const", dest="loglevel",
#                         const=logging.DEBUG, default=logging.INFO)

#     # JID and password options.
#     parser.add_argument("-j", "--jid", dest="jid",
#                         help="JID to use")
#     parser.add_argument("-p", "--password", dest="password",
#                         help="password to use")
#     parser.add_argument("-t", "--to", dest="to",
#                         help="JID to send the message to")
#     parser.add_argument("-m", "--message", dest="message",
#                         help="message to send")

#     args = parser.parse_args()

#     # Setup logging.
#     logging.basicConfig(level=args.loglevel,
#                         format='%(levelname)-8s %(message)s')

#     if args.jid is None:
#         args.jid = input("Username: ")
#     if args.password is None:
#         args.password = getpass("Password: ")
#     if args.to is None:
#         args.to = input("Send To: ")
#     if args.message is None:
#         args.message = input("Message: ")

#     # Setup the EchoBot and register plugins. Note that while plugins may
#     # have interdependencies, the order in which you register them does
#     # not matter.
#     xmpp = SendMessageBot(args.jid, args.password, args.to, args.message)
#     xmpp.register_plugin('xep_0030')  # Service Discovery
#     xmpp.register_plugin('xep_0199')  # XMPP Ping

#     # Connect to the XMPP server and start processing XMPP stanzas.
#     xmpp.connect()
#     xmpp.process(forever=False)


