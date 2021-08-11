import logging
from getpass import getpass
from argparse import ArgumentParser
from EchoBot import EchoBot
import slixmpp
from client import Client

if __name__ == '__main__':
  parser = ArgumentParser(description=Client.__doc__)

  parser.add_argument("-d", "--debug", help="set logging to DEBUG",
                    action="store_const", dest="loglevel",
                    const=logging.DEBUG, default=logging.INFO)
  # Setup logging.
  args = parser.parse_args()
  logging.basicConfig(level=args.loglevel,
                      format='%(levelname)-8s %(message)s')
  print("""
    \t\t\tMENU
    Bienvenido a tu cliente XMPP favorito, ingresa el numero de la opcion que desees:
    1. Iniciar sesion con una cuenta existente
    2. Crear una nueva cuenta
    3. Eliminar una cuenta del servidor
  """)

  respuesta = input('')

  if respuesta=='1':
      jid = input('Ingresa tu JID:\t\n')
      password = input('ingresa tu contrasena:\t\n')
      user = Client(jid, password)
      # user = Client('marco@alumchat.xyz', '12345')
      user.connect()
      user.process()

  elif respuesta=='2':
      jid = input('Ingresa tu JID:\t\n')
      password = input('ingresa tu contrasena:\t\n')
      xmpp = Client(jid, password)
      # xmpp = Client('marco@alumchat.xyz', '12345')
      xmpp.register_plugin('xep_0030')
      xmpp.register_plugin('xep_0004')
      xmpp.register_plugin('xep_0199')
      xmpp.register_plugin('xep_0066')
      xmpp.register_plugin('xep_0077')
      xmpp['xep_0077'].force_registration = True
      xmpp.connect()
      xmpp.process()
      # xmpp.plugin['xep_0077'].make_registration_form
  elif respuesta=='3':
      jid = input('Ingresa el JID de la cuenta a eliminar:\t\n')
