# VideoSync
Kadir Ersoy, Muhammet Sen

## Description
VideoSync is a screen sharing application that allows a host to share their screen with clients on the LAN. It uses a server-client architecture where server, the host, takes screen recording and distributes it to clients. Clients, on the other hand, receive the screen recording and display it on their screen. Main challenge is to keep the clients in sync with each other. 

## How to Run
### Server
Server is the host that shares its screen with clients. It is run by executing the following command:
```
python main.py server
```
We have a config file that contains node name, node type(server/client), video configuration information etc. Server is required to have name = "server" in the config file.
### Client
Client is the application that receives the screen recording from the server and displays it on the screen. It is run by executing the following command:
```
python main.py
```

Client is required to have name = "cX" in the config file, where X is the client number. You can have multiple clients with different client numbers.

---

Video resolution and FPS can be modified in the config file, in order to adapt to the network conditions and hardware capabilities.