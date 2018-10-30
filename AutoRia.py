import requests
import json

class Auto_Ria():
	def mark(self,data):
		response = json.loads(requests.get(
			"https://developers.ria.com/auto/categories/1/marks?api_key=8SvFzVX3ILDYOxfWEJVc3KkRBENsLIYnD5MVVpzv").text)
		for mark in response:
			if data.message.lower().replace(" ", "")==mark["name"].lower().replace(" ", ""):
				data.storage["AutoRia_attributes"]["mark"]=str(mark["value"])
				return 
	def model(self,data):
		response = json.loads(requests.get(
			"https://developers.ria.com/auto/categories/1/marks/"+data.storage["AutoRia_attributes"]["mark"]+"/models?api_key=8SvFzVX3ILDYOxfWEJVc3KkRBENsLIYnD5MVVpzv").text)
		for model in response:
			if data.message.lower().replace(" ", "")==model["name"].lower().replace(" ", ""):
				data.storage["AutoRia_attributes"]["model"]=str(model["value"])
				return 
	def Get_price(self,data):
		request="https://developers.ria.com/auto/average_price?api_key=8SvFzVX3ILDYOxfWEJVc3KkRBENsLIYnD5MVVpzv"
		if data.storage["AutoRia_attributes"].get("mark")!=None:
			request+="&marka_id="+str(data.storage["AutoRia_attributes"]["mark"])
		if data.storage["AutoRia_attributes"].get("model")!=None:
			request+="&model_id="+str(data.storage["AutoRia_attributes"]["model"])
		if data.storage["finding_list"].get("max_run")!=None:
			request += "&raceInt="+str(data.storage["finding_list"].get("min_run"))+"&raceInt="+str(data.storage["finding_list"].get("max_run"))
		print (request)
		response=requests.get(request).text
		return  json.loads(response)

		