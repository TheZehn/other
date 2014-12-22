import pygame, time, pcapy, threading
from struct import *
from impacket import ImpactDecoder, ImpactPacket

#set the 
grid_size = 32 #numbers of rows and columns
width = 30 #cell width
height = 20 #cell height
margin = 1 #cell margin


#set some colors
BLACK = ( 0, 0, 0)
WHITE = ( 255, 255, 255)
RED = ( 255, 0, 0)

#set up the initial grid
grid = []
for row in range(grid_size):
	grid.append([])
	for column in range(grid_size):
		grid[row].append((0,0))

pygame.init()

size = [(width+margin)*grid_size,(height+margin)*grid_size]
screen = pygame.display.set_mode(size)
screen.fill(BLACK)

pygame.display.set_caption("1024")

done = False

my_ip = ["10.42.0.37","127.0.0.1","176.16.55.1","176.16.251.1"]

cap = pcapy.open_live("eth0", 65535, 1, 0)
cap.setfilter("ip proto \\tcp")

def ageColor(oldcolor,time_diff):
	aftercolor = ()
	for hue in oldcolor:
		temp_col = hue+time_diff*25
		if temp_col >= 250:
			temp_col = 255
		aftercolor = aftercolor + (temp_col,)
	return aftercolor if aftercolor else oldcolor
		# if aftercolor:
		# 	boxcolor = aftercolor
		# 	return 

def checkGrid():

	for row in range(grid_size):
		for column in range(grid_size):
			boxcolor = WHITE
			texthue = (100,100,100)
			dest_addr, when_set = grid[row][column]

			if  when_set > 0:
				if dest_addr in my_ip:
					boxcolor = RED
				else:
					boxcolor = BLACK
				texthue = WHITE
				
				time_diff = time.time() - when_set
				boxcolor = ageColor(boxcolor,time_diff)
				
			if sum(boxcolor) == 765:
				grid[row][column] = (0,0)
			location = [(margin+width)*column+margin,(margin+height)*row+margin,width,height]
			pygame.draw.rect(screen,boxcolor,location)
			myfont = pygame.font.SysFont("default", 16)
			label = myfont.render(str((row)*grid_size+(column)), 1, texthue)
			fontplace = tuple(location)				
			screen.blit(label, fontplace)
		pygame.display.flip()

def getPacket():
	(header, packet) = cap.next()
	decoder = ImpactDecoder.EthDecoder()
	eth = decoder.decode(packet)

	ip=eth.child()  #internet layer
	trans=ip.child() #transport layer
	d_addr = ip.get_ip_dst()
	if ip.get_ip_p() == 6:
		dest_port = trans.get_th_dport()
	elif ip.get_ip_p() == 17:
		dest_port = trans.get_uh_dport()
	else:
		print ip.get_ip_p()


	
	if dest_port <= grid_size**2:
		print "port:",dest_port
		place_row,place_column = divmod(dest_port,grid_size)

		grid[place_row][place_column] = (d_addr,time.time()) #remove div[1] by one, 'cause grid starts at zero
# t = threading.Thread(target=checkGrid(), args = ())
# t.start()
while not done:
	pygame.display.flip()
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			done = True
	

	getPacket()

	checkGrid()
	# else:
	# 	print s_addr," > ",d_addr, dest_port

	

pygame.quit()
