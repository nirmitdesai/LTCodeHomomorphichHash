#!/usr/bin/env python

import random,time,datetime,hashlib,sys
from math import ceil
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor,task
import struct,json

requestId=''
host=()

def soliton(N, seed):
  prng = random.Random()
  prng.seed(seed)
  while 1:
    x = random.random() # Uniform values in [0, 1)
    i = int(ceil(1/x))       # Modified soliton distribution
    yield i if i <= N else 1 

def lt_encode(source, blocksize=2):
  print "blocksize = ",blocksize
  prng = random.Random()
  n = len(source)
  N = int(ceil(n*1.0/blocksize))
  print "File size = ",n
  print "Number of Blocks in the file = ",N
  s = soliton(N, prng.randint(0, 2 ** 32 - 1))

  while 1:
    d = next(s)
    seed = prng.randint(0, 2 ** 32 - 1)
    rng  = random.Random(seed)
    r = bytearray(blocksize)
  

    for k in rng.sample(range(N), d):
          
      offset = k*blocksize
      j      = 0
      end    = min(offset + blocksize, n)
      while offset < end:
	charToSend = source[offset]
	
	'''if random.randint(0,1) and charToSend=='a':
		#charToSend='u'
    		print "=="*30
		print """

                Sending Corrupt Block!!


                The character 'a' appearing at some places in file 
                is sent as character 'u'


                """
      		print "=="*30 '''         
        r[j] ^= ord(charToSend)
        offset += 1
        j      += 1
    packingVal=">i"+"q"+str(blocksize)+"s"

    st=struct.Struct(packingVal)
    print("stuct packed")
    print "d = ",d,"seed = ",seed
    values=[d,seed,str(r)]
   # print " values = ",values
    pd=st.pack(*values)
   # stuff = json.dumps(values)
    print "len of pd = ",len(pd)
    yield pd

class EchoClientDatagramProtocol(DatagramProtocol):
    noOfmessages=2  
    st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    seederDict = {}
    with open(sys.argv[1], 'rb') as f:
        buf = f.read()
	
    if len(buf) > 7168:
    	fountain=lt_encode(buf,7168)
    else:
	fountain=lt_encode(buf,len(buf)/4)
    
    

    def startProtocol(self):
        #self.transport.connect('54.244.65.114', 6969)
	#self.transport.write("seed", ('54.244.65.114', 6969) )
	#st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
	#FileToSeed = "Test123.txt"
  	filePath = sys.argv[1]
  	FileToSeed = filePath[filePath.rfind("/")+1:]

	self.transport.write("s"+"|"+self.st+"|"+FileToSeed, ('54.214.173.224', 6969))
  	print "=="*30
  	print "Sending information to tracker to seed a file ",FileToSeed
	print "=="*30
    def sendDatagram(self,host):
	
	 print "Host = ",host
         self.transport.write(next(self.fountain) ,('54.214.173.224', 6969))
        

    def datagramReceived(self, datagram, host):
	print "datagram receivde = ",datagram," from host = ",host
       
        if len(datagram.split("|")) == 1:  
            if self.noOfmessages == 2:
              	
            	(requestId, filename) = json.loads(datagram)
                print "=="*30
                print "Recieved a requestID for seeding the file ",filename, " for any Leecher who requests"
                print "=="*30
            	self.seederDict[filename] = requestId
                print "requestId ",requestId
            	self.noOfmessages-=1
            if datagram == "ok":
              	print "=="*30
            	print "Hash verified!!"
                print "Seeder and Leecher are now Authenticated, File transfering process has started!! "
                print "=="*30
          	l=task.LoopingCall(self.sendDatagram,host)
                l.start(0.5)
        
        elif datagram.split("|")[0] == "request" and self.noOfmessages == 1:
           self.noOfmessages-=1
           print "=="*30
           print "Recieved request from Leecher at ",host," for requestId"
           print "=="*30
           requestId = self.seederDict[datagram.split("|")[1]]
           m=hashlib.md5()
           m.update(requestId+self.st)
           self.transport.write(m.digest(),('54.214.173.224', 6969)) 

	if datagram=="done":
    		print "=="*30
		print """"

	            Reciever has successfully decoded the file!!

	            Stop transfers and ending connection with peer

	            """
     		print "=="*30       
		self.f.close()
		reactor.stop()
	
def main():

    protocol = EchoClientDatagramProtocol()
    t = reactor.listenUDP(8000, protocol)

    reactor.run()

if __name__ == '__main__':
    main()
