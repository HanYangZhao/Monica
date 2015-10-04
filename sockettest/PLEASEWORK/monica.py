import pyaudio, sys, socket, wave

port = 3003
chunk = 16
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

wf = wave.open('piano2.wav', 'rb')
chnls = wf.getnchannels();
samp = wf.getsampwidth();
frame = wf.getframerate();
nframes = wf.getnframes();
print chnls, samp, frame, nframes


#p = pyaudio.PyAudio()
#stream = p.open(format=wf.get_format_from_width(wf.getsampwidth()),
#                channels=wf.getnchannels(),
#                rate=wf.getframerate(),
 #               output=True)

#data = wf.readframes(chunk)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create the socket
print "created socket"
server_socket.bind(('', port)) # listen on port 5000
print "listening?"
server_socket.listen(5) # queue max 5 connections
client_socket, address = server_socket.accept()

print "Your IP address is: ", socket.gethostbyname(socket.gethostname())
print "Server Waiting for client on port ", port

while True:

    # test string
    #data = bytearray('DEADBEEF'.decode('hex'))
    #client_socket.sendall(data)
    
   try:
        #print len(wf.readframes(chunk))
        client_socket.sendall(wf.readframes(chunk))
   except IOError,e:
      if e[1] == pyaudio.paInputOverflowed: 
         print e 
         x = '\x00'*16*256*2 #value*format*chunk*nb_channels 

print "still listening"
stream.stop_stream()
stream.close()
socket.close()
p.terminate()