# -*- coding: utf-8 -*-
from BotEngine import *
import re
import time
import json
import random
import requests
import threading
from woocommerce import API
import price_calculator
import mannager_connection
import re
import ProductsSortingModule
import CopartAPI
import AutoRia
import IaaIAPI
import site_support
copart = CopartAPI.CopartAPI()
copart.Set("perpage", 1)
iaaa=IaaIAPI.IaaIAPI()
from BotEngine.NewLogger import *
log = NewLogger(LOG_CONSOLE)

Auto_Ria=AutoRia.Auto_Ria()
calculator=price_calculator.Calculator()

#CopartProducts=copart.Make_Query()


def cleanhtml(raw_html):
	cleanr = re.compile('<.*?>')
	cleantext = re.sub(cleanr, '', raw_html)
	return cleantext

# import manager_connection

admin_chat_id = 301346887
bot = TelegramBot(__file__)
bot = mannager_connection.manager_connection(bot, admin_chat_id)


def convert_finding_list(data):
	text=""
	if data.storage["finding_list"].get("type")!=None:
		text+="Тип: "+str(data.storage["finding_list"]["type"])+"\n"
	if data.storage["finding_list"].get("min_prise")!=None:
		text+="Мин. цена: "+str(data.storage["finding_list"]["min_prise"])+"\n"
	if data.storage["finding_list"].get("max_prise") !=None:
		text+="Макс. цена: "+str(data.storage["finding_list"]["max_prise"])+"\n"
	if data.storage["finding_list"].get("mark")!=None:
		text += "Марка: " + str(data.storage["finding_list"]["mark"])+"\n"
	if data.storage["finding_list"].get("model")!=None:
		text += "Модель: " + str(data.storage["finding_list"]["model"])+"\n"
	if data.storage["finding_list"].get("min_run") !=None:
		text += "Мин. пробег: " + str(data.storage["finding_list"]["min_run"])+"\n"
	if data.storage["finding_list"].get("max_run")!=None:
		text += "Макс. пробег: " + str(data.storage["finding_list"]["max_run"])+"\n"
	if data.storage["finding_list"].get("transmission")!=None:
		text += "Трансмиссия: " + str(data.storage["finding_list"]["transmission"])+"\n"
	if data.storage["finding_list"].get("kuzov") !=None:
		text += "Кузов: " + str(data.storage["finding_list"]["kuzov"])+"\n"
	if data.storage["finding_list"].get("oil") !=None:
		text += "Топливо: " + str(data.storage["finding_list"]["oil"])+"\n"
	return text
#################################################################################################################################
# DATABASE functions
@Database_(bot.database)
def create_row_question(user_id, message):
	connect = bot.database.Get_Connection()
	cursor = connect.cursor()
	cursor.execute("SELECT * FROM help WHERE user_id=%s" % (int(user_id)))
	local_request = cursor.fetchone()
	local_last_row = 0
	if local_request == None:
		cursor.execute(
			"INSERT INTO help(user_id,question,last_id) VALUES (%s,'%s',%s)" % (int(user_id), message, 0))
	else:
		while local_request != None:
			local_last_row = local_request
			local_request = cursor.fetchone()
		cursor.execute("INSERT INTO help(user_id,question,last_id) VALUES (%s,'%s',%s)" % (
			int(user_id), message, local_last_row["id"]))
	connect.commit()

@Database_(bot.database)
def append_attributes_to_user_histiory(data):
	connect = bot.database.Get_Connection()
	cursor = connect.cursor()
	cursor.execute("INSERT INTO user_attributes_history (user_id,attributes) VALUES(%s,'%s')" % (data.user_id, json.dumps(data.storage["finding_list"])))
	connect.commit()

@Database_(bot.database)
def append_id(id,tag):
	connect = bot.database.Get_Connection()
	cursor = connect.cursor()
	cursor.execute("INSERT INTO ids_of_added_cars (car_id,product_tag ) VALUES(%s,'%s')" % ( id,tag))
	connect.commit()

@Database_(bot.database)
def is_exist(tag):
	connect = bot.database.Get_Connection()
	cursor = connect.cursor()
	cursor.execute("SELECT * FROM ids_of_added_cars WHERE product_tag='%s'" % ( tag))
	answer=cursor.fetchone()
	if answer!=None:
		return True
	else:
		return False

@Database_(bot.database)
def get_last_row(user_id):
	connect =  bot.database.Get_Connection()
	cursor = connect.cursor()
	cursor.execute("SELECT * FROM help WHERE user_id=%s" % (user_id))
	local_a = cursor.fetchone()
	local_b = 0
	while local_a != None:
		local_b = local_a
		local_a = cursor.fetchone()
	return local_b

@Database_(bot.database)
def append_a_source(data):
	connect = bot.database.Get_Connection()
	cursor = connect.cursor()
	cursor.execute("SELECT * FROM sourse_of_user WHERE user_id='%s'" % (data.user_id))
	query_result=cursor.fetchone()
	if query_result==None:
		if isinstance(data.message, list) and len(data.message)>1:
			cursor.execute("INSERT INTO sourse_of_user (user_id,sourse_id) VALUES(%s,%s)" % (data.user_id,data.message[1]))
		else:
			cursor.execute(
				"INSERT INTO sourse_of_user (user_id,sourse_id) VALUES(%s,%s)" % (data.user_id, 0))
	connect.commit()
