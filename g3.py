#

import socket, sys, pygame, threading, time, pcapy
from struct import *
pygame.init()
running = True
bg = (210,210,240)


size = width, height = 768,768
cell = 3
clock = pygame.time.Clock()
screen = pygame.display.set_mode(size)
pygame.display.set_caption("G3!")
screen.fill((255,255,255))
pygame.draw.rect(screen,bg,(0,0,cell*4,cell*256),0)

#create an INET, STREAMing socket


# receive a packet

def putDot(threadn,location, color, size):
	# print color
	div = divmod(location,256)
	div = tuple([cell*x for x in div])
	DURATION = 2.0 # seconds
	ratio = 0.0 # alpha as a float [0.0 .. 1.0]

	pygame.draw.rect(screen,color,(div[0],div[1],cell,cell),0)
	time.sleep(2)
	if location <= 1024:
		color2 = (210,210,240)
	else:
		color2 = (255,255,255)
	pygame.draw.rect(screen,color2,(div[0],div[1],cell,cell),0)


def parse(packet):
	eth_length = 14
	dest_port = 0
	eth_header = packet[:eth_length]
	eth = unpack('!6s6sH' , eth_header)
	eth_protocol = socket.ntohs(eth[2])
	if eth_protocol == 8 :
		ip_header = packet[eth_length:20+eth_length]
		iph = unpack('!BBHHHBBH4s4s' , ip_header)
		version_ihl = iph[0]
		version = version_ihl >> 4
		ihl = version_ihl & 0xF
 
		iph_length = ihl * 4
		protocol = iph[6]
		if protocol == 6 :
			t = iph_length + eth_length
			tcp_header = packet[t:t+20]
 
			#now unpack them :)
			tcph = unpack('!HHLLBBHHH' , tcp_header)
			dest_port = tcph[1]
		elif protocol == 17 :
			u = iph_length + eth_length
			udph_length = 8
			udp_header = packet[u:u+8]
 
			#now unpack them :)
			udph = unpack('!HHHH' , udp_header)
			dest_port = udph[1]
		if dest_port:
			color = (0,0,0)
			if dest_port <= 1024:
				color = (255,0,0)
			t = threading.Thread(target=putDot, args = ("1",dest_port, color, size))
			t.start()	



cap = pcapy.open_live("eth0", 65536, 1, 0)

while running:

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
				exit()
	
	(header, packet) = cap.next()
	parse(packet)
	
	pygame.display.flip()
	# clock.tick(10)

