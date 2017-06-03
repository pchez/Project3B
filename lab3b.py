import csv

#SUPERBLOCK
#GROUP
#BFREE - same format as inode, each index is block number and have 0 if free and 1 if not
#IFREE - same as above
#DIRENT
#INODE for each inode # a list of attributes. list of dicts. each index is an inode number. each dict has key
#'info' which stores all the attributes associated with the inode data structure in the ext2 header file
#'dirent' which stores a list of associated directories of that inode number
#and similarly, an 'indirect' key
#INDIRECT

BLOCKSIZE = 1024	

def createArrays(fs):
	superblock = []
	group = []
	bfree = [1]*BLOCKSIZE #initialize an array of ones, default is not free
	ifree = [1]*BLOCKSIZE
	inode = [0]*BLOCKSIZE #not sure if this should be the whole blocksize or just number of inodes in inode block
	
	#initialize inode dict to have empty
	for i in range(0,BLOCKSIZE):
		inode[i] = {'info':[], 'dirent':[], 'indirect':[]}
		
	for row in fs:
		type = row[0] 	#identifies whether this row is for SUPERBLOCK, GROUP, BFREE, etc
		if type=='SUPERBLOCK':
			superblock = row[1:len(row)]	#store everything after SUPERBLOCK into array
		elif type=='GROUP':
			group = row[1:len(row)]
		elif type=='BFREE':
			bfree[int(row[1])] = 0 #mark items on bfree list as free (0)
		elif type=='IFREE':
			ifree[int(row[1])] = 0 #mark items on ifree list as free (0)
		elif type=='DIRENT':
			inode[int(row[1])]['dirent'].append(row[2:len(row)])  #append dirent entry to associated inode parent
		elif type=='INODE':
			inode[int(row[1])]['info'] = row[2:len(row)] #add all inode info to the inode index that it's referred to
		elif type=='INDIRECT':
			inode[int(row[1])]['indirect'].append(row[2:len(row)])  #append indirect entry to associated inode parent
			
	return superblock, group, bfree, ifree, inode
		

if __name__=="__main__":

    #-----------open file----------------------
    with open('trivial.csv', newline="") as filesysCSV:
    	filesysReader = csv.reader(filesysCSV, delimiter=',')
    	filesys = list(filesysReader) #<---- the main data structure that stores everything in a list of lists
    	
    #----------read everything into lists and lists of lists----------
    superblock, group, bfree, ifree, inode = createArrays(filesys)
    
    
    
    	
    


