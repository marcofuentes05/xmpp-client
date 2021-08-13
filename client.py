# --------------------------------------------
# client.py                                  |
# Marco Fuentes - 18188                      |
# Guatemala, 2021                            |
# Defines the Client class to comunicate via |
# XMPP                                       |
# --------------------------------------------

import logging
from getpass import getpass
from argparse import ArgumentParser
import sys
import slixmpp
from slixmpp import ClientXMPP
from slixmpp.exceptions import IqError, IqTimeout
from slixmpp.xmlstream.asyncio import asyncio

# Class definition
class Client(slixmpp.ClientXMPP):
  def __init__(self, jid, password):
    try:
      # Call ClientXMPP constructor with given props
      print('Loading...')
      super().__init__(jid, password)
    except:
      pass
      
    # Define event handlers for interesting events.
    self.add_event_handler('failed_auth', self.loginFail)
    self.add_event_handler("groupchat_message", self.muc_message)
    self.add_event_handler('register', self.userRegister)
    self.add_event_handler('message', self.message)
    self.add_event_handler('session_start', self.start)

  # Define main flow
  async def start(self, event):
    # Send initial presence, ONLINE status
    self.send_presence()
    chatstate = self.Message()
    chatstate['chat_state'] = 'active'
    chatstate.send()

    # Retreive the roster so that the client can operate
    await self.get_roster()
    try:
      # Display options
      sigue = True
      while (sigue):
        response1 = input("""
        Ingresa la opción que desees:
        1. Mostrar usuarios conectados
        2. Mostrar contactos
        3. Agregar usuario a contactos
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
          # Iterate over client_roster to show user's contact list
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
          # Add a user to the contact list.
          userjid = input('Ingresa el JID de tu compa:\t')
          self.send_presence_subscription(pto=userjid)
          self.send_message(mto=userjid, mbody='Hola!', mtype='chat', mfrom=self.boundjid.bare)
        
        elif response1 == '4':
          # Show details of a contact
          userjid = input('Ingresa el JID de tu compa: \t')
          user = self.client_roster[userjid]
          self.client_roster.presence(userjid)
          print('Nombre: {}'.format(userjid))
          for client, status in self.client_roster.presence(userjid).items():
            if status['status']:
                print('Estado: {}'.format(status['status']))

        elif response1=='5':
          # Chat with a user, identified by JID
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

          # _chapuz_ to get the message in time.
          await self.get_roster()

        elif response1=='6':
          # Enter a group chat, identified by ROOM, ande define a NICKNAME
          room = input('Ingresa el JID del room al que deseas entrar: \t')
          nickname = input('Ingresa tu nickname: \t')
          self.plugin['xep_0045'].join_muc(room ,nickname)

        elif response1=='7':
          # Define a presence message.
          loop = True
          while(loop):
            print(
                """
                1. Disponible
                2. Fuera de Linea
                3. No molestar
                """
            )
            presence = input('Ingresa el numero del estado que quieras:\t')
            if presence == '1':
              presence_show = 'chat'
              status = 'Disponible'
              loop = False
            elif presence == '2':
              presence_show = 'away'
              status = 'Fuera de Linea'
              loop = False
            elif presence == '3':
              presence_show = 'dnd'
              status = 'No molestar'
              loop = False
            else:
              print('Opcion invalida')
          try:
            # Call send_presence method and pass the needed props
            self.send_presence(pshow=presence_show, pstatus=status)
            logging.info('Mensaje de presencia enviado: {}'.format(presence_show))
          except IqError:
            logging.error('Error al enviar presencia')
          except IqTimeout:
            logging.error('No hubo respuesta del servidor')
        elif response1=='8':
          pass
        elif response1=='9':
          # Delete my account
          self.connect()
          self.delete_account()
          self.disconnect()
          return None
        elif response1=='10':
          # Get the roster (this triggers the end of the event loop)
          await self.get_roster()
        elif response1=='11':
          # Exit
          self.send_presence(pshow='Desconectado', pstatus='away')
          sigue=False
          self.disconnect()
          return None
    except IqError as err:
      print('Error: %s' % err.iq['error']['condition'])
    except IqTimeout:
      print('Error: Request timed out')
    
  async def muc_message(self, msg):
    # Called when a room message is received,
    # automatically responds if user.JID is mentioned  

    # Show received message
    print('MESSAGE FROM {}: {}'.format(msg['from'], msg['body']))
    # Checks if the message is not sent by the bot itself
    if msg['mucnick'] != self.nick:
      self.send_message(mto=msg['from'].bare,
                        mbody=msg['body'],
                        mtype='groupchat')

  async def userRegister(self, event):
    # Called when a register event is triggered
    resp = self.Iq()
    resp['type'] = 'set'
    resp['register']['username'] = self.boundjid.user
    resp['register']['password'] = self.password

    try:
      # If success, print
        await resp.send()
        logging.info("Account created for %s!" % self.boundjid)
    except IqError as e:
        logging.error("Could not register account: %s" %
                      e.iq['error']['text'])
        self.disconnect()
    except IqTimeout:
        logging.error("No response from server.")
        self.disconnect()

  async def loginFail(self, event):
    # Called when login fails, event failed_auth triggered
    print('CREDENCIALES INCORRECTAS')
    self.disconnect()

  async def message(self, msg):
    # Called when a message is received, event message triggered
    # Show received message
    if msg['type'] in ('normal', 'chat'):
      print('\n{} *DICE*: {}\t'.format(msg['from'], msg['body']))

  def delete_account(self):
    # Delete account, called when user selects it in the menu.
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

    print("Cuenta eliminada con exito")
    self.disconnect() 
