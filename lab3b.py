import csv

#SUPERBLOCK
#GROUP
#BFREE - same format as inode, each index is block number and have 0 if free and 1 if not
#IFREE - same as above
#DIRENT - dictionary with key as parent inode and values as the rest of the DIRENT entry
#INODE - dictionary with key as inode number and values as the rest of the dirent entry
#INDIRECT - dictionary with key as parent inode and values as the rest of the INDIRECT entry

BLOCKSIZE = 1024	
referenced = []

def createArrays(fs):
	superblock = []
	group = []
	bfree = [1]*BLOCKSIZE #initialize an array of ones, default is not free
	ifree = [1]*BLOCKSIZE #initialize an array of ones, default is not free
	dirent = {}
	indirect = {}
	inode = {}
	
	
	for row in fs:
		type = row[0] 	#identifies whether this row is for SUPERBLOCK, GROUP, BFREE, etc
		if row[0]=='SUPERBLOCK':
			superblock = row[1:len(row)]	#store everything after SUPERBLOCK into array
		elif type=='GROUP':
			group = row[1:len(row)]
		elif type=='BFREE':
			bfree[int(row[1])] = 0 #mark items on bfree list as free (0)
		elif type=='IFREE':
			ifree[int(row[1])] = 0 #mark items on ifree list as free (0)
		elif type=='DIRENT':
			if int(row[1]) in dirent.keys():	#if already an existent key, append
				dirent[int(row[1])].append(row[2:len(row)])
			else:								#else start a new nested list
				dirent[int(row[1])] = [row[2:len(row)]]
		elif type=='INODE':
			inode[int(row[1])] = row[2:len(row)] #add all inode info to the inode index that it's referred to
		elif type=='INDIRECT':
			if int(row[1]) in indirect.keys():	#if already an existent key, append
				indirect[int(row[1])].append(row[2:len(row)])
			else:								#else start a new nested list
				indirect[int(row[1])] = [row[2:len(row)]]
			
	return superblock, group, bfree, ifree, inode, dirent, indirect
		

	
def invalidBlockHelper(inode, superblock, group):
	# First Check for Invalid INODES
	s = ''
	lastInodeBlk = group[7] + ((superblock[3]*superblock[1])/superblock[2]) 
	for key in inode.keys():
		# only check if valid inode num, valid mode number, and greater than zero link count
		if inode[key] > 0 and inode[key][2] > 0 and inode[key][5] > 0:		

			for j in range(12,26):
				if inode[key][j] <= 0 or inode[key][j] > superblock[4]: #invalid block
					if j == 24:
						print('INVALID INDIRECT BLOCK ', inode[key][j], ' IN INODE ', inode[key], 'AT OFFSET ', j-12)  
					elif j == 25:
						print('INVALID DOUBLE INDIRECT BLOCK ', inode[key][j], ' IN INODE ', inode[key], 'AT OFFSET ', j-12)  	
					elif j == 26:
						print('INVALID TRIPPLE INDIRECT BLOCK ', inode[key][j], ' IN INODE ', inode[key], 'AT OFFSET ', j-12)  	
					else:
						print('INVALID BLOCK ', inode[key][j], ' IN INODE ', inode[key], 'AT OFFSET ', j-12)  
				elif inode[key][j] < lastInodeBlk : #reserved block
					if j == 24:
						print('RESERVED INDIRECT BLOCK ', inode[key][j], 'IN INODE ', inode[key], 'AT OFFSET ' j-12)
					elif j == 25:
						print('RESERVED DOUBLE INDIRECT BLOCK ', inode[key][j], 'IN INODE ', inode[key], 'AT OFFSET ' j-12)
					elif j == 26:
						print('RESERVED TRIPPLE INDIRECT BLOCK ', inode[key][j], 'IN INODE ', inode[key], 'AT OFFSET ' j-12)
					else:
						print('RESERVED BLOCK ', inode[key][j], 'IN INODE ', inode[key], 'AT OFFSET ' j-12)
				else: #mark block for duplicate (maybe create a new array with markers per block) 
				 	if inode[key][j] in referenced:
				 		print('DUPLICATE ', 'BLOCK ', inode[key][j], 'IN INODE ', inode[key], 'AT OFFSET ', j-12)
				 	else:
				 		referenced.append(blockNum)
				 		
		else: #inode block itself has error -- how to handle???
			print('INVALID BLOCK ', inode[key], ' IN INODE ', inode[key], 'AT OFFSET ???')  
	

	for key in indirect.keys():
		if indirect[key] > 0:	
			if indirect[key][3] <= 0 or indirect[key][3] > superblock[4]:
				if indirect[key][1] == 1:
					print('INVALID BLOCK ', indirect[key][3], ' IN INODE ', indirect[key], 'AT OFFSET ', indirect[2])
				elif indirect[key][1] == 2:
					print('INVALID INDIRECT BLOCK ', indirect[key][3], ' IN INODE ', indirect[key], 'AT OFFSET ', indirect[2])
				else:				
					print('INVALID DOUBLE INDIRECT BLOCK ', indirect[key][3], ' IN INODE ', indirect[key], 'AT OFFSET ', indirect[2])
			elif indirect[key][3] <= lastInodeBlk:
				if indirect[key][1] == 1:
					print('RESERVED BLOCK ', indirect[key][3], 'IN INODE ', inode[key], 'AT OFFSET ', indirect[2])
				elif indirect[key][1] == 2:
					print('RESERVED INDIRECT BLOCK ', indirect[key][3], 'IN INODE ', inode[key], 'AT OFFSET ', indirect[2])
				else:
					print('RESERVED DOUBLE INDIRECT BLOCK ', indirect[key][3], 'IN INODE ', inode[key], 'AT OFFSET ', indirect[2])
			
		else:  # what error message do we output here? for later

	for key in dirent.keys():
		if dirent[key] > 0 and inode[key][] > 0:
			
		else:
			

if __name__=="__main__":

    #-----------open file----------------------
    with open('trivial.csv', newline="") as filesysCSV:
    	filesysReader = csv.reader(filesysCSV, delimiter=',')
    	filesys = list(filesysReader) #<---- the main data structure that stores everything in a list of lists
    	
    #----------read everything into lists and lists of lists----------
    superblock, group, bfree, ifree, inode, dirent, indirect = createArrays(filesys)
    
    #invalidBlockHelper(inode);  #examine every blk pointer in: i-node, direct blk, single, double, tripple indirect    
    # for this we will loop through EVERY inode, and check all of its blk pointers 
    # errors here will be either INVALID BLOCK or RESERVED (meaning that the blk number is in one of the SUPER, GROUP, IFREE, BFREE, and INODE TABLE areas)	
    invalidBlockHelper(inode, superblock);


