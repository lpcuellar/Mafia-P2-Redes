##  Universidad del Valle de Guatemala
##  Redes
##  Proyecto 2

##  Creación de Mafia
##  Luis Pedro Cuéllar - 18220
##  Andrés Paiz - 191142
##  Pablo Coutino - 18817

import math
import random
import socket
import threading
import pickle
import os
import sys
import time

roles = {
    1:"Mafioso",
    2:"Civil",
    3:"Doctor",
    4:"Detective"
}

groups = {}

class Group:
    def __init__(self,admin,client):
        self.admin = admin

        self.clients = {}
        self.waitClients = {}
        self.clients[admin] = client

        self.allMembers = set()
        self.allMembers.add(admin)
        self.onlineMembers= set()
        self.deadMembers = {}

        self.offlineMessages = {}

        self.joinRequests = set()

        self.roles= {}
        self.rolesJugadores = []
        
        # self.deadMembers = {}
        #   0) nadie
        #   1) dia todos pueen hablar
        #   2) es noche mafia habla
        #   3) noche roles especiales

        self.daytime= 1

        self.mafiaCount =0
        self.civilCount =0
        self.detectiveCount=0
        self.timeLeft=90

    def countdown(self,t):
        #countdown(int(tiempo en segundos))
        while t:
            mins, secs = divmod(t, 60)
            timer = '{:02d}:{:02d}'.format(mins, secs)
        
            print(timer, end="\r")
        
            time.sleep(1)
            t -= 1
    def narrator(self):
        daytimeText = ""
        if(self.daytime==1):
            daytimeText= "DIA"
        elif(self.daytime==2):
            daytimeText ="NOCHE (Solo Mafiosos pueden hablar)"
        else:
            daytimeText ="NOCHE (Solo Detective puede ver)"
        state= "NARRADOR: AHORITA ES DE "+daytimeText +" \nHAY "+ str(self.mafiaCount) + " MAFIOSOS ," + str(self.civilCount) + " CIVILES , " + self.detectiveCount +" DETECTIVES" 
        for member in self.allMembers:
            self.clients[member].send(bytes(state,"utf-8"))


    def startGame(self):
        mafiaLeft= self.mafiaCount
        civiliansLeft= self.civilianCount
        detectivesLeft=self.detectiveCount
        self.daytime=1
        self.narrator()

    def asignRoles(self):
        mafiaCount= self.mafiaCount
        civilianCount= self.civilCount
        detectiveCount=self.detectiveCount        

        playersCount= len(self.allMembers)

        if(playersCount==4):
            mafiaCount=1
            civilianCount=2
            detectiveCount=1

        elif(playersCount==5):
            mafiaCount=1
            civilianCount=3
            detectiveCount=1
    
        elif(playersCount==2):
            mafiaCount=1
            civilianCount=1
            detectiveCount=0
        elif(playersCount==3):
            mafiaCount=1
            civilianCount=2
            detectiveCount=0

        elif(playersCount==6):
            mafiaCount=2
            civilianCount=3
            detectiveCount=1

        elif(playersCount==7):
            mafiaCount=2
            civilianCount=4
            detectiveCount=1

        elif(playersCount==8):
            mafiaCount=2
            civilianCount=4
            detectiveCount=2

        elif(playersCount==9):
            mafiaCount=2
            civilianCount=5
            detectiveCount=2

        else:
            mafiaCount=math.ceil(playersCount/4)
            detectiveCount=math.ceil(playersCount/6)
            civilianCount=playersCount-detectiveCount-mafiaCount
        
        print("THE DISTRIBUTION OF ROLES IS:")
        print(" MAFIA :" + str(mafiaCount))
        print(" DETECTIVE :" + str(detectiveCount))
        print(" CIVILS :" + str(civilianCount))
        
        pendingPlayers= []
        for member in self.allMembers:
            pendingPlayers.append(member)
        
        print("ASSIGNING MAFIA ")
        
        for j in range(0, mafiaCount):
            print("THE FOLLOWING IS GETTING ASSIGNED")
            
            nextPlayer =random.randint(0,len(pendingPlayers)-1)
            
            print(pendingPlayers[nextPlayer])
            
            self.rolesJugadores.append({"user":pendingPlayers[nextPlayer],"role":"MAFIA"})
            pendingPlayers.remove(pendingPlayers[nextPlayer])
        
        print("ASIGNANDO DETECTIVES")
        
        for j in range(0,detectiveCount):
            print("THE FOLLOWING IS GETTING ASSIGNED")
            
            nextPlayer =random.randint(0,len(pendingPlayers)-1)
            
            print(pendingPlayers[nextPlayer])
            
            self.rolesJugadores.append({"user":pendingPlayers[nextPlayer],"role":"DETECTIVE"})
            pendingPlayers.remove(pendingPlayers[nextPlayer])
            
            print(pendingPlayers)
        
        print("ASIGNANDO CIVILES")
        
        for j in range(0,civilianCount):
            print("THE FOLLOWING IS GETTING ASSIGNED")
        
            nextPlayer =random.randint(0,len(pendingPlayers)-1)
        
            print(pendingPlayers[nextPlayer])
        
            self.rolesJugadores.append({"user":pendingPlayers[nextPlayer],"role":"CIVIL"})
            pendingPlayers.remove(pendingPlayers[nextPlayer])
        
        print(self.rolesJugadores)

        print("SENDING MESSAGE")
        print(self.clients)

        for member in self.allMembers:
            for i in self.rolesJugadores:
                usr = ""
                rol = ""
                for key in i:
                    if key == "user":
                        usr = i[key]

                    elif key == "role":
                        rol = i[key]

                    else:
                        print("not found")
                
                if usr == member:
                    print("Le enviare un mensaje a "+str(usr)+ " diciendole que su rol es : " + str(rol))
                    self.clients[usr].send(bytes("Tu rol asignado es : " + str(rol),"utf-8"))

            # myrole = 
            # self.clients[member].send(bytes( "TU ROL ES : " + myrole,"utf-8"))
        self.civilianCount= civilianCount
        self.mafiaCount= mafiaCount
        self.detectiveCount=detectiveCount
        self.startGame()

    def disconnect(self,username):
        self.onlineMembers.remove(username)
        del self.clients[username]

    def connect(self,username,client):
        self.onlineMembers.add(username)
        self.clients[username] = client
        
        print("NEW USER CONENCTED")
        
        for member in self.onlineMembers:
            print(str(member))
            
    def sendMessage(self,message,username):
        for member in self.allMembers:
            if member != username:
                self.clients[member].send(bytes(username + ": " + message,"utf-8"))

