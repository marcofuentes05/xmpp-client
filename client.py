import logging
from getpass import getpass
from argparse import ArgumentParser
import sys
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
    self.add_event_handler('message', self.recieveMessage)
    # self.add_event_handler('auth_success', self.loginSuccess)

  async def receiveMessage(self, msg):
    if msg['type'] in ('normal', 'chat'):
      print('NEW MESSAGE:\t', msg)

  async def start(self, event):
    self.send_presence()
    roster = await self.get_roster()
    print('\n\nROSTER:\n',roster, '\n\n')
    self.send_message(mto=self.recipient, mbody=self.msg)
    self.disconnect()

  async def loginFail(self, event):
    print('\n\n\nCREDENCIALES INCORRECTAS\n\n\n')

class Client(slixmpp.ClientXMPP):
  def __init__(self, jid, password):
    try:
      print('Loading...')
      super().__init__(jid, password)
    except:
      pass
    self.add_event_handler('session_start', self.start)
    self.add_event_handler('failed_auth', self.loginFail)
    self.add_event_handler("groupchat_message", self.muc_message)
    self.add_event_handler('register', self.userRegister)
    self.add_event_handler('message', self.message)
    self.received = set()


  async def start(self, event):
    self.send_presence()
    await self.get_roster()
    try:
      sigue = True
      while (sigue):
        response1 = input("""
        Ingresa la opción que desees:
        1. Mostrar usuarios conectados
        2. Mostrar contactos                      - 
        3. Agregar usuario a contactos            -
        4. Mostrar detalles de un contacto
        5. Chatear con alguien
        6. Unirse a chat grupal
        7. Enviar mensaje de presencia
        8. Enviar archivo
        9. Eliminar mi cuenta
        10 Ver respuestas
        11 Salir
        """)
        if response1=='1':
          pass
        elif response1 == '2':
          groups = self.client_roster.groups()
          for group in groups:
            for jid in groups[group]:
              name = self.client_roster[jid]['name']
              print('Nombre: {}'.format(jid))
              connections = self.client_roster.presence(jid)
              for client, status in connections.items():
                  if status['status']:
                    print('Estado: {}'.format(status['status']))
        elif response1 == '3':
          userjid = input('Ingresa el JID de tu compa:\t')
          self.send_presence_subscription(pto=userjid)
          self.send_message(mto=userjid, mbody='Hola!', mtype='chat', mfrom=self.boundjid.bare)
        elif response1 == '4':
          userjid = input('Ingresa el JID de tu compa: \t')
          print(self.client_roster[userjid])
        elif response1=='5':
          userjid = input('Ingresa el JID de tu compa: \t')
          chatstate = self.Message()
          chatstate['chat_state'] = 'composing'
          chatstate['to'] = userjid
          chatstate.send()
          await self.get_roster()
          msg = input('Ingresa el mensaje a enviar:\n')
          self.send_message(mto=userjid,
                            mbody=msg,
                            mtype='chat')
          chatstate = self.Message()
          chatstate['chat_state'] = 'active'
          chatstate['to'] = userjid
          chatstate.send()
          await self.get_roster()
        elif response1=='6':
          room = input('Ingresa el JID del room al que deseas entrar: \t')
          nickname = input('Ingresa tu nickname: \t')
          await self.plugin['xep_0045'].joinMUC(room ,nickname, wait=True)

        elif response1=='7':
          loop = True
          while(loop):
            print(
                '''
                1. Available
                2. Unavailable
                3. Do not disturb
                '''
            )
            presence = input('Elija un estado: ')
            if presence == '1':
              presence_show = 'chat'
              status = 'Available'
              loop = False
            elif presence == '2':
              presence_show = 'away'
              status = 'Unavailable'
              loop = False
            elif presence == '3':
              presence_show = 'dnd'
              status = 'Do not Disturb'
              loop = False
            else:
              print('Opcion invalida')
          try:
            self.send_presence(pshow=presence_show, pstatus=status)
            logging.info('Presence set')
          except IqError:
            logging.error('Error al enviar presencia')
          except IqTimeout:
            logging.error('No hubo respuesta del servidor')
        elif response1=='8':
          pass
        elif response1=='9':
          self.connect()
          self.delete_account()
        elif response1=='10':
          await self.get_roster()
        elif response1=='11':
          sigue=False
          self.disconnect()
          return None
    except IqError as err:
      print('Error: %s' % err.iq['error']['condition'])
    except IqTimeout:
      print('Error: Request timed out')
    
  async def muc_message(self, msg):
    print('MESSAGE FROM {}: {}'.format(msg['from'], msg['body']))
    if msg['mucnick'] != self.nick:
      self.send_message(mto=msg['from'].bare,
                        mbody=msg['body'],
                        mtype='groupchat')
    # PENDING IMPLEMENTATION

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

  async def logOut(self):
    self.disconnect()

  async def message(self, msg):
    logging.info(msg)
    if msg['type'] in ('normal', 'chat'):
      print('\n{} *DICE*: {}\t'.format(msg['from'], msg['body']))

  def delete_account(self):
    self.register_plugin("xep_0030")
    self.register_plugin("xep_0004")
    self.register_plugin("xep_0199")
    self.register_plugin("xep_0066")
    self.register_plugin("xep_0077")

    delete = self.Iq()
    delete['type'] = 'set'
    delete['from'] = self.boundjid.user
    delete['register']['remove'] = True
    delete.send()

    print("Account deleted succesfully.")
    self.disconnect() 
