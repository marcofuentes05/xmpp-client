# About

The purpose of this project is to implement a simple XMPP client that is capable of sending and receiving messages, files and updates from users and contacts. The project was made using Python3.7.0 and the `sliXMPP` library.

### Project Functionalities
- [x] Register a new account
- [x] Log in with an existing account
- [x] Log out of a current session
- [x] Delete account from server
- [x] Retreive user's contact list
- [x] Show user details
- [x] 1 on 1 chat
- [ ] Group Chat
- [x] Send Presence Stanzas
- [ ] Send/Receive Files

## Difficulties
The main difficulty in developing this project was definetively the lack of documentation on `sliXMPP`'s website. It made the whole process longer.

## Lessons Learned
- I learned how to implement a client that follows a generally known protocol.
- How to handle asynchronous events in python.

# Requirements

This project requires the following modules:
- Python3.7.0
- sliXMPP
- aiohttp

# Configuration

To install dependencies, run
```
pip3 install sliXMPP
```

Make sure to be connected to a secure and reliable internet provider (**unlike** Claro Guatemala)

