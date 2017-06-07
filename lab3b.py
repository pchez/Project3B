#!/usr/bin/python
from __future__ import print_function
import csv
import sys

#SUPERBLOCK
#GROUP
#BFREE - same format as inode, each index is block number and have 0 if free and 1 if not
#IFREE - same as above
#DIRENT - dictionary with key as parent inode and values as the rest of the DIRENT entry
#INODE - dictionary with key as inode number and values as the rest of the dirent entry
#INDIRECT - dictionary with key as parent inode and values as the rest of the INDIRECT entry

BLOCKSIZE = 1024	
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
	referenced = []
	#-------------first mark all duplicates----------------------
	for key in inode.keys():
		for j in range(10,25):
			if int(inode[key][j]) < 0 or int(inode[key][j]) > int(superblock[0]): #ignore invalid block
				continue
			elif int(inode[key][j]) < lastInodeBlk and int(inode[key][j]):		 #ignore reserved block
				continue
			else:	
				if int(inode[key][j]) != 0:
					referenced.append(int(inode[key][j]))		#add to referenced list
	for key in indirect.keys():
		for j in range(0,len(indirect[key])):
			if int(indirect[key][j][3]) <= 0 or int(indirect[key][j][3]) > int(superblock[0]):	#ignore invalid		
				continue
			elif int(indirect[key][j][3]) <= lastInodeBlk:	#ignore
				continue
			else:	
				if int(indirect[key][j][3]) != 0:
					referenced.append(int(indirect[key][j][3]))	#add to referenced list
		
	#---------------go through all inode entries----------------
	for key in inode.keys():
		# only check if valid inode num, valid mode number, and greater than zero link count
		if int(key) > 0 and int(inode[key][1]) > 0 and int(inode[key][4]) > 0:		
			#print(key)
			for j in range(10,25):
				#print 'key ', key, 'iblock num ', j, 'address ', inode[key][j]  	#for debugging - DELETE
				
				if j == 22:		#get type of block for stdout
					blockType = 'INDIRECT '
					offset = 12  
				elif j == 23:
					blockType = 'DOUBLE INDIRECT '
					offset = 12 + int(superblock[2])/4
				elif j == 24:
					blockType = 'TRIPPLE INDIRECT '
					offset = 12 + (int(superblock[2])/4) + ((int(superblock[2])/4)*(int(superblock[2])/4))	
				else:
					blockType = ''
					offset = j-10
					
				if int(inode[key][j]) < 0 or int(inode[key][j]) > int(superblock[0]): #invalid block
					print('INVALID ', blockType, 'BLOCK ', inode[key][j], ' IN INODE ', key, ' AT OFFSET ', offset, sep="") 
				
				elif int(inode[key][j]) < lastInodeBlk and int(inode[key][j]) > 0: #reserved block
					print('RESERVED ', blockType, 'BLOCK ', inode[key][j], ' IN INODE ', key, ' AT OFFSET ', offset, sep="")
				
				else: #mark block as visited or duplicate (maybe create a new array with markers per block) 
				 	if int(inode[key][j]) != 0 and referenced.count(int(inode[key][j])) > 1: #is duplicate!	
				 		print('DUPLICATE ', blockType, 'BLOCK ', inode[key][j], ' IN INODE ', key, ' AT OFFSET ', offset, sep="")
					
				 		
		#else: #inode block itself has error -- how to handle???
			#print('INVALID BLOCK ', inode[key], ' IN INODE ', inode[key], ' AT OFFSET ???', sep="")  
	
	#-------------------go through all indirect entries---------------
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
					print('INVALID ', blockType, 'BLOCK ', indirect[key][j][3], ' IN INODE ', key, ' AT OFFSET ', indirect[key][j][1], sep="")
				elif int(indirect[key][j][3]) <= lastInodeBlk:
					print('RESERVED ', blockType, 'BLOCK ', indirect[key][j][3], ' IN INODE ', key, ' AT OFFSET ', indirect[key][j][1], sep="")
				else:	#mark this block as visited or duplicate
					if int(indirect[key][j][3]) != 0 and referenced.count(int(indirect[key][j][3])) > 1:
						print('DUPLICATE ', blockType, 'BLOCK ', indirect[key][j][3], ' IN INODE ', key, ' AT OFFSET ', indirect[key][j][1], sep="")
			else:  # what error message do we output here? for later
				print('INVALID BLOCK ', inode[key], ' IN INODE ', key, ' AT OFFSET ???')  
	
		
		
	#check for unreferenced blocks - tested by temporarily changing BFREE 37 to an already referenced blocknum (9)
	possibleValidBlocks = generateAllBlocks(lastInodeBlk) 
	unreferenced = list(set(possibleValidBlocks) - set(referenced+bfree))
	for unrefBlock in unreferenced:
		print('UNREFERENCED BLOCK', unrefBlock)
		
	#check for allocated blocks - tested in same way as described above
	allocated = set(referenced).intersection(set(bfree))
	for allocBlock in allocated:
		print('ALLOCATED BLOCK', allocBlock, 'ON FREELIST')
	
def inodeAllocationAudit():
	allocated = []
	unallocated = []
	
	for inode_num in inode.keys():
		if inode_num in ifree: 
			#if file or directory has links associated, allocated
			if (inode[inode_num][0]=='d' or inode[inode_num][0]=='f') and int(inode[inode_num][4]) > 0: 		
				print('ALLOCATED INODE ', inode_num, ' ON FREELIST', sep="")
		else: #not on freelist
			#if file or directory doesn't have links associated, unallocated
			if (inode[inode_num][0]=='d' or inode[inode_num][0]=='f') and int(inode[inode_num][4])==0: 
				print('UNALLOCATED INODE ', inode_num, 'NOT ON FREELIST', sep="")
			

