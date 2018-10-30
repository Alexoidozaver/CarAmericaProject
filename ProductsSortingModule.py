import CopartAPI
import IaaIAPI
from BotEngine.NewLogger import *
from BotEngine.Data import Data
import json

iaai_sorting = IaaIAPI.IaaIAPI()
iaai_sorting.Set("perpage", 1)
copart = CopartAPI.CopartAPI()
copart.Set("perpage", 1)


# CopartProducts=copart.Make_Query()


def get_copatr_by_id(id):
	a = copart.Get_Car_Info(id)
	print (a)
	return a


def add_posible_value(car, name, keyboard_list):
	# добавляет значение атрибута в клавиатуру из CARAmerica API
	id_of_atribute = [i for i in range(len(car["attributes"])) if
					  car["attributes"][i]["name"] == name]
	if len(id_of_atribute) == 1:
		try:
			if car["attributes"][id_of_atribute[0]]['options'][0] not in keyboard_list:
				keyboard_list.append(car["attributes"][id_of_atribute[0]]['options'][0])
		except:
			pass
	return keyboard_list


translation_dictionary = {
	'Automatic': "Механическая",
	'Manual': "Автоматическая",
	'Compressed Natural Gas': "Сжатый природный газ",
	'Convertible To Gaseous Powered': "Конвертируемый в газовый",
	'Diesel': "Дизель",
	'Electric': "Электрический",
	'Flexible Fuel': "Гибкое топливо",
	'Gas': "Газ",
	'Hybrid Engine': "Гибридный двигатель",
	'Hydrogen Fuel Cell': "Водородный топливный элемент",
	'Bus': "Автобус",
	'Coupe': "Купе",
	'Coupe 3d': "Купе 3д",
	'Hatchbac': "Хетчбек",
	'Limousin': "Лимузин",
	'Moto Cro': "Мото-Кро",
	'Motor Sc': "Мотор-С",
	'Motorize': "Моторизированая",
	'Pickup': "Пикап",
	'Racer': "Гоночная",
	'Road/str': "Доржный / уличный",
	'Roadster': "Родстер",
	'Sedan 2': "Седан 2",
	'Sedan 4d': "Седан 4д",
	'Sport Pi': "Спорт Пи",
	'Sports V': "Спорт 6",
	'Step Van': "микроавтобус",
	'Tilt Cab': "Грузовик",
	'Tractor': "Трактор",
	'Van Camp': "Фургон"
}


def get_real_name(name):
	for item in translation_dictionary.items():
		if item[1] == name:
			return item[0]
	return "Error"


def add_copart_atributes(data, name):
	# возвращает клаву в которую добавили нужные атрибуты из Копарт АПИ
	list = []
	amount = 0
	if name == 'Модель':
		list = copart.Get_All_Models(data.storage["finding_list"].get("mark"))
	elif name == 'Марка':
		list = copart.Get_All_Marks()
	else:
		copart_answer = take_copart_answer(data)
		if name == 'Год':
			i = 2010
			while i < 2019:
				list.append(str(i))
				i += 1
		elif name == 'Коробка':
			for item in copart_answer["data"]["results"]["facetFields"][15]["facetCounts"]:
				if translation_dictionary.get(item["displayName"]) != None:
					list.append(translation_dictionary[item["displayName"]])
		elif name == 'Тип кузова':
			for item in copart_answer["data"]["results"]["facetFields"][12]["facetCounts"]:
				if translation_dictionary.get(item["displayName"]) != None:
					list.append(translation_dictionary[item["displayName"]])
		elif name == 'Тип топлива':
			for item in copart_answer["data"]["results"]["facetFields"][13]["facetCounts"]:
				if translation_dictionary.get(item["displayName"]) != None:
					list.append(translation_dictionary[item["displayName"]])
		amount += int(copart_answer["data"]["results"]["totalElements"])
	return list, amount


