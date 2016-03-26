#!/usr/bin/env python

import random,time,datetime,hashlib,sys , socket
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import struct
import bitarray
import json
from math import ceil
''' assume the file contains 'abcdefg\n' 
    ab-->block 1, cd-->block 2, ef-->block 3 , g\n-->block4
'''

class EchoUDP(DatagramProtocol):
	noOfmessages=2
	requestId=''
	seederTimestamp=''
	data = bytearray()
        edges={}	
	blocksize=0
	noOfBlocks=0				
        
	#This holds hash of abcdefg\n , abcd , efg\n,ab,cd,ef,g\n 
	hashTree=[]

	piece0Decoded=False
	piece1Decoded=False

	def startProtocol(self):
		print "=="*30
		print "Leecer now active!!"
		print "=="*30
		st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
		#fileName = "Test123.txt"			# Read from .torrentFile
        	#self.transport.connect('54.244.65.114', 6969)
        	filePath = sys.argv[1]
		filePath = filePath[:filePath.rfind(".")]
		fileName = filePath[filePath.rfind("/")+1:]	
		trackerUrl = ""
		self.transport.write("l"+"|"+st+"|"+fileName,('127.0.0.1', 6969))
		print "=="*30
		print "Sending information to tracker to leech a file ",fileName
		print "=="*30
		with open(sys.argv[1]) as f:
			self.noOfBlocks = f.readline()
			self.noOfBlocks = int( self.noOfBlocks.rstrip('\n'))
			self.blocksize = f.readline()
			self.blocksize = int( self.blocksize.rstrip('\n'))
			self.data = bytearray(self.noOfBlocks)
			print "=="*30
			print "No of Blocks in the file= ",self.noOfBlocks
			print "--"*30
			print "Blocksize to read = ",self.blocksize
			trackerUrl = f.readline()
			print "--"*30
			print "URL of Amazon EC2 tracker = ",trackerUrl
			print "--"*30
			self.hashTree = json.loads(f.readline())
			print "--"*30
			print "HashTree = ",self.hashTree
			print "=="*30

	def hashOf(self,stuff):
	    ascii=[ord(i) for i in stuff]
	    summed = sum(ascii)
	    temp = summed %257
     	    return (47**temp) %1543

	def checkHomomorphicHash(self,start,N,hashIndex,level=1):
		
		val1 = int(ceil((N-start)*1.0/2))
		val2 = N-start-val1

		firstHalfInEdges = True
		secondHalfInEdges = True
		
		print "Start = ",start," val1 = ",val1, "val2 = ",val2," hashindex=",hashIndex,"level = ",level
	    	
		for i in range(start,start+val1):
			if not (i,) in self.edges:
				firstHalfInEdges = False
	
	    	for i in range(start+val1, start+val1+val2):
			if not (i,) in self.edges:
				secondHalfInEdges = False

		if level==1 and self.piece0Decoded:
			firstHalfInEdges = False

		if level==1 and self.piece1Decoded:
			secondHalfInEdges = False

	    	if firstHalfInEdges:
			 tempMsg =""
			 for i in range(start,start+val1):
				print "len of message =",len((self.edges[(i,)])) 
				tempMsg += (self.edges[(i,)])
			 print "=="*30
			 print "\n"
			 #print " First half of the message receieved= ",tempMsg 
			 print "\n"
			 print "=="*30
			 m=hashlib.md5()
			 m.update(tempMsg)
			 print "hashindex being compared to (1) = ",hashIndex
			 if self.hashOf(list(m.digest())) == self.hashTree[hashIndex]:
			 	if level==1:
			 		print "=="*30
			 		print "\n"
					print """


							Homomorphic Hash of piece 0 verified!!

							Start receiving Second half of the message

							"""
					print "\n"
			 		print "=="*30		
					self.piece0Decoded = True
				else:
					print "=="*30
			 		print "\n"
					print "Homomorphic hash of block is correct"
					print "\n"
			 		print "=="*30	
			 else:
				if val1!=1:
					self.checkHomomorphicHash(0,val1,hashIndex+2,level+1)
				else:
					#delete the keys

			 		print "=="*30	
			 		print "\n"
					print "dictionary keys = ",self.edges.keys()
			 		print "Updating local HashTree for part1 verification! \n"
					del self.edges[(start,)]
	
		if secondHalfInEdges:
			temp1Msg = ""
			print "temp1msg second half made from ",
			for i in range(start+val1,min(start+val1+val2,N)):
				print i,
				temp1Msg += (self.edges[(i,)])
			
			print "len of temp1msg = ",len(temp1Msg)
			print "now stripping for possiuble null characters"
			temp1Msg = temp1Msg.rstrip('\0')
			print "post stripping , len of temp1msg = ",len(temp1Msg)
			print
			#print "secondHalf message = ",temp1Msg 
			m=hashlib.md5()
			m.update(temp1Msg)
			print "hashindex being compared to (2) = ",hashIndex+1
			if self.hashOf(list(m.digest())) == self.hashTree[hashIndex+1]:
				print "=="*30	
			 	print "\n"
				if level==1:
					print "Homomorphic hash of piece 1 verified!"	
					self.piece1Decoded = True
				else:
					print "Homomorphic hash of block(2) is correct"
				print "\n"
				print "=="*30
			else:
				print "=="*30	
			 	print "\n"
				print "dictionary keys 2 = ",self.edges.keys()
			 	print "Updating local HashTree for part 2 verification! \n"
				if val2!=1:
					self.checkHomomorphicHash(start+val1,start+val1+val2,hashIndex+4,level+1)
				else:
					del self.edges[(start+val1,)]
					

        def processStuff(self,degree,seed,data):
            rng = random.Random(seed)
            print "=="*30
            print "Data was formed by xoring blocks "
	    #print "self.noOfBlocks = ", self.noOfBlocks
            tempListOfBlocks = rng.sample(range(self.noOfBlocks), degree)
	    tempListOfBlocks.sort()
	    tupleOfBlocks = tuple(tempListOfBlocks)
	    print tupleOfBlocks				
                       
            if len(self.edges)==0:
                self.edges[tupleOfBlocks]=data
	  
	    elif tupleOfBlocks in self.edges: pass		

	    else :
		listOfKeys= self.edges.keys()
		listOfKeys.sort(key=len)
		decodedData=bytearray(data)
		if len(tupleOfBlocks)==1:
			self.edges[tupleOfBlocks]=data
		for keys in listOfKeys:
			if len(keys) > len(tupleOfBlocks) and set(tupleOfBlocks).issubset(set(keys)):
				q=set(keys).difference(set(tupleOfBlocks))
				v=set(tupleOfBlocks).intersection(set(keys))
				if tuple(v) not in self.edges.keys():
					self.edges[tuple(v)]=data
				tupleOfBlocks=tuple(q)
	             		for i in range(self.blocksize):
					decodedData[i]=decodedData[i]^ bytearray(self.edges[keys])[i]
				if not tuple(q) in self.edges.keys():
					self.edges[tuple(q)]=str(decodedData)
	             		del self.edges[keys]

			elif (len(keys) < len(tupleOfBlocks)) and set(keys).issubset(set(tupleOfBlocks)):
				q=set(tupleOfBlocks).difference(set(keys))
				tupleOfBlocks=tuple(q)
	             		for i in range(self.blocksize):
					decodedData[i]=decodedData[i]^ bytearray(self.edges[keys])[i]
				if not tuple(q) in self.edges.keys():
					self.edges[tuple(q)]=str(decodedData)
			elif len(keys) == len(tupleOfBlocks):
				pass
		if not tupleOfBlocks in self.edges:
			self.edges[tupleOfBlocks]=str(decodedData)

	        
		self.checkHomomorphicHash(0,self.noOfBlocks,1)
	    
            
        def writeToFile(self):
		f=open('1yoLTcode.pdf','w')
		for keys in self.edges.keys():
			if len(keys)==1:
				print "Keys generated= ",keys
				k = (self.edges[keys]).rstrip('\0')
				f.seek(self.blocksize*keys[0],0)
				f.write(k)
		f.close() 
		  

   	def datagramReceived(self, datagram, address):
		#print "Datagram received and len of datagram = ",len(datagram)
		#print "Address", address	
		if self.noOfmessages == 2:
			self.noOfmessages-=1
			print "--"*30
			print "Leecher requests Seeder for requestId"
			print "--"*30
			(requestId,seederTimestamp,seederIP,fileName) = json.loads(datagram)
			self.seederTimestamp = str(seederTimestamp)
			self.requestId = str(requestId)
			sendSeederRequest = "request|"+fileName
			#print "seederIP", seederIP
			ipPort = tuple(seederIP) #unicode ip here!!
			#print "ipPort ",ipPort
			#(ipPort,) = ipPort
			ipPort = tuple(ipPort)
			(ip,port)= ipPort
			host = (str(ip),port)
			#print "HOSTTTT ",host
			self.transport.write(sendSeederRequest,('127.0.0.1', 6969))
			print "--"*30
			print "Request sent to seeder at ",host
			print "--"*30

		elif self.noOfmessages ==1:
			hashReceived = datagram
			self.noOfmessages-=1
			print "--"*30
			print "RequestId ",self.requestId, " and SeederTimestamp",self.seederTimestamp
			print "--"*30
			m=hashlib.md5()
			m.update(self.requestId+self.seederTimestamp)
			if hashReceived == m.digest():
				print "--"*30
				print "Hash matched!!, now sending Confirmation to Seeder for File Transfer"
				print "--"*30
			else: 
				print "--"*30
				print "No match!!!"
				print "--"*30
			self.transport.write("ok",('127.0.0.1', 6969))					
		else:
			
			structFormat = "i"+"q"+str(self.blocksize)+"s"
    			s = struct.Struct(structFormat)
    			unpacked_data = s.unpack(datagram)
    			degree,seed,self.data = unpacked_data
                	print "Degree = ", degree, "Seed = ", seed
    			self.processStuff(degree,seed,self.data)
			counter=0
			for keys in self.edges.keys():
				if len(keys)==1:
					counter=counter+1
			print "dictionary = ",self.edges.keys()
			print "counter value = ", counter
			if counter== self.noOfBlocks:
				print "All blocks successfully decoded"
				self.writeToFile()
				self.transport.write("done",('127.0.0.1', 6969))
				reactor.stop()
	
def main():
    # this was in original code. If i put this file on server and in client did sendto(serverIP,6969) it worked.
    reactor.listenUDP(6970, EchoUDP()) # are you sure about the () after EchoUDP? yes look here
    reactor.run()

if __name__ == '__main__':
    main()
