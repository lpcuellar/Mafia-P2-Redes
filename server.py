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

narrator_state = """
¡¡COMENZAMOS CON EL JUEGO!!

NARRADOR: 
    AHORITA ES DE {0}
    HAY {1} MAFIOSO(S) --- {2} CIVIL(ES) --- {3} DETECTIVE(S)

"""

mafia_night_message = """

La noche en donde solo los de la MAFIA está empezando.
Tienen 1 minuto para elegir una víctima.

"""

detective_night_message = """

La noche en donde solo los DETECTIVES está empezando.
Tienen 1 minuto para elegir un jugador para ver su carta.

"""

discussion_message = """

Empieza el periodo de discusión.
Tienen 1 minuto para elegir si matan a un jugador o no.

"""

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
        self.deadMembers = []

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
        self.votes=[{'user':'cl2','vote':'cl1'},{'user':'cl3','vote':'cl1'},{'user':'cl1','vote':'cl2'}]
        self.votesAgainst=[]
        self.start = False

    def send_broadcast(self, message):
        for member in self.allMembers:
            self.clients[member].send(bytes(message,"utf-8"))
    
    #borra todos los votos almacenados
    def clearVotes(self):
        print("VOTES ANTES:")
        print(self.votes)
        
        for j in range(0, len(self.votes))  :
            self.votes.remove(self.votes[0])

        print("VOTES DESPUES:")
        print(self.votes)



    ##Revisa si ese usuario ya habia votado y si si, lo remplaza.
    def addVote(self,username,target):
        newvote= {'user':username,'vote':target}
        print("tu nuevo voto es :" +str(newvote))
        test=newvote['user']
        replacement=False
        if(len(self.votes)>0):
            listo =False
            for vote in self.votes:
                print(vote)
                if vote['user']  == newvote['user']:
                    print("Encontre un voto de "+ test)
                    self.votes.remove(vote)
                    self.votes.append(newvote)
                    replacement=True                        
            if(replacement==False):
                self.votes.append(newvote)

        else:
            self.votes.append(newvote)
        print(self.votes)


    ## metodo usado para restar de la partida a un usuario
    def killUser(self,username):
        for role in self.rolesJugadores:
            if(role['user']==username):
                if(role['role']==1):
                    self.civiliansLeft-=1
                    self.deadMembers.append(username)
                elif(role['role']==2):
                    self.mafiaLeft-=1
                    self.deadMembers.append(username)
                elif(role['role']==3):
                    self.detectivesLeft-=1
                    self.deadMembers.append(username)



    ## Una vez hecha la votacion, se hace un recuento de los votos de todos los usuarios vivos

    def countVotes(self):
        for user in self.allMembers:
            self.votesAgainst.append({'user':user,'votes':0})

        print(self.votesAgainst)

        for user in self.allMembers:
            for vote in self.votes:
                if vote['vote'] == user:
                    print("Encontre un voto en contra de " + user)
                    for x in self.votesAgainst:
                        if(x['user']==user):
                            res=x['votes']
                            x['votes']=res+1

        print(self.votesAgainst)


        localmax=0
        deaduser=""
        for element in self.votesAgainst:
            if(element['votes']>localmax):
                localmax=element['votes']
                deaduser=element['user']
        print("El maximo de votos es de" +str(localmax))
        print("El votado preliminarmente es :"+ deaduser)
        for element in self.votesAgainst:
            if(element['votes']==localmax and element['user']!=deaduser):
                print("Hay un empate. nadie muere")
                localmax=0
                deaduser=""

        print("El maximo de votos es de " +str(localmax))
        print("El votado preliminarmente es :"+ deaduser)
        if(deaduser==""):
            pass
        else:
            killUser(deaduser)






    def countdown(self,t):
        #countdown(int(tiempo en segundos))
        while t:
            mins, secs = divmod(t, 60)
            timer = '{:02d}:{:02d}'.format(mins, secs)
        
            print(timer, end="\r")
        
            time.sleep(1)
            t -= 1
   

   ##Busca la lista de usuasrios conectados y les asigna un rol aleatoriamente
    def asignRoles(self):
        print("\nASSIGNING ROLES FOR THE PLAYERS")

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
        
        print("\nTHE DISTRIBUTION OF ROLES IS:")
        print(" MAFIA :" + str(mafiaCount))
        print(" DETECTIVE :" + str(detectiveCount))
        print(" CIVILS :" + str(civilianCount))
        
        pendingPlayers= []
        for member in self.allMembers:
            pendingPlayers.append(member)
        
        print("\nASSIGNING MAFIA ")
        
        for j in range(0, mafiaCount):
            print("THE FOLLOWING PLAYERS ARE MAFIA:")
            
            nextPlayer =random.randint(0,len(pendingPlayers)-1)
            
            print(pendingPlayers[nextPlayer])
            
            self.rolesJugadores.append({"user":pendingPlayers[nextPlayer],"role":"MAFIA"})
            pendingPlayers.remove(pendingPlayers[nextPlayer])
        
        print("\nASSIGNING DETECTIVES")
        
        for j in range(0,detectiveCount):
            print("THE FOLLOWING PLAYERS ARE DETECTIVES:")
            
            nextPlayer =random.randint(0,len(pendingPlayers)-1)
            
            print(pendingPlayers[nextPlayer])
            
            self.rolesJugadores.append({"user":pendingPlayers[nextPlayer],"role":"DETECTIVE"})
            pendingPlayers.remove(pendingPlayers[nextPlayer])
            
            print(pendingPlayers)
        
        print("\nASSIGNING CIVILS")
        
        for j in range(0,civilianCount):
            print("THE FOLLOWING PLAYERS ARE CIVILS:")
        
            nextPlayer =random.randint(0,len(pendingPlayers)-1)
        
            print(pendingPlayers[nextPlayer])
        
            self.rolesJugadores.append({"user":pendingPlayers[nextPlayer],"role":"CIVIL"})
            pendingPlayers.remove(pendingPlayers[nextPlayer])
        
        print("\nTHE ROLES ASSIGNED ARE THE FOLLOWING:")

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
                    print("El usuario: "+ str(usr) + " tiene el role : " + str(rol))
                    self.clients[member].send(bytes("Tu rol asignado es : {0}".format(str(rol)),"utf-8"))

        self.civilCount= civilianCount
        self.mafiaCount= mafiaCount
        self.detectiveCount=detectiveCount

    def moment(self, daytime):
        if daytime == 0 and self.isFirstDay == False:
            print("\nTHE DISUSSION PERIOD IS STARTING")
        
            self.send_broadcast(discussion_message)

        elif daytime == 1:
            print("\nTHE NIGHT WERE ONLY THE MAFIA IS ACTIVE IS STARTING")
        
            send_broadcast(mafia_night_message)

        elif daytime == 2:
            print("\nTHE NIGHT WERE ONLY THE DETECTIVES ARE ACTIVE IS STARTING")
        
            self.send_broadcast(detective_night_message)
        
        else:
            print("Unknown moment :( ")

    def narrator(self):
        print("\nNARRATOR FASE STARTING")

        daytimeText = ""
        state = ""
        
        if ((self.daytime % 3) == 0):
            daytimeText= "DIA"
            state = narrator_state.format(str(daytimeText), str(self.mafiaCount), str(self.civilCount), str(self.detectiveCount))

            print(state)
            
            if self.isFirstDay:
                self.send_broadcast(state)

            else:
                self.send_broadcast(state)

                self.isFirstDay = False
                self.moment(self.daytime)


        elif ((self.daytime % 3) == 1):
            daytimeText ="NOCHE (Solo Mafiosos pueden hablar)"
            state = narrator_state.format(str(daytimeText), str(self.mafiaCount), str(self.civilCount), str(self.detectiveCount))

            print(state)

            self.send_broadcast(state)
            self.moment(self.daytime)
        
        elif ((self.daytime % 3) == 2):
            daytimeText ="NOCHE (Solo Detective puede ver)"
            state = narrator_state.format(str(daytimeText), str(self.mafiaCount), str(self.civilCount), str(self.detectiveCount))

            print(state)

            self.send_broadcast(state)
            self.moment(self.daytime)

        else:
            print("UNKNOWN DAY STATE")


    # Registra en el servidor el estaod en el que estan.

    def printState():
        print("MAFIOSOS LEFT: " + str(mafiaCount))
        print ("DEtectives LEFT:"+ str(detectiveCount))
        print("Cviviles Left :"+str(civiliansLeft))
        if(state == 0):
            print("ES DE NOCHE. LE TOCA VOTAR A LOS MAFIOSOS ")
        elif (state==1):
            print("ES DE NOCHE. LE TOCA ACTUAR AL DETECTIVE")
        elif (state ==2):
            print("ES DE DIA . LE TOCA VOTAR A LOS CIVILES")
        print   ("VOTOS REALIZADOS: "+ str  (len(votes)))


    def gameplay(self):

        while self.mafiaLeft>0:
            if( state == 0):
                clearVotes()
                printState()
                while (len(self.votes)< self.mafiaLeft):
                    print("AUN FLATAN VOTOS")
                    
                
                printState()
                countVotes()
                printState()
                state=2
    
            # elif( state == 1):
            #     printState()
            #     x = input("Presione x para ver una carta civil")
            #     if (x== "x"):
            #     state=2


            elif (state == 2):
                clearVotes()
                printState()
                while (len(votes)< self.mafiaLeft+self.civiliansLeft+self.detectivesLeft):
                    print("Faltan votos")
            
                printState()
                countVotes()
                printState()
                state=0



        printState()



    def startGame(self):
        print("\nCLIENT REQUESTED TO START THE GAME")
        self.start=True
        self.asignRoles()

        mafiaLeft = self.mafiaCount
        civiliansLeft = self.civilCount
        detectivesLeft = self.detectiveCount
        
        self.isFirstDay = True
        self.daytime = 0
        self.narrator()
        self.clearVotes()
        self.gameplay()

    def disconnect(self,username):
        self.onlineMembers.remove(username)
        del self.clients[username]

    def connect(self,username,client):
        self.onlineMembers.add(username)
        self.clients[username] = client
        
        print("\n***NEW USER CONENCTED***\n")
        
        for member in self.onlineMembers:
            print(str(member))
            
    def sendMessage(self,message,username):
        #para que los juagadore muertos no puedan enviar mensajes
        print("RECIBI ESTE MENSAJE :"+ message + " DE : "+ username + " ... RETRASNMITIENDO...")
        if(username in self.deadMembers):
            print("Mensaje no enviado porque este usuario esta muerto")
        else:
            for member in self.allMembers:
                if member != username:
                    self.clients[member].send(bytes(username + ": " + message,"utf-8"))


