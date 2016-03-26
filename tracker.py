#!/usr/bin/env python

import random
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import json



class EchoUDP(DatagramProtocol):

	    
        seederLeecherDict = { } 
	seederInfo={}
	leecherInfo={}
	seederInfo["timestamp"]=[]
	leecherInfo["timestamp"]=[]
	seederInfo["socket"]=[]
	leecherInfo["socket"]=[]
	seederInfo["fileName"] = []
	leecherInfo["fileName"] = []
	seederLeecherDict["s"]=seederInfo
	seederLeecherDict["l"]=leecherInfo
       
	
	def formatting(self,msg,b4newlines,afterNewLines):
		for i in range(b4newlines):
			print
		print msg
		for i in range(afterNewLines):
			print

	def startProtocol(self):
		print '-'*80
		self.formatting(">Tracker is running",2,1)
		print '-'*80

   	def datagramReceived(self, datagram, address):

	
		#leecher is at 6970
		#seeder is at 8000
		logFile=open('log.txt','a')


		
		if datagram[0] =="s" or datagram[0] == "l":
			(ip,port) = address
			(Usertype,TimeStamp,fileName) = datagram.split("|")
			if(datagram[0] == "s"):
				print
				print "Request from Seeder. "+ '\n' + '\t' + "Seeder i/p: " + ip + '\n' + '\t' + "File: " + fileName + '\n' + '\t' + "TimeStamp: " + TimeStamp +'\n'
				logFile.write("Request from Seeder. "+ '\n' + '\t' + "Seeder i/p: " + ip + '\n' + '\t' + "File: " + fileName + '\n' + '\t' + "TimeStamp: " + TimeStamp +'\n')
				print
			else:
				print
				print "Request from Leecher. "+ '\n' + '\t' + "Leecher i/p: " + ip + '\n' + '\t' + "File: " + fileName + '\n' + '\t' + "TimeStamp: " + TimeStamp +'\n'
				logFile.write("Request from Leecher. "+ '\n' + '\t' + "Leecher i/p: " + ip + '\n' + '\t' + "File: " + fileName + '\n' + '\t' + "TimeStamp: " + TimeStamp +'\n')
				print
			print "-"*80			
			self.seederLeecherDict[Usertype]["fileName"].append(fileName)
			self.seederLeecherDict[Usertype]["socket"].append(address)
			self.seederLeecherDict[Usertype]["timestamp"].append(TimeStamp)

			print "-"*80
			if fileName not in self.seederLeecherDict["l"]["fileName"]:
				print
				print ">No leecher yet.Seeder must wait."
				print
				print "-"*80
		
			if fileName not in self.seederLeecherDict["s"]["fileName"]:
				print
				print ">No seeder available.Leecher must wait."
				print
				print "-"*80		
		
			if fileName in self.seederLeecherDict["l"]["fileName"] and fileName in self.seederLeecherDict["s"]["fileName"]:
				SeederIndex = self.seederLeecherDict['s']['fileName'].index(fileName)
				LeecherIndex = self.seederLeecherDict['l']['fileName'].index(fileName)
				requestId ='RiD'+ self.seederLeecherDict['s']['socket'][SeederIndex][0][:6] +  self.seederLeecherDict['s']['socket'][SeederIndex][0][6:] #should be 'l'
				sendToLeecher = json.dumps((requestId,self.seederLeecherDict['s']['timestamp'][SeederIndex],self.seederLeecherDict['s']['socket'][SeederIndex],fileName))
				print
				print ">RequestId : ", requestId
				print
				print "-"*80
				print "Tracker to Leecher - " + '\n' + '\t' + "RequestID: " + requestId + '\n' + '\t' + "Seeder's TimeStamp: " + self.seederLeecherDict['s']['timestamp'][SeederIndex] + '\n' + '\t' + "File: " + fileName + '\n'
				logFile.write("Tracker to Leecher - " + '\n' + '\t' + "RequestID: " + requestId + '\n' + '\t' + "Seeder's TimeStamp: " + self.seederLeecherDict['s']['timestamp'][SeederIndex] + '\n' + '\t' + "File: " + fileName + '\n') 
				self.transport.write(sendToLeecher, self.seederLeecherDict['l']['socket'][LeecherIndex])
				print "Tracker to Seeder - " + '\n' + '\t' + "RequestID: " + requestId + '\n' + '\t' + "File: " + fileName + '\n' + "=="*30
				sendToSeeder = json.dumps((requestId,fileName))
				logFile.write("Tracker to Seeder - " + '\n' + '\t' + "RequestID: " + requestId + '\n' + '\t' + "File: " + fileName + '\n' + "=="*30 + '\n')
				self.transport.write(sendToSeeder, self.seederLeecherDict['s']['socket'][SeederIndex])
	
				print "--"*80
				print "dictionary = ",self.seederLeecherDict


		else:
			print "datagram = ",datagram,"from ",address ,"is being tunnelled",
			if address in self.seederLeecherDict['s']['socket']:
				print "to", self.seederLeecherDict['l']['socket']
				self.transport.write(datagram , self.seederLeecherDict['l']['socket'][0])
			else:
				print "to", self.seederLeecherDict['s']['socket']
				self.transport.write(datagram , self.seederLeecherDict['s']['socket'][0])
				
			
def main():
    reactor.listenUDP(6969, EchoUDP())
    reactor.run()
   
if __name__ == '__main__':
    main()
