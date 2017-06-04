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
	for key in inode.keys():
		# only check if valid inode num, valid mode number, and greater than zero link count
		if inode[key] > 0 and inode[key][2] > 0 and inode[key][5] > 0:		

			for j in range(13,27):
				if inode[key][j] < 0 or inode[key][j] > superblock[6]: #invalid block
					print('INVALID BLOCK ', inode[key][j], ' IN INODE ', inode[key], 'AT OFFSET ???')  
				elif inode[key][j] <= group[8]: #reserved block
					print('RESERVED BLOCK ', inode[key][j], 'IN INODE ', inode[key], 'AT OFFSET ???')
				else: #mark block for duplicate (maybe create a new array with markers per block) 
				 	if inode[key][j] in referenced:
				 		print('DUPLICATE ', 'BLOCK ', inode[key][j], 'IN INODE ', inode[key], 'AT OFFSET ???')
				 	else:
				 		referenced.append(blockNum)
				 		
		else: #inode block itself has error -- how to handle???
			print('INVALID BLOCK ', inode[key], ' IN INODE ', inode[key], 'AT OFFSET ???')  
	
	for key in dirent.keys():
		if dirent[key] > 0:
			
			
	


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


