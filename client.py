##  Universidad del Valle de Guatemala
##  Redes
##  Proyecto 2

##  Creación de Mafia
##  Luis Pedro Cuéllar - 18220
##  Andrés Paiz - 191142
##  Pablo Coutino - 18817

import socket
import threading
import pickle
import sys

ascii_art = """
******************************************************************************************************
*                                                                                                    *
*        __  ______    _____________       _________    ____  ____     _________    __  _________    *
*       /  |/  /   |  / ____/  _/   |     / ____/   |  / __ \/ __ \   / ____/   |  /  |/  / ____/    *
*      / /|_/ / /| | / /_   / // /| |    / /   / /| | / /_/ / / / /  / / __/ /| | / /|_/ / __/       *
*     / /  / / ___ |/ __/ _/ // ___ |   / /___/ ___ |/ _, _/ /_/ /  / /_/ / ___ |/ /  / / /___       *
*    /_/  /_/_/  |_/_/   /___/_/  |_|   \____/_/  |_/_/ |_/_____/   \____/_/  |_/_/  /_/_____/       *
*                                                                                                    *
******************************************************************************************************                                                                                            
"""
instrucciones = " Instrucciones: \n\n Como se Gana? \n\n Mafia debe de intentar matar a todos los civiles, ya sea votando o matandolos en la noches mientras que los civiles deben de descubrir quien es mafia y votarlos durante el dia \n\n Cuales son los Roles? \n\n Normalmente existen muchos roles pero en este caso jugaremos con mafia, civiles y detective. \n\n Que hacer si es mafia? \n\n Los mafia deben de tratar hacerse pasar como civiles durante el dia y eliminar a un jugador por medio de una votacion durante la noche \n\n Que hacer si es detective? \n\n Si se es detective, durante la noche puede investigar a un jugador de su eleccion para descubrir si es civil o mafia. \n\n Que hacer si es civil? \n\n Los civiles deben de intentar descubrir quien es mafia durante el dia para asi votar para eliminarlos \n\n Que pasa si hay un empate en las votaciones? \n\n Si durante cualquiera de los dos procesos de votacion existe un empate no sucede nada"
menu = """

Available Commands:
    /1 -> READ INSTRUCTIONS
    /2 -> Approve Join Requests (Admin)
    /3 -> Disconnect
    /4 -> View All Members
    /5 -> Start GAME
    /vote -> To vote (only allowed during game)    
    
Type anything else to send a message: """

state = {}


def serverListen(serverSocket):
    while True:
        msg = serverSocket.recv(1024).decode("utf-8")
        if msg == "/viewRequests":
            serverSocket.send(bytes(".","utf-8"))
            response = serverSocket.recv(1024).decode("utf-8")
            if response == "/sendingData":
                serverSocket.send(b"/readyForData")
                data = pickle.loads(serverSocket.recv(1024))
                if data == set():
                    print("No pending requests.")
                else:
                    print("Pending Requests:")
                    for element in data:
                        print(element)
            else:
                print(response)
        ##para que el admin pueda aceptar gente en la sala de espera
        elif msg == "/approveRequest":
            serverSocket.send(bytes(".","utf-8"))
            response = serverSocket.recv(1024).decode("utf-8")
            if response == "/proceed":
                state["inputMessage"] = False
                print("Please enter the username to approve: ")
                with state["inputCondition"]:
                    state["inputCondition"].wait()
                state["inputMessage"] = True
                serverSocket.send(bytes(state["userInput"],"utf-8"))
                print(serverSocket.recv(1024).decode("utf-8"))
            else:
                print(response)
        ##Para hacer votos en contra de usuarios
        elif msg =="/requestVote":
            serverSocket.send(bytes(".","utf-8"))
            response = serverSocket.recv(1024).decode("utf-8")

            print(response)
            if (response == "/nowVote"):
                print("El servidor me autoriza votar")
                state["inputMessage"] = False
                print("Please enter the username you want to kill: ")
                with state["inputCondition"]:
                    state["inputCondition"].wait()
                state["inputMessage"] = True
                print("lo que le enviare al server es :" + str(state["userInput"]))
                serverSocket.send(bytes(state["userInput"],"utf-8"))
                print(serverSocket.recv(1024).decode("utf-8"))
            else:
                print(response)

        elif msg == "/disconnect":
            serverSocket.send(bytes(".","utf-8"))
            state["alive"] = False
            break
        elif msg == "/messageSend":
            serverSocket.send(bytes(state["userInput"],"utf-8"))
            state["sendMessageLock"].release()
        elif msg == "/allMembers":
            serverSocket.send(bytes(".","utf-8"))
            data = pickle.loads(serverSocket.recv(1024))
            print("All Room Members:")
            for element in data:
                print(element)
        elif msg == "/startGame":
            print("EL SERVIDOR DICE QUE INICIE EL JUEGO")
            serverSocket.send(bytes(state["userInput"],"utf-8"))
            state["sendMessageLock"].release()
            # response = serverSocket.recv(1024).decode("utf-8")
        elif msg == "/insufficientPlayers":
            print("EL SERVIDOR DICE QUE NO HAY SUFICIENTES JUGADORES CONNECTADOS")
            state["sendMessageLock"].release()
            #response = serverSocket.recv(1024).decode("utf-8")

        else:
            print(msg)

