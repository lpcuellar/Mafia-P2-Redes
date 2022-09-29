import random
import math

roles = {1:"Mafioso",2:"Civil",3:"Doctor",4:"Detective"}


members =[]
roles= {1:"CIVIL", 2:"MAFIA", 3:"VIDENTE"}
deadMembers = {}
rolesjugadores = []

mafiaCount=0
civilianCount=0
detectiveCount=0
 
# members.append("jugador1")
# members.append("jugador2")
# members.append("jugador3")
# members.append("jugador4")

##crear lista de usuarios random 
x= range(25)
for i  in x:
	members.append("jugador"+str(i))



print(members)
playersCount =len(members)
if(playersCount==4):
	mafiaCount=1
	civilianCount=3
	detectiveCount=0
elif(playersCount==5):
	mafiaCount=1
	civilianCount=3
	detectiveCount=1
elif(playersCount==6):
	mafiaCount=2
	civilianCount=3
	detectiveCount=1
elif(playersCount==7):
	mafiaCount=2
	civilianCount=4
	detectiveCount=1
elif(playersCount==8):
	mafiaCount=3
	civilianCount=4
	detectiveCount=1
elif(playersCount==9):
	mafiaCount=3
	civilianCount=5
	detectiveCount=1
else:
	mafiaCount=math.ceil(playersCount/4)
	detectiveCount=math.ceil(playersCount/6)
	civilianCount=playersCount-detectiveCount-mafiaCount

print("LA DISTRIBUCION SERIA:")
print("MAFIOSOS :" + str(mafiaCount))
print("VIDENTES :" + str(detectiveCount))
print("CIVILES :" + str(civilianCount))
pendingPlayers= members  
print("ASIGNANDO MAFIOSOS")
for j in range(0,mafiaCount):
	print("EL SIGUIENTE A SER ASIGNADO")
	nextPlayer =random.randint(0,len(pendingPlayers)-1)
	print(pendingPlayers[nextPlayer])
	rolesjugadores.append({"user":pendingPlayers[nextPlayer],"role":2})
	pendingPlayers.remove(pendingPlayers[nextPlayer])
print("ASIGNANDO DETECTIVES")
for j in range(0,detectiveCount):
	print("EL SIGUIENTE A SER ASIGNADO")
	nextPlayer =random.randint(0,len(pendingPlayers)-1)
	print(pendingPlayers[nextPlayer])
	rolesjugadores.append({"user":pendingPlayers[nextPlayer],"role":3})
	pendingPlayers.remove(pendingPlayers[nextPlayer])
print(pendingPlayers)
print("ASIGNANDO CIVILES")
for j in range(0,civilianCount):
	print("EL SIGUIENTE A SER ASIGNADO")
	nextPlayer =random.randint(0,len(pendingPlayers)-1)
	print(pendingPlayers[nextPlayer])
	rolesjugadores.append({"user":pendingPlayers[nextPlayer],"role":1})
	pendingPlayers.remove(pendingPlayers[nextPlayer])
print(rolesjugadores)