# Functions
#################################################################################################################################
# Steps
@Step(bot.handler, "main", "start")
def main_start(data):
	data.storage["iaai_search_error"] = False
	data.engine.database.append_a_source(data)
	if isinstance(data.message, list) and (len(data.message) == 4 or len(data.message) == 3 or len(data.message) == 2):
		if data.message[2]=="cars" and len(data.message) == 3:
			data.storage["finding_list"]["type"] = data.engine.data.Get("buttons", "car")
			data.engine.Set_Position_Active(data,"find", "check_prise")
		elif len(data.message) == 4:
			Send_Product_Id_Branch(data, int(data.message[3]), data.message[2], 0)
			return
	else:
		data.storage["finding_list"] = {}
		if data.type == Handle_Triger():
			keyboard = []
			keyboard.append([
				{"type": "text", "text": "{buttons[about_us]}", "data": {"i": "main", "s": "about_us"}}])
			keyboard.append([
				{"type": "text", "text": "{buttons[delivery]}", "data": {"i": "main", "s": "help"}}])
			data.engine.Send_Photo(data,
								   link="AgADAgADNakxGwEsIUqJQCrviGXS17rLRg4ABFX3Yf7fR966CfMDAAEC",
								   keyboard=("main"))
			data.engine.Send_Message(data, text=data.Get_Answer("main", "start"),
									 keyboard=data.engine.Callback_Keyboard(keyboard))
		else:
			if data.message == data.engine.data.Get("buttons", "other"):
				data.engine.Send_Message(data,text="Также вы можете заказать другие виды транспорта:", keyboard=data.engine.Get_Keyboard(name="other"))
			elif data.message == data.engine.data.Get("buttons", "mannager"):
				return Go_To("help", "mennager")
			elif data.message == data.engine.data.Get("buttons", "back"):
				data.engine.Send_Message(data,text="Открыто главное меню.", keyboard=data.engine.Get_Keyboard(name="main"))
			buttons = [data.engine.data.Get("buttons", "car"),
					   data.engine.data.Get("buttons", "motosycle"),
					   data.engine.data.Get("buttons", "water"),
					   data.engine.data.Get("buttons", "special"),
					   data.engine.data.Get("buttons", "bicycle"),
					   data.engine.data.Get("buttons", "quadrocopters"),
					   data.engine.data.Get("buttons", "extreme"),
					   data.engine.data.Get("buttons", "gyrotransport")]
			if data.message in buttons:
				if data.message == data.engine.data.Get("buttons", "car"):
					data.storage["finding_list"]["type"] = data.message
					return Go_To("find", "check_prise")
				else:
					data.storage["finding_list"]["type"] = data.message
					return Go_To("find", "query_mobile")


def Send_Product_Id_Branch(data, id, site, photo_id):
	message = ""
	car_images = []
	if site == "copart":
		copart_info = copart.Get_Car_Info(int(id))
		if copart_info["data"]["lotDetails"].get("mkn") != None:
			message += " " + str(copart_info["data"]["lotDetails"].get("mkn"))
		if copart_info["data"]["lotDetails"].get("lm") != None:
			message += " " + str(copart_info["data"]["lotDetails"].get("lm"))
		if copart_info["data"]["lotDetails"].get("lcy") != None:
			message += " " + str(copart_info["data"]["lotDetails"].get("lcy"))
		car_images = copart.Get_Car_Images(str(id))["data"]["imagesList"]["FULL_IMAGE"]
		car_images = ProductsSortingModule.create_image_list(car_images)
	else:
		iaai_info = ProductsSortingModule.take_iaai_info(str(id))
		car_images = iaaa.Get_All_Images(iaai_info["stock_id"])
		message += iaai_info["name"] + ' ' + str(iaai_info["year"])
	if photo_id >= len(car_images):
		photo_id = 0
	'''keyboard = data.engine.Get_Keyboard("1",
										callback={
											"1": {"i": "id", "s": "buy", "id": str(id), "st": site, "p": str(photo_id)}}
										, text={"1": "<font color=\"#FFFFFF\">" + "{buttons[Checkout]}" + "</font>"})'''
	keyboard = InlineKeyboardMarkup(
		[[InlineKeyboardButton(data.engine.data.Get("buttons", "Checkout"), callback_data=data.engine.Callback_Data(
			{"i": "id", "s": "buy", "id": str(id), "st": site, "p": str(photo_id)}))],

		 [InlineKeyboardButton(data.engine.data.Get("buttons", "description"), callback_data=data.engine.Callback_Data(
			 {"i": "id", "s": "mr", "id": str(id), "st": site, "p": str(photo_id)}))],
		 [InlineKeyboardButton(data.engine.data.Get("buttons","photos").format(str(photo_id + 1),str(len(car_images))), callback_data=data.engine.Callback_Data(
			 {"i": "id", "s": "ph", "id": str(id), "st": site, "p": str(photo_id)}))]])

	data.engine.Send_Photo(data, link=car_images[photo_id], keyboard=("listing_2"))
	data.engine.Send_Message(data, text=message, keyboard=keyboard)



@Step(bot.callback_handler, "id", "buy")
def callback_ctg_view_buy(data):
	desc = ""
	copart_info = None
	if data.message["st"] == "copart":
		copart_info = copart.Get_Car_Info(int(data.message["id"]))
		desc = add_description_copart(data, copart_answer=copart_info["data"]["lotDetails"], clear=True)
	else:
		iaai_info = ProductsSortingModule.take_iaai_info(data.message["id"])
		desc = add_description_iaai(data, iaai_info=iaai_info, clear=True)
	message = ""
	message += data.message["st"] + " " + data.message["id"] + "\n" + desc
	if data.message["st"] == "copart":
		message += "\nЦена:" + str(copart_info["data"]["lotDetails"]["la"])
		message +="\nhttps://www.copart.com/lot/"+str(data.message["id"])
	answer = ""
	if data.engine.database.is_exist(data.storage["site"] + " " + str(data.message["id"])):
		pass
	else:
		if data.message["st"] == "copart":
			answer = site_support.append_car(data, copart_answer=copart_info)
		else:
			answer = site_support.append_car(data, iaai_info=iaai_answer)
		data.engine.database.append_id(int(answer["product"]["id"]),
									   data.message["st"] + " " + str(data.message["id"]))
	data.message = message
	query(data, message, is_group=True, is_by_id=True)