def take_copart_answer(data, page=1, id=None):
	if id == None:
		change_atributes_in_engine(data, "mark", "mark", False)
		change_atributes_in_engine(data, "model", "model", False)
		change_atributes_in_engine(data, "kuzov", "body", True)
		change_atributes_in_engine(data, "oil", "fuel", True)
		change_atributes_in_engine(data, "transmission", "transmission", True)
		if data.storage["finding_list"].get("year") != None:
			copart.Set("year_from", data.storage["finding_list"].get("year"))
			copart.Set("year_to", data.storage["finding_list"].get("year"))
		else:
			copart.Set("year_from", 1900)
			copart.Set("year_to", 2019)
		copart.Set("page", page)
		copart.Set("perpage", 1)
		CopartProducts = copart.Make_Query()
		return CopartProducts
	else:
		return copart.Get_Car_Info(id)


def change_atributes_in_engine(data, name, subname, is_translated):
	if data.storage["finding_list"].get(name) != None:
		if is_translated:
			if not translated_atributes_append(data, name, subname):
				copart.Set(subname, data.storage["finding_list"].get(name))
		else:
			copart.Set(subname, data.storage["finding_list"].get(name))

	else:
		copart.Set(subname, "")


def translated_atributes_append(data, atribure, subname):
	for key in translation_dictionary.keys():
		if data.storage["finding_list"].get(atribure) == translation_dictionary[key]:
			copart.Set(subname, key)
			return True
	return False


def take_iaai_answer(data, page):
	append_atributes_iaai_into_object(data, page)
	if data.storage["iaai_search_error"]:
		return None
	return iaai_sorting.Make_Query()


def take_iaai_info(id):
	return iaai_sorting.Get_Car_Info(id)


def add_iaai_atributes(data, name, list):
	if name == 'Марка':
		list2 = iaai_sorting.Get_All_Marks()
		data.storage["iaai_marks"] = list2


def append_atributes_iaai_into_object(data, page=1):
	data.storage["iaai_search_error"] = False
	iaai_sorting.Set("page", str(page))
	if data.storage["finding_list"].get("mark") != None:
		id = get_mark_id(data.storage["finding_list"].get("mark"))
		if id == None:
			data.storage["iaai_search_error"] = True
		else:
			iaai_sorting.Set("mark", id)
	else:
		iaai_sorting.query.pop("mark", "")
	if data.storage["finding_list"].get("model") != None:
		id = get_model_id(data, data.storage["finding_list"].get("model"), data.storage["finding_list"].get("mark"))
		if id == None:
			data.storage["iaai_search_error"] = True
		else:
			iaai_sorting.Set("model", id)
	else:
		iaai_sorting.query.pop("model", "")
	if data.storage["finding_list"].get("year") != None:
		iaai_sorting.Set("year_from", data.storage["finding_list"].get("year"))
		iaai_sorting.Set("year_to", data.storage["finding_list"].get("year"))
	else:
		iaai_sorting.query.pop("year_from", "")
		iaai_sorting.query.pop("year_to", "")
	return True


def get_mark_id(name):
	marks = iaai_sorting.Get_All_Marks()
	for mark in marks:
		if mark["name"] == name:
			return str(mark["id"])
	return None


def get_model_id(data, name, mark):
	for mark_iaai in data.storage["iaai_marks"]:
		if mark_iaai["name"].lower() == mark.lower():
			models = iaai_sorting.Get_All_Models(mark_iaai["name"])
			for model in models:
				if model["model"].lower() == name.lower():
					return str(model["model_id"])
	return None


def create_image_list(images):
	image_list = []
	for image in images:
		image_list.append(image["url"])
	return image_list


def take_copart_amount(data):
	copart_answer = take_copart_answer(data)
	return int(copart_answer["data"]["results"]["totalElements"])


def take_iaai_amount(data):
	append_atributes_iaai_into_object(data)
	if data.storage["iaai_search_error"]:
		return 0
	iaai_answer = iaai_sorting.Make_Query()
	if iaai_answer == None:
		return 0
	return int(iaai_answer["amount"])