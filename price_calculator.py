import urllib.request
import csv
import json

def isint(s):
	try:
		int(s)
		return True
	except ValueError:
		return False
class Calculator():
	def __init__(self):
		svsfile = urllib.request.urlopen(
			"https://docs.google.com/spreadsheets/d/e/2PACX-1vS51WzwV1bq12DzshtyxCJA9MPeumO5xugf9ufibFMahmREjyJuqxP58C_LH_lIxWbaGLGT0K2xISqP/pub?gid=0&single=true&output=csv").read()
		svsfile = svsfile.decode('utf-8')
		last=""
		preslat=""
		list = svsfile.split("\n")
		for i in range(len(list)):
			list[i] = list[i].split(",")
		self.list=list
	def get_price(self,data):
		if data.storage["finding_list"].get("mark")!=None and data.storage["finding_list"].get("model")!=None:
			for car in self.list:
				if data.storage["finding_list"].get("mark").replace(" ","").lower()==car[0].replace(" ","").lower() and data.storage["finding_list"].get("model").replace(" ","").lower()==car[1].replace(" ","").lower():
					if data.storage["finding_list"].get("year")!=None:
						i=0
						while 3+i*4<len(car):
							if str(car[3+i*4])==str(data.storage["finding_list"].get("year")):
								return car[5+i*4]
							i+=1
					else:
						prise=0
						i=0
						while 3 + i * 4 < len(car):
							prise+=int(car[3+i*4])
							i += 1
						return prise/i
			return "not found"
					