@Step(bot.callback_handler, "id", "mr")
def callback_ctg_view_mr(data):
	copart_info = None
	if data.message["st"] == "copart":
		copart_info = copart.Get_Car_Info(int(data.message["id"]))
		desc = add_description_copart(data, copart_answer=copart_info["data"]["lotDetails"], clear=True)
	else:
		iaai_info = ProductsSortingModule.take_iaai_info(data.message["id"])
		desc = add_description_iaai(data, iaai_info=iaai_info, clear=True)
	keyboard = InlineKeyboardMarkup(
		[[InlineKeyboardButton(data.engine.data.Get("buttons", "Checkout"), callback_data=data.engine.Callback_Data(
			{"i": "id", "s": "buy", "id": data.message["id"],"st": data.message["st"], "p": data.message["p"]}))]])

	message =  desc
	if data.message["st"] == "copart":
		message += "\n\n" + str(copart_info["data"]["lotDetails"]["lat"])
	data.engine.Send_Message(data, text="Подробное поисание:", keyboard=("listing_2"))
	data.engine.Send_Message(data, text=message, keyboard=keyboard)



@Step(bot.callback_handler, "id", "ph")
def callback_ctg_view_ph(data):
	log.I(data.engine.callback_handler.globalTrigers)
	Send_Product_Id_Branch(data, int(data.message["id"]), data.message["st"], int(data.message["p"]) + 1)


# WORKING WITH ID
############################################################################################################################


@Step(bot.handler, "find", "by_id")
def main_start(data):
	if data.type == Handle_Triger():
		if data.message[2] == "copart":
			data.storage["site"]="copart"
			data.storage["id_of_car"]=data.message[3]
			answer=copart.Get_Car_Info(int(data.message[3]))
			data.storage["photo_id"] = 0
			send_product(data,copart_answer=answer,keyboard_type="Static")
		if data.message[2] == "iaai":
			data.storage["site"]="iaai"
			data.storage["id_of_car"]=data.message[3]
			answer=copart.Get_Car_Info(int(data.message[3]))
			data.storage["photo_id"] = 0
			send_product(data,iaai_answer=answer,keyboard_type="Static")
	else:
		if data.message.find("Еще фото")!=-1 :
			if len(data.storage["car_images"])>data.storage["photo_id"]+1:
				data.storage["photo_id"] +=1
			else:
				data.storage["photo_id"] = 0
			send_product(data)


@Step(bot.handler, "find", "query_mobile")
def main_start(data):
	if data.type == Handle_Triger():
		data.message=data.message[2:]
		query(data, data.message)
	else:
		pass



@Step(bot.handler, "find", "check_prise")
def main_start(data):
	if data.type == Handle_Triger():
		data.storage["AutoRia_attributes"]={}
		keyboard = []
		keyboard.append([data.engine.data.Get("buttons", "back"), data.engine.data.Get("buttons", "no_matter")])
		prise = 0
		i = 0
		while prise < 30000:
			if i == 0:
				keyboard.append([])
			keyboard[len(keyboard) - 1].append(str(prise) + " - " + str(prise + 5000))
			prise += 5000
			i += 1
			if i == 2:
				i = 0
		if i == 0:
			keyboard.append([])
		keyboard[len(keyboard) - 1].append("30000 - 80000")
		keyboard.append([data.engine.data.Get("buttons", "back"), data.engine.data.Get("buttons", "no_matter")])
		data.engine.Send_Message(data, text=data.Get_Answer("find", "prise_auto"),
								 keyboard=keyboard)
	else:
		if data.message == data.engine.data.Get("buttons", "back"):
			return Go_To("main", "start")
		if data.message == data.engine.data.Get("buttons", "menu"):
			return Go_To("main", "start")
		if data.message == data.engine.data.Get("buttons", "no_matter"):
			data.storage["finding_list"]["min_prise"] = 0
			data.storage["finding_list"]["max_prise"] = 80000
			return Go_To("find", "check_mark")
		else:
			prises = data.message.split("-")
			data.storage["finding_list"]["min_prise"] = int(prises[0])
			data.storage["finding_list"]["max_prise"] = int(prises[1])
			return Go_To("find", "check_mark")


@Step(bot.handler, "find", "check_mark")
def main_start(data):
	if data.type == Handle_Triger():
		send_attributes(data, 0, 'Марка', "mark_auto")

	else:
		if data.message == data.engine.data.Get("buttons", "back"):
			data.storage["finding_list"]["min_prise"] = 0
			data.storage["finding_list"]["max_prise"] = 80000
			return Go_To("find", "check_prise")
		elif data.message == data.engine.data.Get("buttons", "all"):
			data.storage["finding_list"]["mark"] = None
			return Go_To("find", "check_year")

		elif data.message == data.engine.data.Get("buttons", "give_found"):
			return Go_To("find", "look")
		else:
			Auto_Ria.mark(data)
			data.storage["finding_list"]["mark"] = data.message
			return Go_To("find", "check_model")


