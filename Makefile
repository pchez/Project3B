# NAME: Priscilla Cheng and Saurabh Deo
# EMAIL: priscillaccheng@gmail.com and saurabhdeo27@gmail.com
# ID: 404159386 and 404616605

SOURCES = lab3b.py
TARNAME = lab3b-404159386.tar.gz
TARCONTENTS = $(SOURCES) README Makefile

default:
	cp lab3b.py lab3b
	chmod +x lab3b

clean:
	@- rm lab3b $(TARNAME)

dist:  
	tar -czvf $(TARNAME) $(TARCONTENTS)
	
