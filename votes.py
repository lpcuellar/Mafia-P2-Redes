votes= []
votesagainst=[]
#[{user:"cl1",vote:"cl2"},{user:"cl2",vote:"cl1"}]
users=["cl1","cl2","cl3","cl4"]
votes.append({'user':"cl1",'vote':"cl2"})
votes.append({'user':"cl2",'vote':"cl3"})
votes.append({'user':"cl3",'vote':"cl2"})
votes.append({'user':"cl4",'vote':"cl3"})
print(votes)



state = 0
start = False
civiliansLeft = 2
mafiaCount = 1
detectiveCount = 1


def addVote(newvote, test):
	replacement=False
	if len(votes)>0:
		for vote in votes:
			print(vote)
			if vote['user']  == newvote['user']:
				print("Encontre un voto de "+ test)
				votes.remove(vote)
				votes.append(newvote)
				replacement=True
		if(replacement==False):
			votes.append(newvote)
	else:
		votes.append(newvote)


def countVotes():
	print(votes)
	for user in users:
		votesagainst.append({'user':user,'votes':0})

	print(votesagainst)

	for user in users:
		for vote in votes:
			if vote['vote'] == user:
				print("Encontre un voto en contra de " + user)
				for x in votesagainst:
					if(x['user']==user):
						res=x['votes']
						x['votes']=res+1

	print(votesagainst)


	localmax=0
	deaduser=""
	for element in votesagainst:
		if(element['votes']>localmax):
			localmax=element['votes']
			deaduser=element['user']
	print("El maximo de votos es de" +str(localmax))
	print("El votado preliminarmente es :"+ deaduser)
	for element in votesagainst:
		if(element['votes']==localmax and element['user']!=deaduser):
			print("Hay un empate. nadie muere")
			localmax=0
			deaduser=""

	print("El maximo de votos es de " +str(localmax))
	print("El votado preliminarmente es :"+ deaduser)



newvote= {'user':"cl4",'vote':"cl2"}
test=newvote['user']

#addVote(newvote, test)

countVotes()

##0 noche mafia; 1 detective ; 2 dia


def clearVotes():
	votes=[]
	votesagainst=[]


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

clearVotes()

def revisaridentidad(user):
	pass




while mafiaCount>0:
	if( state == 0):
		printState()
		clearVotes()
		while (len(votes)< mafiaCount):
			x = input("Presione x para matar a un civil")
			if (x== "x"):
				newvote= {'user':"cl4",'vote':"cl2"}
				test=newvote['user']
				addVote	(newvote,test)
		state=1
		civiliansLeft-=1
	
	elif( state == 1):
		printState()
		x = input("Presione x para ver una carta civil")
		if (x== "x"):
			state=2


	elif (state == 2):
		printState()
		clearVotes()
		while (len(votes)< mafiaCount+civiliansLeft+detectiveCount):
			x = input("Presione x para matar a alguien")
			if (x== "x"):
				newvote= {'user':"cl4",'vote':"cl2"}
				test=newvote['user']
				addVote	(newvote,test)
		state=0
		mafiaCount-=1



printState()