@Step(bot.handler, "find", "check_model")
def main_start(data):
	if data.type == Handle_Triger():
		send_attributes(data, 0, 'Модель', "model_auto")
	else:
		if data.message == data.engine.data.Get("buttons", "back"):
			data.storage["AutoRia_attributes"]["mark"]=None
			data.storage["finding_list"]["mark"] = None
			return Go_To("find", "check_mark")
		if data.message == data.engine.data.Get("buttons", "all"):
			return Go_To("find", "check_year")
		elif data.message == data.engine.data.Get("buttons", "give_found"):
			return Go_To("find", "look")
		else:
			Auto_Ria.model(data)
			data.storage["finding_list"]["model"] = data.message
			if data.storage["finding_list"]["type"] == data.engine.data.Get("buttons", "special"):
				return Go_To("find", "look")
			return Go_To("find", "check_year")


@Step(bot.handler, "find", "check_year")
def main_start(data):
	if data.type == Handle_Triger():
		send_attributes(data, 0, 'Год', "year_auto")
	else:
		if data.message == data.engine.data.Get("buttons", "back"):
			data.storage["AutoRia_attributes"]["model"]=None
			data.storage["finding_list"]["model"] = None
			return Go_To("find", "check_model")
		if data.message == data.engine.data.Get("buttons", "all"):
			return Go_To("find", "check_way")

		elif data.message == data.engine.data.Get("buttons", "give_found"):
			return Go_To("find", "look")
		else:
			data.storage["finding_list"]["year"] = data.message
			return Go_To("find", "check_way")


@Step(bot.handler, "find", "check_way")
def main_start(data):
	if data.type == Handle_Triger():
		data.engine.Send_Message(data, text=data.Get_Answer("find", "chose_way"), keyboard=("chose_way"))
	else:
		if data.message == data.engine.data.Get("buttons", "continue"):
			return Go_To("find", "check_run")
		elif data.message == data.engine.data.Get("buttons", "give_found"):
			return Go_To("find", "look")

@Step(bot.handler, "find", "check_run")
def main_start(data):
	# hz potom nahuiARY
	if data.type == Handle_Triger():
		# answers = wcapi.get("products/attributes/10/terms").json()
		keyboard = []
		keyboard.append([data.engine.data.Get("buttons", "give_found")])
		keyboard.append([data.engine.data.Get("buttons", "back"), data.engine.data.Get("buttons", "no_matter")])
		prise = 0
		i = 0
		while prise < 30000:
			if i == 0:
				keyboard.append([])
			keyboard[len(keyboard) - 1].append(str(prise) + " - " + str(prise + 5000))
			prise += 5000
			i += 1
			if i == 2:
				i = 0
		if i == 0:
			keyboard.append([])
		keyboard[len(keyboard) - 1].append("30000 - 120000")
		keyboard.append([data.engine.data.Get("buttons", "no_matter")])
		message = data.engine.Send_Message(data, text="По запросу найдено: " + "Загрузка ⏱").message_id
		data.engine.Send_Message(data, text= data.Get_Answer("find","racing_auto"),keyboard=keyboard)
		thread = threading.Thread(target=change, args=[data, message])
		thread.start()
	else:
		if data.message == data.engine.data.Get("buttons", "back"):
			data.storage["finding_list"]["year"] = None
			return Go_To("find", "check_year")
		if data.message == data.engine.data.Get("buttons", "no_matter"):
			data.storage["finding_list"]["min_run"] = None
			data.storage["finding_list"]["max_run"] = None
			return Go_To("find", "chack_transmission_car")
		elif data.message == data.engine.data.Get("buttons", "give_found"):
			return Go_To("find", "look")
		else:
			prises = []
			prises = data.message.split("-")
			data.storage["finding_list"]["min_run"] = int(prises[0])
			data.storage["finding_list"]["max_run"] = int(prises[1])
			return Go_To("find", "chack_transmission_car")


@Step(bot.handler, "find", "chack_transmission_car")
def main_start(data):
	if data.type == Handle_Triger():
		send_attributes(data, 0, 'Коробка', "transmission_auto")
	else:
		if data.message == data.engine.data.Get("buttons", "back"):
			data.storage["finding_list"]["min_run"] = None
			data.storage["finding_list"]["max_run"] = None
			return Go_To("find", "check_run")
		if data.message == data.engine.data.Get("buttons", "all"):
			data.storage["finding_list"]["transmission"] = None
			return Go_To("find", "chack_kuzov_car")
		elif data.message == data.engine.data.Get("buttons", "give_found"):
			return Go_To("find", "look")
		else:
			data.storage["finding_list"]["transmission"] =ProductsSortingModule.get_real_name(data.message)
			return Go_To("find", "chack_kuzov_car")


@Step(bot.handler, "find", "chack_kuzov_car")
def main_start(data):
	if data.type == Handle_Triger():
		send_attributes(data, 0, 'Тип кузова', "kuzov_auto")
	else:
		if data.message == data.engine.data.Get("buttons", "back"):
			data.storage["finding_list"]["transmission"] = None
			return Go_To("find", "chack_transmission_car")
		if data.message == data.engine.data.Get("buttons", "all"):
			return Go_To("find", "chack_toil_car")

		elif data.message == data.engine.data.Get("buttons", "give_found"):
			return Go_To("find", "look")
		else:
			data.storage["finding_list"]["kuzov"] = ProductsSortingModule.get_real_name(data.message)
			return Go_To("find", "chack_toil_car")