##Revisar si el cliente ingresa un comando especial
def userInput(serverSocket):
    while state["alive"]:
        state["sendMessageLock"].acquire()
        state["userInput"] = input(">>>")
        state["sendMessageLock"].release()
        with state["inputCondition"]:
            state["inputCondition"].notify()
        if state["userInput"] == "/1":
            print(instrucciones)
        elif state["userInput"] == "/2":
            serverSocket.send(b"/approveRequest")
        elif state["userInput"] == "/3":
            serverSocket.send(b"/disconnect")
            break
        elif state["userInput"] == "/4":
            serverSocket.send(b"/onlineMembers")
        elif state["userInput"] == "/5":
            state["sendMessageLock"].acquire()
            serverSocket.send(b"/startGame")
        elif state["userInput"] == "/vote":
            #state["sendMessageLock"].acquire()
            serverSocket.send(b"/vote")
        elif state["inputMessage"]:
            state["sendMessageLock"].acquire()
            serverSocket.send(b"/messageSend")

def waitServerListen(serverSocket):
    while not state["alive"]:
        msg = serverSocket.recv(1024).decode("utf-8")
        if msg == "/accepted":
            state["alive"] = True
        
            print("Ud ha sido aceptado a la sala solicitada")
            serverSocket.send(b".")
        
            break
        
        elif msg == "/waitDisconnect":
            state["joinDisconnect"] = True
            break

def waitUserInput(serverSocket):
    while not state["alive"]:
        state["userInput"] = input(">>>")
        if state["userInput"] == "/3" and not state["alive"]:
            serverSocket.send(b"/waitDisconnect")
            break

def main():
    if len(sys.argv) < 3:
        print("USAGE: python client.py <IP> <Port>")
        print("EXAMPLE: python client.py localhost 8000")
    
        return
    
    serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    serverSocket.connect((sys.argv[1], int(sys.argv[2])))
    
    state["inputCondition"] = threading.Condition()
    state["sendMessageLock"] = threading.Lock()
    
    print(ascii_art)
    print("WELCOME TO MAFIA CARD GAME!")
    
    state["username"] = input("Ingrese su nombre de usuario: ")
    state["roomname"] = input("Ingrese el nombre de la sala: ")
    state["alive"] = False
    state["joinDisconnect"] = False
    state["inputMessage"] = True
    
    serverSocket.send(bytes(state["username"],"utf-8"))
    serverSocket.recv(1024)
    
    serverSocket.send(bytes(state["roomname"],"utf-8"))
    response = serverSocket.recv(1024).decode("utf-8")
    
    if response == "/adminReady":
        print("Se creo la sala ",state["roomname"]," y ud. es el admin.")
    
        state["alive"] = True
    
    elif response == "/ready":
        print("Ud se ha unido a la sala : ",state["roomname"])
    
        state["alive"] = True
    
    elif response == "/wait":
        print("ud esta en la sala de espera...")
        ##print("Available Commands:\n/1 -> Disconnect\n")
    
    waitUserInputThread = threading.Thread(target=waitUserInput,args=(serverSocket,))
    waitServerListenThread = threading.Thread(target=waitServerListen,args=(serverSocket,))
    
    userInputThread = threading.Thread(target=userInput,args=(serverSocket,))
    serverListenThread = threading.Thread(target=serverListen,args=(serverSocket,))
    
    waitUserInputThread.start()
    waitServerListenThread.start()
    
    while True:
        if state["alive"] or state["joinDisconnect"]:
            break
    
    if state["alive"]:
        print(menu)
    
        waitUserInputThread.join()
        waitServerListenThread.join()
        
        userInputThread.start()
        serverListenThread.start()
    
    while True:
    
        if state["joinDisconnect"]:
            serverSocket.shutdown(socket.SHUT_RDWR)
            serverSocket.close()
            
            waitUserInputThread.join()
            waitServerListenThread.join()
    
            print("Disconnected from PyconChat.")
    
            break
    
        elif not state["alive"]:
            serverSocket.shutdown(socket.SHUT_RDWR)
            serverSocket.close()
            
            userInputThread.join()
            serverListenThread.join()
    
            print("Disconnected from PyconChat.")
    
            break

if __name__ == "__main__":
	main()