def pyconChat(client, username, roomname):
    while True:
        msg = client.recv(1024).decode("utf-8")
        
        if msg == "/viewRequests":
            client.send(b"/viewRequests")
            client.recv(1024).decode("utf-8")
        
            if username == groups[roomname].admin:
                client.send(b"/sendingData")
                client.recv(1024)
                client.send(pickle.dumps(groups[roomname].joinRequests))
        
            else:
                client.send(b"You're not an admin.")
        
        elif msg == "/approveRequest":
            client.send(b"/approveRequest")
            client.recv(1024).decode("utf-8")
        
            if username == groups[roomname].admin:
                client.send(b"/proceed")
                usernameToApprove = client.recv(1024).decode("utf-8")
        
                if usernameToApprove in groups[roomname].joinRequests:
                    groups[roomname].joinRequests.remove(usernameToApprove)
                    groups[roomname].allMembers.add(usernameToApprove)
        
                    if usernameToApprove in groups[roomname].waitClients:
                        groups[roomname].waitClients[usernameToApprove].send(b"/accepted")
                        groups[roomname].connect(usernameToApprove,groups[roomname].waitClients[usernameToApprove])
                        del groups[roomname].waitClients[usernameToApprove]
        
                    print("Member Approved:",usernameToApprove,"| Group:",roomname)
        
                    client.send(b"User has been added to the group.")
        
                else:
                    client.send(b"The user has not requested to join.")
        
            else:
                client.send(b"You're not an admin.")
        
        elif msg == "/disconnect":
            client.send(b"/disconnect")
            client.recv(1024).decode("utf-8")
            groups[roomname].disconnect(username)
        
            print("User Disconnected:",username,"| Group:",roomname)
        
            break
        
        elif msg == "/messageSend":
            client.send(b"/messageSend")
            message = client.recv(1024).decode("utf-8")
            groups[roomname].sendMessage(message,username)
        
        elif msg == "/waitDisconnect":
            client.send(b"/waitDisconnect")
            del groups[roomname].waitClients[username]
        
            print("Waiting Client:",username,"Disconnected")
        
            break
        
        elif msg == "/allMembers":
            client.send(b"/allMembers")
            client.recv(1024).decode("utf-8")
            client.send(pickle.dumps(groups[roomname].allMembers))
        
        elif msg == "/startGame":
            ##client.send(b"/startGame")
            print("CLIENT REQUESTED TO START THE GAME")
            ##revisar si hay minimo cupo
        
            numberOfPlayers =len(groups[roomname].allMembers)
            print("El numero de jugadores en la sala es: {}".format(numberOfPlayers))
        
            if(numberOfPlayers >= 2):
                groups[roomname].asignRoles()
                client.send(b"/startGame")
                message = client.recv(1024).decode("utf-8")
        
            else:
                client.send(b"/insufficientPlayers")
                message = client.recv(1024).decode("utf-8")
        
            client.recv(1024).decode("utf-8")

        elif msg == " ":
            pass

        else:
            print("UNIDENTIFIED COMMAND:",msg)
            




def handshake(client):
    username = client.recv(1024).decode("utf-8")
    client.send(b"/sendroomname")
    roomname = client.recv(1024).decode("utf-8")
    
    if roomname in groups:
        if username in groups[roomname].allMembers:
            groups[roomname].connect(username,client)
            client.send(b"/ready")
    
            print("User Connected:",username,"| Group:",roomname)
    
        else:
            groups[roomname].joinRequests.add(username)
            groups[roomname].waitClients[username] = client
            groups[roomname].sendMessage(username+" has requested to join the group.","PyconChat")
            client.send(b"/wait")
    
            print("Join Request:",username,"| Group:",roomname)
    
        threading.Thread(target=pyconChat, args=(client, username, roomname,)).start()
    
    else:
        groups[roomname] = Group(username,client)
        threading.Thread(target=pyconChat, args=(client, username, roomname,)).start()
        client.send(b"/adminReady")
    
        print("New Group:",roomname,"| Admin:",username)

def main():
    if len(sys.argv) < 3:
        print("USAGE: python server.py <IP> <Port>")
        print("EXAMPLE: python server.py localhost 8000")
        return
    
    listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listenSocket.bind((sys.argv[1], int(sys.argv[2])))
    listenSocket.listen(10)
    
    print("PyconChat Server running")
    
    while True:
        client,_ = listenSocket.accept()
        threading.Thread(target=handshake, args=(client,)).start()

if __name__ == "__main__":
    main()