@Step(bot.handler, "find", "chack_toil_car")
def main_start(data):
	if data.type == Handle_Triger():
		send_attributes(data, 0, 'Тип топлива', "oil_auto")
	else:
		if data.message == data.engine.data.Get("buttons", "back"):
			data.storage["finding_list"]["kuzov"] = None
			return Go_To("find", "chack_kuzov_car")
		if data.message == data.engine.data.Get("buttons", "all"):
			return Go_To("find", "look")
		elif data.message == data.engine.data.Get("buttons", "give_found"):
			return Go_To("find", "look")
		else:
			data.storage["finding_list"]["oil"] = ProductsSortingModule.get_real_name(data.message)
			filters = ""
			if data.storage["finding_list"]["oil"] != None:
				pass
			return Go_To("find", "look")


@Step(bot.callback_handler, "main", "about_us")
def callback_ctg_view(data):
	keyboard = []
	keyboard.append([{"type": "url", "text": "{buttons[site]}", "url": "http://caramerica.com.ua/"}])
	data.engine.Send_Message(data, text=data.Get_Answer("main", "about_company"),
							 keyboard=data.engine.Callback_Keyboard(keyboard))


@Step(bot.callback_handler, "main", "maybee_start")
def callback_ctg_view(data):
	data.engine.Set_Position_Active(data, "main", "start")
@Step(bot.callback_handler, "main", "help")
def callback_ctg_view(data):

	data.engine.Send_Message(data, text=data.Get_Answer("main", "help"), keyboard= data.engine.data.Get("keyboards", "cancel"))
	data.engine.Set_Position_Passive(data, "help", "mennager")

@Step(bot.handler,"main", "maybe_start")
def callback_ctg_view(data):
	if data.type == Handle_Triger():
		pass
	else:
		if data.message == data.engine.data.Get("buttons", "menu"):
			return Go_To("main", "start")
		if data.message == data.engine.data.Get("buttons", "find"):
			return Go_To("find", "check_prise")

@Step(bot.handler, "find", "look")
def callback_ctg_view(data):
	copart_answer=ProductsSortingModule.take_copart_answer(data, page=0)#maybe here
	iaai_answer=ProductsSortingModule.take_iaai_answer(data, page=1)
	if data.type == Handle_Triger():
		data.engine.database.append_attributes_to_user_histiory(data)
		data.storage["car_id"]=0
		data.storage["copart_cars_amount"]=int(copart_answer["data"]["results"]["totalElements"])
		if iaai_answer==None:
			data.storage["iaai_cars_amount"] =0
		else:
			data.storage["iaai_cars_amount"]=int(iaai_answer["amount"])
		if data.storage["copart_cars_amount"]>0:
			data.storage["site"] = "copart"
		else:
			data.storage["site"] = "iaai"
		data.storage["photo_id"]=0
		if data.storage["iaai_cars_amount"]+data.storage["copart_cars_amount"]==0:
			data.engine.Send_Message(data,text=data.Get_Answer("find","nothing"),keyboard=("Nothing"))
			data.engine.Set_Position_Passive(data,"main", "maybe_start")
		else:
			send_product(data,copart_answer=copart_answer,iaai_answer=iaai_answer)

	else:
		if data.message == data.engine.data.Get("buttons", "menu"):
			message = ""
			message += "НЕ Оформленая заявка\n" + data.storage["site"] + " " + str(data.storage[
				"id_of_car"]) + "\n" + convert_finding_list(data)
			query(data, message, true_sight=False)
			return Go_To("main", "start")
		elif data.message == data.engine.data.Get("buttons", "back"):
			data.storage["photo_id"] = 0
			if data.storage["car_id"]==0:
				if data.storage["copart_cars_amount"]==0 :
					data.storage["car_id"] =data.storage["iaai_cars_amount"]
				elif data.storage["iaai_cars_amount"]==0:
					data.storage["car_id"] = data.storage["copart_cars_amount"]-1
				else:
					data.storage["car_id"]=data.storage["copart_cars_amount"] + data.storage["iaai_cars_amount"]-1
			else:
				data.storage["car_id"]-=1
		elif data.message == data.engine.data.Get("buttons", "next"):
			data.storage["photo_id"] = 0
			if data.storage["copart_cars_amount"]==0 and data.storage["car_id"]<data.storage["iaai_cars_amount"]:
				data.storage["car_id"] += 1
			elif data.storage["iaai_cars_amount"]==0 and data.storage["car_id"] + 1<data.storage["copart_cars_amount"]:
				data.storage["car_id"] += 1
			elif int(data.storage["car_id"]) + 1 < data.storage["copart_cars_amount"] + data.storage["iaai_cars_amount"]:
				data.storage["car_id"] += 1
			else:
				data.storage["car_id"] = 0
		if data.storage["copart_cars_amount"] > data.storage["car_id"]:
			data.storage["site"] = "copart"
		else:
			data.storage["site"] = "iaai"
		send_product(data)

@Step(bot.callback_handler, "l", "more")
def callback_ctg_view(data):
	if data.message["t"]=="c":
		data.storage["site"]="copart"
		add_description_copart(data,data.message["id"])
	else:
		data.storage["site"] = "iaai"
		add_description_iaai(data,data.message["id"])
	data.storage["car_id"] = int(data.message["id2"])
	data.storage["id_of_car"] = int(data.message["id"])
	data.engine.Set_Position_Active(data, "v", "order")



@Step(bot.callback_handler, "l", "photo")
def callback_ctg_view(data):
	data.storage["id_of_car"] = int(data.message["id"])
	if len(data.storage["car_images"]) > data.storage["photo_id"] + 1:
		data.storage["photo_id"] += 1
	else:
		data.storage["photo_id"] = 0
	data.storage["car_id"] = int(data.message["id2"])
	send_product(data)

