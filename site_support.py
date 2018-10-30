import requests
import json
from woocommerce import API


def append_car(data, copart_answer=None, iaai_info=None):
	wcapi = API(
		url="http://caramerica.com.ua/",  # Your store URL
		consumer_key="№№№№№№№№№№№№№№№№№№№№№№№№№№№№",  # Your consumer key
		consumer_secret="c№№№№№№№№№№№№№№№№№№№№№№№№№№№№",  # Your consumer secret
		version="v3",  # WooCommerce API version
		timeout=9999
	)
	# print (wcapi.get("products?per_page=1&pa_model=68").json())
	# print(wcapi.get("products/attributes").json()) 13507
	print (data.storage["description"].replace("\n", "<br>"))
	data_json = {
		"product": {
			"title": "Car_test_123_delete_if_see",
			"description": data.storage["description"].replace("\n", "<br>"),
			"short_description": data.storage["description"].replace("\n", "<br>"),

			"images": [

			],
			"attributes": [

			]

		}
	}
	i = 0
	for image in data.storage["car_images"]:
		data_json["product"]["images"].append({
			"src": image,
			"position": i
		})
		i += 1
	if copart_answer != None:
		data_json["product"]["title"] = copart_answer["data"]["lotDetails"]["ld"]
		data_json["product"]["attributes"].append({
			"name": "Модель",
			"slug": "model",
			"position": "0",
			"visible": False,
			"variation": True,
			"options": [
				copart_answer["data"]["lotDetails"]["lm"]
			]
		})
		data_json["product"]["attributes"].append({
			"name": "Марка",
			"slug": "make",
			"position": "0",
			"visible": False,
			"variation": True,
			"options": [
				copart_answer["data"]["lotDetails"]["mkn"]
			]
		})
		if copart_answer["data"]["lotDetails"]["lcy"] != None:
			data_json["product"]["attributes"].append({
				"name": "Год",
				"slug": "caryear",
				"position": "0",
				"visible": False,
				"variation": True,
				"options": [
					copart_answer["data"]["lotDetails"]["lcy"]
				]
			})
	else:
		data_json["product"]["title"] = iaai_info["name"]
		data_json["product"]["attributes"].append({
			"name": "Модель",
			"slug": "model",
			"position": "0",
			"visible": False,
			"variation": True,
			"options": [
				iaai_info["name"].replace(iaai_info["name"].split(" ")[0] + " ", "")
			]
		})
		data_json["product"]["attributes"].append({
			"name": "Марка",
			"slug": "make",
			"position": "0",
			"visible": False,
			"variation": True,
			"options": [
				iaai_info["name"].split(" ")[0]
			]
		})
		if iaai_info.get("year") != None:
			data_json["product"]["attributes"].append({
				"name": "Год",
				"slug": "caryear",
				"position": "0",
				"visible": False,
				"variation": True,
				"options": [
					iaai_info.get("year")
				]
			})
	return (wcapi.post("products", data_json).json())


