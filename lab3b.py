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
possibleValidBlocks = []


def generateAllBlocks(last_inode_block):
	block_num = int(last_inode_block)
	max_blocks = int(superblock[0])
	allBlocks = []
	for i in range(int(last_inode_block), max_blocks):
		allBlocks.append(block_num)
		block_num += 1
	return allBlocks

def createArrays(fs):
	superblock = []
	group = []
	bfree = []
	ifree = []
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
			bfree.append(int(row[1])) #add inode number onto bfree list
		elif type=='IFREE':
			ifree.append(int(row[1])) #add inode number onto ifree list
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
		

	
def blockConsistencyHelper(inode, superblock, group):
	# First Check for Invalid INODES
	s = ''
	lastInodeBlk = int(group[7]) + ((int(superblock[3])*int(superblock[1]))/int(superblock[2]) )

	for key in inode.keys():
		# only check if valid inode num, valid mode number, and greater than zero link count
		if int(key) > 0 and int(inode[key][1]) > 0 and int(inode[key][4]) > 0:		

			for j in range(10,25):
				#print('key ', key, 'iblock num ', j, 'address ', inode[key][j]) 	#for debugging - DELETE
				
				if j == 22:		#get type of block for stdout
					blockType = 'INDIRECT '
				elif j == 23:
					blockType = 'DOUBLE INDIRECT '
				elif j == 24:
					blockType = 'TRIPPLE INDIRECT '	
				else:
					blockType = ''
					
				if int(inode[key][j]) <= 0 or int(inode[key][j]) > int(superblock[0]): #invalid block
					print('INVALID ', blockType, 'BLOCK ', inode[key][j], ' IN INODE ', key, ' AT OFFSET ', j-10, sep="")  
				
				elif int(inode[key][j]) < lastInodeBlk : #reserved block
					print('RESERVED ', blockType, 'BLOCK ', inode[key][j], ' IN INODE ', key, ' AT OFFSET', j-10, sep="")
				
				else: #mark block as visited or duplicate (maybe create a new array with markers per block) 
				 	if inode[key][j] in referenced:
				 		print('DUPLICATE ', blockType, 'BLOCK ', inode[key][j], ' IN INODE ', key, ' AT OFFSET', j-10, sep="")
				 	else:
				 		referenced.append(int(inode[key][j]))
				 		
		else: #inode block itself has error -- how to handle???
			print('INVALID BLOCK ', inode[key], ' IN INODE ', inode[key], ' AT OFFSET ???', sep="")  
	

	for key in indirect.keys():
		for j in range(0,len(indirect[key])):
			if int(key) > 0:
				if int(indirect[key][j][1])==1:
					blockType = 'INDIRECT '
				elif indirect[key][j][1] == 2:
					blockType = 'DOUBLE INDIRECT '
				elif indirect[key][j][1] == 3:
					continue #<----redundant case already checked in iblock 14
				else:
					blockType = ''
					
				if int(indirect[key][j][3]) <= 0 or int(indirect[key][j][3]) > int(superblock[0]):				
					print('INVALID ', blockType, 'BLOCK ', indirect[key][j][3], ' IN INODE ', key, 'AT OFFSET ', indirect[key][j][1], sep="")
				elif int(indirect[key][j][3]) <= lastInodeBlk:
					print('RESERVED ', blockType, 'BLOCK ', indirect[key][j][3], ' IN INODE ', key, 'AT OFFSET ', indirect[key][j][1], sep="")
				else:	#mark this block as visited or duplicate
					if int(indirect[key][j][3]) in referenced:
						print('DUPLICATE ', blockType, 'BLOCK ', indirect[key][j][3], ' IN INODE ', key, 'AT OFFSET ', indirect[key][j][1], sep="")
					else:
						referenced.append(int(indirect[key][j][3]))
			else:  # what error message do we output here? for later
				print('INVALID BLOCK ', inode[key], ' IN INODE ', key, 'AT OFFSET ???')  
	
	#check for unreferenced blocks - tested by temporarily changing BFREE 37 to an already referenced blocknum (9)
	possibleValidBlocks = generateAllBlocks(lastInodeBlk) 
	unreferenced = list(set(possibleValidBlocks) - set(referenced+bfree))
	for unrefBlock in unreferenced:
		print('UNREFERENCED BLOCK', unrefBlock)
		
	#check for allocated blocks - tested in same way as described above
	allocated = set(referenced).intersection(set(bfree))
	for allocBlock in allocated:
		print('ALLOCATED BLOCK', allocBlock, 'ON FREELIST')
	
#def inodeAllocationAudit():
	#swag

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
	blockConsistencyHelper(inode, superblock, group)
	#inodeAllocationAudit()