@Step(bot.callback_handler, "found", "buy")
def callback_ctg_view(data):
		data.storage["id_of_car"]=data.message["id"]
		data.storage["site"] = data.message["site"]
		data.engine.Set_Position_Active(data, "v", "phone")

@Step(bot.handler, "v", "order")
def callback_ctg_view(data):
	if data.type == Handle_Triger():
		keyboard = InlineKeyboardMarkup(
			[[InlineKeyboardButton(data.engine.data.Get("buttons", "Checkout"), callback_data=data.engine.Callback_Data(
				{"i": "found", "s": "buy","id":str(data.storage["id_of_car"])}))]])
		message= "Описание\n\n"+data.storage["description"]+"\n\n"+data.storage["price"]
		data.engine.Send_Message(data, text=message, keyboard=keyboard)
		data.engine.Set_Position_Passive(data, "find", "look")
	else:
		pass

@Step(bot.handler, "v", "phone")
def callback_ctg_view(data):
	if data.type == Handle_Triger():
		message=""
		message+=data.storage["site"]+" "+data.storage["id_of_car"]
		data.message=data.storage["site"]+" "+data.storage["id_of_car"]
		query(data,message,is_group=True)

		if data.storage["site"] == "copart":
			add_description_copart(data, data.storage["id_of_car"])
			car_images = copart.Get_Car_Images(str(data.storage["id_of_car"]))["data"]["imagesList"]["FULL_IMAGE"]
			car_images = ProductsSortingModule.create_image_list(car_images)
		else:
			iaai_info = ProductsSortingModule.take_iaai_info(str(data.storage["id_of_car"]))
			add_description_iaai(data, data.storage["id_of_car"])
			car_images = iaaa.Get_All_Images(iaai_info["stock_id"])
		keyboard = InlineKeyboardMarkup(
			[[InlineKeyboardButton(data.engine.data.Get("buttons", "op"), callback_data=data.engine.Callback_Data(
				{"i": "found", "s": "site", "id": data.storage["id_of_car"], "site": data.storage["site"]}))]])
		data.engine.Send_Photo(data, link=car_images[0],chat_id=admin_chat_id)
		data.engine.Send_Message(data, keyboard=keyboard, text="\n"+data.storage["description"],chat_id=admin_chat_id)



@Step(bot.callback_handler, "found", "site")
def callback_ctg_view(data):
		data.storage["id_of_car"]=data.message["id"]
		data.storage["site"]=data.message["site"]
		if data.engine.database.is_exist(data.storage["site"]+" "+str(data.storage["id_of_car"])):
			data.engine.Send_Message(data, text="Такой лот уже есть на сайте",chat_id=admin_chat_id)
		else:
			if data.storage["site"] == "copart":

				copart_answer = ProductsSortingModule.get_copatr_by_id(data.storage["id_of_car"])
				answer = site_support.append_car(data, copart_answer=copart_answer)
			else:
				iaai_answer = ProductsSortingModule.take_iaai_info(data.storage["id_of_car"])
				answer = site_support.append_car(data, iaai_info=iaai_answer)
			data.engine.database.append_id(int(answer["product"]["id"]),
										   data.storage["site"] + " " + str(data.storage["id_of_car"]))
			data.engine.Send_Message(data, text="Лот опубликован на сайте",chat_id=admin_chat_id)

def create_keyboard(answers, column_amount):
	amount_of_buttons_in_row = 0
	keyboard = []
	for answer in answers:
		lenght = len(keyboard) - 1
		if amount_of_buttons_in_row == 0:
			keyboard.append([])
			lenght += 1
		amount_of_buttons_in_row += 1
		keyboard[lenght].append(str(answer))
		if amount_of_buttons_in_row == column_amount:
			amount_of_buttons_in_row = 0
	return keyboard

def change(data,message):
	amount = ProductsSortingModule.take_copart_amount(data)
	amount += ProductsSortingModule.take_iaai_amount(data)
	data.engine.Edit_Message(data, message_id=message, text="По запросу найдено: " + str(amount))

def send_attributes(data, id, attribute, attribute_key):
	data.storage["keyboard_id"] = id
	keyboard_list, amount = ProductsSortingModule.add_copart_atributes(data,  attribute)
	ProductsSortingModule.add_iaai_atributes(data, attribute,keyboard_list)
	keyboard = []
	if attribute_key !="mark_auto" and attribute_key !="model_auto":
		keyboard.append([data.engine.data.Get("buttons", "give_found")])
	keyboard.append([data.engine.data.Get("buttons", "back"),data.engine.data.Get("buttons", "menu_g")])
	keyboard.append([data.engine.data.Get("buttons", "all")])
	keyboard2 = create_keyboard(keyboard_list, 3)
	keyboard += keyboard2
	keyboard.append([data.engine.data.Get("buttons", "more"), data.engine.data.Get("buttons", "all")])
	message=data.engine.Send_Message(data,text="По запросу найдено: " +"Загрузка ⏱" ).message_id
	data.engine.Send_Message(data, text=data.Get_Answer("find",attribute_key), keyboard=keyboard)
	thread = threading.Thread(target=change, args=[data,message])
	thread.start()

	#data.engine.Send_Message(data,text=str(ProductsSortingModule.take_copart_amount(data)))
	#data.engine.Send_Message(data,text=str(ProductsSortingModule.take_iaai_amount(data)))


