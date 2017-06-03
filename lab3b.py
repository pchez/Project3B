import csv


if __name__=="__main__":

    #-----------open file----------------------
    with open('trivial.csv', newline="") as trivial_csv:
    	trivialfs = csv.reader(trivial_csv, delimiter=',')
    	trivial = list(trivialfs)
    
    
    	
    