##MAnejo de recepcion de mensjaes co nocodigos especificos  del lado del servidor
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
        
        elif msg =="/vote":
            client.send(b"/requestVote")
            client.recv(1024).decode("utf-8")
            print(groups[roomname].deadMembers)
            print(username)
            ##para restringir votaciones a cuando el juego ya inicio
            if(groups[roomname].start==True):
                if username in groups[roomname].deadMembers:
                    print("Voto bloqueado porque ese usuario esta muerto")
                
                else:
                    # print("Este usuario le pidio al servidor votar: "+ username)
                    client.send(b"/nowVote")
                    usernameToKill = client.recv(1024).decode("utf-8")
                    print("Y le pidio que matara a "+usernameToKill)
                    groups[roomname].addVote(username,usernameToKill)
                    client.send(b"Vote submitted")
            else:
                print("Voto bloqueado porque no ha iniciado el juego")
                client.send(b"No es momento de votar")

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
            numberOfPlayers =len(groups[roomname].allMembers)
            print("\nEl numero de jugadores en la sala es: {}".format(numberOfPlayers))
        
            if(numberOfPlayers >= 2):
                groups[roomname].startGame()
                #groups[roomname].countVotes()
                client.send(b"/startGame")
                #message = client.recv(1024).decode("utf-8")
        
            else:
                client.send(b"/insufficientPlayers")
                #message = client.recv(1024).decode("utf-8")
        
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
            groups[roomname].sendMessage("\n"+ username +" has requested to join the group.","PyconChat")
            client.send(b"/wait")
    
            print("Join Request:",username,"| Group:",roomname)
    
        threading.Thread(target=pyconChat, args=(client, username, roomname,)).start()
    
    else:
        groups[roomname] = Group(username,client)
        threading.Thread(target=pyconChat, args=(client, username, roomname,)).start()
        client.send(b"/adminReady")
    
        print("\n***New Group:",roomname,"| Admin:",username, "***\n")

def main():
    if len(sys.argv) < 3:
        print("\nUSAGE: python server.py <IP> <Port>")
        print("EXAMPLE: python server.py localhost 8000")
        return
    
    listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listenSocket.bind((sys.argv[1], int(sys.argv[2])))
    listenSocket.listen(10)
    
    print("\nPyconChat Server running")
    
    while True:
        client,_ = listenSocket.accept()
        threading.Thread(target=handshake, args=(client,)).start()

if __name__ == "__main__":
    main()