def send_product(data, copart_answer=None,iaai_answer=None,keyboard_type="Normal",chat_id=None):
	message = ""
	if data.storage["copart_cars_amount"] > data.storage["car_id"] or (keyboard_type=="Static" and copart_answer!=None):
		if copart_answer == None:
			copart_answer = ProductsSortingModule.take_copart_answer(data, page=int(data.storage["car_id"]))
		id = copart_answer["data"]["results"]["content"][0]["ln"]
		data.storage["car_images"] = copart.Get_Car_Images(str(id))["data"]["imagesList"]["FULL_IMAGE"]
		try:
			data.storage["car_images"] = copart.Get_Car_Images(str(id))["data"]["imagesList"]["FULL_IMAGE"]
		except:
			data.storage["photo_id"] = 0
			if data.storage["car_id"] + 1 < data.storage["copart_cars_amount"] + data.storage["iaai_cars_amount"]:
				data.storage["car_id"] += 1
			else:
				data.engine.Send_Message(data,text="К сожалению, найденые машини не подходят для показа из за отсутствия обязательной информации.")
				data.engine.Set_Position_Active(data, "main", "start")
				return
			send_product(data)
			return
		data.storage["car_images"] =ProductsSortingModule.create_image_list(data.storage["car_images"])
		data.storage["id_of_car"] = str(copart_answer["data"]["results"]["content"][0].get("ln"))
		if copart_answer["data"]["results"]["content"][0].get("mkn") != None:
				message += " " + str(copart_answer["data"]["results"]["content"][0].get("mkn"))
		if copart_answer["data"]["results"]["content"][0].get("lm") != None:
				message += " " + str(copart_answer["data"]["results"]["content"][0].get("lm"))
		if copart_answer["data"]["results"]["content"][0].get("lcy") != None:
				message += " " + str(copart_answer["data"]["results"]["content"][0].get("lcy"))
		add_description_copart(data,copart_answer=copart_answer["data"]["results"]["content"][0])
	else:
		if iaai_answer == None:
			iaai_answer = ProductsSortingModule.take_iaai_answer(data,page=int(data.storage["car_id"])-int(data.storage["copart_cars_amount"]))
		if iaai_answer==None:
			data.engine.Send_Message(data,text="К сожалению, ничего не найдено")
			data.engine.Set_Position_Active(data,"main","start")
		data.storage["id_of_car"] = str(iaai_answer["items"][0]["id"])
		data.storage["car_images"] =iaaa.Get_All_Images(iaai_answer["items"][0]["stock_id"])


		message += iaai_answer["items"][0]["name"] + ' ' + str(iaai_answer["items"][0]["year"])
		iaai_info=ProductsSortingModule.take_iaai_info(iaai_answer["items"][0]["id"])
		add_description_iaai(data,iaai_info=iaai_info)
	keyboard = InlineKeyboardMarkup(
			[[InlineKeyboardButton(data.engine.data.Get("buttons", "Checkout"), callback_data=data.engine.Callback_Data(
				{"i": "found", "s": "buy","id":data.storage["id_of_car"] ,"site":data.storage["site"]}))],

			 [InlineKeyboardButton(data.engine.data.Get("buttons", "description"), callback_data=data.engine.Callback_Data(
				 {"i": "l", "s": "more","id":data.storage["id_of_car"],"id2":data.storage["car_id"],"t":data.storage["site"][0]}))],
			 [InlineKeyboardButton(data.engine.data.Get("buttons", "photos").format(
				  str(data.storage["photo_id"] + 1),
				  str(len(data.storage["car_images"]))), callback_data=data.engine.Callback_Data(
				  {"i": "l", "s": "photo","id":data.storage["id_of_car"],"id2":data.storage["car_id"]}))
			  ]
			 ])

	if keyboard_type=="Normal":

		autoria_prise = str(Auto_Ria.Get_price(data)["arithmeticMean"]).split(".")[0]
		site_prise = str(calculator.get_price(data))

		if autoria_prise!=None and autoria_prise!="None":

			if site_prise == "not found":
				random.seed()
				a = random.randint(20, 30)
				site_prise = str(int((int(autoria_prise) * (100 - a) / 10) // 10))
				data.storage["price"] = "\nЦена: {}$\nДешевле чем на рынке на {}% - AutoRia".format(str(int(float(site_prise))),
																									str(a))
				message += "\nЦена: {}$\nДешевле чем на рынке на {}% - AutoRia".format(str(int(float(site_prise))), str(a))
			else:
				percent = (int(float(site_prise)) / int(float(autoria_prise)) * 100) // 1
				data.storage["price"] = "\nЦена: {}$\nДешевле чем на рынке на {}% - AutoRia".format(str(int(float(site_prise))),
																									str(percent))
				message += "\nЦена: {}$\nДешевле чем на рынке на {}% - AutoRia".format(str(int(float(site_prise))), str(percent))
	if chat_id==None:
		data.engine.Send_Photo(data, link=data.storage["car_images"][data.storage["photo_id"]],keyboard=("listing"))
		data.engine.Send_Message(data, text=message, keyboard=keyboard)
	else:
		message=""
		if copart_answer!=None:
			message += "\nЦена: " + str(copart_answer["data"]["results"]["content"][0]["la"])
			message += "\nhttps://www.copart.com/lot/" + str(copart_answer["data"]["results"]["content"][0]["ln"])
		data.engine.Send_Photo(data, link=data.storage["car_images"][data.storage["photo_id"]],chat_id=chat_id)
		data.engine.Send_Message(data, text=message+"\n"+data.storage["description"], chat_id=chat_id)





def add_description_copart(data, id=None, copart_answer=None,clear=False):
	if id != None:
		copart_answer = ProductsSortingModule.get_copatr_by_id(id)["data"]["lotDetails"]

	if data.storage.get("description")!=None:
		desc2 = data.storage["description"] + ""
	else:
		desc2 =""
	data.storage["description"] = ""
	if copart_answer.get("ld") != None:
		data.storage["description"] += " " + str(copart_answer.get("ld")) + "\n"
	if copart_answer.get("eng") != None:
		data.storage["description"] += "Двигатель: " + str(copart_answer.get("eng")) + "\n"
	if copart_answer.get("cy") != None:
		data.storage["description"] += "Количество цилиндров: " + str(copart_answer.get("cy")) + "\n"
	if copart_answer.get("tmtp") != None:
		data.storage["description"] += "Трансмиссия: " + str(copart_answer.get("tmtp")) + "\n"
	if copart_answer.get("drv") != None:
		data.storage["description"] += "Привод: " + str(copart_answer.get("drv")) + "\n"
	if copart_answer.get("ft") != None:
		data.storage["description"] += "Топливо: " + str(copart_answer.get("ft")) + "\n"
	if clear:
		d1=data.storage["description"]+""
		data.storage["description"]=desc2
		return d1


def add_description_iaai(data, id=None, iaai_info=None,clear=False):
	if id != None:
		iaai_info = ProductsSortingModule.take_iaai_info(id)
	if data.storage.get("description") != None:
		desc2 = data.storage["description"] + ""
	else:
		desc2 = ""
	data.storage["description"] = ""
	if iaai_info.get("name") != None:
		data.storage["description"] += iaai_info["name"] + "\n"
	if iaai_info.get("year") != None:
		data.storage["description"] += iaai_info["year"] + "\n"
	if iaai_info.get("Engine") != None:
		data.storage["description"] += "Двигатель: " + iaai_info["Engine"] + "\n"
	if iaai_info.get("Cylinders") != None:
		data.storage["description"] += "Количество цилиндров: " + iaai_info["Cylinders"] + "\n"
	if iaai_info.get("Body Style") != None:
		data.storage["description"] += iaai_info["Body Style"] + "\n"
	if iaai_info.get("Transmission") != None:
		data.storage["description"] += "Трансмиссия: " + iaai_info["Transmission"] + "\n"
	if iaai_info.get("Drive Line Type") != None:
		data.storage["description"] += "Привод: " + iaai_info["Drive Line Type"] + "\n"
	if iaai_info.get("Fuel Type") != None:
		data.storage["description"] += "Топливо: " + iaai_info["Fuel Type"] + "\n"
	if clear:
		d1=data.storage["description"]+""
		data.storage["description"]=desc2
		return d1






def query(data, text,true_sight=True,is_group=False, is_by_id=False):
	connect = bot.database.Get_Connection()
	cursor = connect.cursor()
	data.engine.database.create_row_question(user_id=data.user_id, message=data.message[1:])
	local_b = data.engine.database.get_last_row(user_id=data.user_id)
	keyboard = InlineKeyboardMarkup(
		[[InlineKeyboardButton(data.engine.data.Get("buttons", "help_answer"), callback_data=data.engine.Callback_Data(
			{"i": "help", "s": "answer", "P": "T", "id": str(local_b["id"])}))],
		 [InlineKeyboardButton(data.engine.data.Get("buttons", "help_phone_query"), callback_data=data.engine.Callback_Data(
			 {"i": "help", "s": "telephone", "P": "T", "id": str(data.user_id)}))],
		 [InlineKeyboardButton(data.engine.data.Get("buttons", "help_history"), callback_data=data.engine.Callback_Data(
			 {"i": "help", "s": "history", "id": str(data.user_id)}))]
		 ])
	text1 = ""
	if data.storage.get("message_subtext") != None:
		text1 = data.storage["message_subtext"] + "\n"
	data.storage["message_subtext"] = None
	message =  data.Get_Answer("help", "new_from")
	user= data.engine.database.Get_User_Info(data.user_id)
	message += user["first_name"] +" "+ user.get("last_name") +text1+ "(#" + str(data.user_id) + ")" + "\nЗміст: " + text
	message_id = ""
	if is_group:
		if not is_by_id:
			send_product(data, chat_id="@CarAmericaUA")
		message_id = data.engine.Send_Message(data,text=message + "\n" + data.storage["description"],keyboard=keyboard,chat_id=admin_chat_id)
		#data.engine.Send_Message(data, text=message, chat_id="@CarAmericaUA")
	else:
		message_id = data.engine.Send_Message(data, text=message ,keyboard=keyboard,chat_id=admin_chat_id)
	date_time = datetime.datetime.now()
	date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
	cursor.execute("UPDATE help SET message_id='%s',question_time='%s'  WHERE id=%s" % (
		message_id["message_id"], date_time, local_b["id"]))
	connect.commit()
	if true_sight:
		data.engine.Send_Message(data, text="Ваша заявка отправлена\nЗадайте вопрос, если хотите, или нажмите \"Отмена\" для выхода в главное меню.",
								 keyboard=data.Get_Keyboard(name="main_call"))
		data.engine.Set_Position_Passive(data, "help", "mennager", MAIN_HANDLER)


def convert_list_to_string(dict_obj):
	string_obj="{"
	for key in dict_obj.keys():
		string_obj+=key+":"+str(dict_obj[key])+", "
	string_obj+="}"
	return string_obj

########################################################################################################
#connection

def query_CRM(dat):
	pass

def email(data):
	pass




def Get_product(data,page_id,product_id):
	values=data.storage["finding_list"]
	products=wcapi.get("products?filter[pa_availability]=v-ukraine&filter[pa_make]=audi").json()
bot.Start(timeout=999999, work_time=1803)