def directoryConsistencyAudit():
	fileLinks = {}
	lastInodeBlk = int(group[7]) + ((int(superblock[3])*int(superblock[1]))/int(superblock[2]) )
	
	#-----------------link count-----------------------------
	for inode_num in inode.keys(): #first count number of links
		
		for dir_inode in dirent.keys(): #loop through all directory entries
			for dir_idx in range(0,len(dirent[dir_inode])):
				if int(dirent[dir_inode][dir_idx][1])==inode_num:
					if inode_num in fileLinks.keys(): #if inode_num already accounted for in list of links
						fileLinks[inode_num] = fileLinks[inode_num] + 1
					else:							#if not already accounted for
						fileLinks[inode_num] = 1	#start the first count
	
	for inode_num in inode.keys():
		if inode[inode_num][0]=='d' or inode[inode_num][0]=='f' or inode[inode_num][0]=='s': #inode type is file, directory, or link
			if inode_num in fileLinks.keys():
				if int(inode[inode_num][4]) != fileLinks[inode_num]:	#num of links that we tracked not same as ref count listed in this entry
					print('INODE ', inode_num, ' HAS ', fileLinks[inode_num], ' LINKS BUT LINKCOUNT IS ', inode[inode_num][4], sep="")
			else:
				print('INODE ', inode_num, ' HAS ', 0, ' LINKS BUT LINKCOUNT IS ', inode[inode_num][4], sep="")
	
	
	#----------------directory validity----------------------
	#accessing a directory is invalid when it doesnt show up in the list of inodes or when the link count is 0
	unallocFlag = 0
	invalidFlag = 0
	for inode_num in dirent.keys():
		for dir_idx in range(0,len(dirent[inode_num])):
			refInode = int(dirent[inode_num][dir_idx][1])
			if refInode in inode.keys():
				if int(inode[refInode][4]==0): #if link count is 0
					unallocFlag = 1
			else: 	#not in list of inodes
				if refInode > int(group[2]) or refInode < 0: #invalid inode number
					invalidFlag = 1
				else:
					unallocFlag = 1
		
		
			if unallocFlag==1:
				print('DIRECTORY INODE ', inode_num, ' NAME ', dirent[inode_num][dir_idx][4], ' UNALLOCATED INODE ', dirent[inode_num][dir_idx][1], sep="")
			if invalidFlag==1:
				print('DIRECTORY INODE ', inode_num, ' NAME ', dirent[inode_num][dir_idx][4], ' INVALID INODE ', dirent[inode_num][dir_idx][1], sep="")
			
			unallocFlag = 0
			invalidFlag = 0
	
	#-------validity of . and .. directories----------------
	ref_dict = {}
	for inode_num in dirent.keys(): 	#get a dict of directory entries and the inodes they reference
		for dir_idx in range(0,len(dirent[inode_num])):
			if inode_num in ref_dict.keys():
				ref_dict[inode_num].append(int(dirent[inode_num][dir_idx][1]))
			else:
				ref_dict[inode_num] = [int(dirent[inode_num][dir_idx][1])]
	
	for inode_num in dirent.keys():
		parent_inode = inode_num
		for dir_idx in range(0,len(dirent[inode_num])):
			ref_inode = int(dirent[inode_num][dir_idx][1])
			if dirent[inode_num][dir_idx][-1]=="'.'":
				if ref_inode != parent_inode:	
					print('DIRECTORY INODE ', inode_num, ' NAME ', dirent[inode_num][dir_idx][-1], ' LINK TO INODE ', dirent[inode_num][dir_idx][1], ' SHOULD BE ', inode_num, sep="")
			if dirent[inode_num][dir_idx][-1]=="'..'":
				if ref_inode in ref_dict.keys():
					if parent_inode not in ref_dict[ref_inode]: #if the directory above contains a ref to this directory entry
						print('DIRECTORY INODE ', inode_num, ' NAME ', dirent[inode_num][dir_idx][-1], ' LINK TO INODE ', dirent[inode_num][dir_idx][1], ' SHOULD BE ', inode_num, sep="")
				else:
					print('DIRECTORY INODE ', inode_num, ' NAME ', dirent[inode_num][dir_idx][-1], ' LINK TO INODE ', dirent[inode_num][dir_idx][1], ' SHOULD BE ', inode_num, sep="")
if __name__=="__main__":
	#read arguments
	if len(sys.argv) < 2:
		sys.stderr.write('Please provide one file system to test\n')
		exit(1)

	#-----------open file----------------------
	with open(sys.argv[1]) as filesysCSV:
		filesysReader = csv.reader(filesysCSV, delimiter=',')
		filesys = list(filesysReader) #<---- the main data structure that stores everything in a list of lists
	#except:
#		sys.stderr.write('File system not found')
		#exit(1)
		
		#----------read everything into lists and lists of lists----------
	superblock, group, bfree, ifree, inode, dirent, indirect = createArrays(filesys)

	#invalidBlockHelper(inode);  #examine every blk pointer in: i-node, direct blk, single, double, tripple indirect    
	# for this we will loop through EVERY inode, and check all of its blk pointers 
	# errors here will be either INVALID BLOCK or RESERVED (meaning that the blk number is in one of the SUPER, GROUP, IFREE, BFREE, and INODE TABLE areas)	
	blockConsistencyHelper(inode, superblock, group)
	inodeAllocationAudit()
	directoryConsistencyAudit()

