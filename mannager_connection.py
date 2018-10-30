from BotEngine.TelegramBot import *
import time
import datetime
import json
from BotEngine.ViberBot import *
from BotEngine.FacebookBot import *

data = json.loads(open("/home/server00/TelegramBots/CarAmerica/" + 'telegram.json', 'r', encoding='utf-8').read())
#viber_bot = ViberBot("/home/kdspnklg/WebhooksGrushaTech/viber_bots/bots/MKitch/", full_path=True)
#facebook_bot = FacebookBot("/home/kdspnklg/WebhooksGrushaTech/facebook_bots/bots/Cosmetico/", full_path=True)

import sys

#sys.path.insert(0, "/home/kdspnklg/WebhooksGrushaTech/viber_bots/bots/MKitch/")
#import ConnectionManager

#viber_bot = ConnectionManager.manager_connection(viber_bot, 410962782)

#sys.path.insert(0, "/home/kdspnklg/WebhooksGrushaTech/facebook_bots/bots/Cosmetico/")
#import facebook_manager_connection

#facebook_bot = facebook_manager_connection.manager_connection(facebook_bot, 410962782)

host = data["settings"]["database"]["host"]
user = data["settings"]["database"]["user"]
password = data["settings"]["database"]["password"]
db = data["settings"]["database"]["db"]


def manager_connection(bot, admin_chat_id, viber_api_token=None, facebook_api_token=None, avatar=None, bot_name=None):
	# viber_bot = ViberBot(api_token=viber_api_token, avatar=avatar, bot_name=bot_name)
	# facebook_bot = FacebookBot(api_token=facebook_api_token)

	database = Database({"host": "localhost", "user": user, "password": password, "db": db, "prefix": ""})
	global_is_call_me = True
	# ----------------------------------------------------------------------------------------------------------------
	bot.answers.content["help"] = {
		"input": "Задайте, будь-ласка, Ваше питання.",
		"great": "Добре, очікуйте відповіді будь-ласка. Я передав Ваше питання людині.",
		"otvet": "Уведіть Вашу відповідь:",
		"push_telephone_button": "Натисніть кнопку \"📞 Відправити номер телефону\" нижче аби відправити Ваш номер нашому менеджеру.",
		"give_phone_to_mennager": "Наш менеджер захотів зателефонувати Вам, натисніть кнопку \"📞 Відправити номер телефону\" нижче, якщо згодні, або дайте текстову відповідь.",
		"send_phone_to_mennager": "Наш менеджер захотів зателефонувати Вам, впишіть номер телефону, якщо згодні, або дайте текстову відповідь.",
		"send_phone": "Впишіть номер телефону,або дайте текстову відповідь."

	}
	bot.data.content["static_data"]["callback"]["instructions"].append({"name": "help", "steps": [
		{"name": "answer"},
		{"name": "telephone"},
		{"name": "history"},
		{"name": "call_me"},
		{"name": "user_answer"}
	]})
	bot.data.content["instructions"].append({
		"name": "help",
		"steps": [{
			"name": "mennager"
		}, {
			"name": "answer"
		}]
	})
	bot.data.content["keyboards"]["main_call"] = [[["📞 Зателефонуйте мені", "request_contact"]], ["{buttons[cancel]}"]]
	bot.data.content["keyboards"]["call_me"] = [[["📞 Відправити номер телефону", "request_contact"]],
												["{buttons[cancel]}"]]


	bot.data.content["keyboards"]["cancel"] = [["{buttons[cancel]}"]]

	@Database_(database)
	def create_row_question(user_id, message):
		connect = database.Get_Connection()
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

	# ----------------------------------------------------------------------------------------------------------------
	@Database_(database)
	def get_list_of_messeging(user_id):
		connect = database.Get_Connection()
		cursor = connect.cursor()
		cursor.execute("SELECT * FROM users WHERE id=%s" % (int(user_id)))
		local_a = cursor.fetchone()
		name = local_a["first_name"]
		last_name = local_a["last_name"]
		cursor.execute("SELECT * FROM help WHERE user_id=%s" % (int(user_id)))
		local_a = cursor.fetchone()
		message = "Історія листування з "
		message += name + last_name + " (#" + str(user_id) + ")" + "\n"
		while local_a != None:
			message += "Питання " + "[" + str(local_a["question_time"]) + "]" + ":\n" + local_a["question"] + "\n"
			if local_a["answer"] != "":
				message += "Відповідь " + "[" + str(local_a["question_time"]) + "]" + ":\n" + local_a["answer"] + "\n"
			message += "------------------\n"
			local_a = cursor.fetchone()
		return message

	# ----------------------------------------------------------------------------------------------------------------

	@Database_(database)
	def get_last_row(user_id):
		connect = database.Get_Connection()
		cursor = connect.cursor()
		cursor.execute("SELECT * FROM help WHERE user_id=%s" % (user_id))
		local_a = cursor.fetchone()
		local_b = 0
		while local_a != None:
			local_b = local_a
			local_a = cursor.fetchone()
		return local_b

	# ----------------------------------------------------------------------------------------------------------------
	@Step(bot.handler, "help", "mennager")
	def main_start(data):
		connection = data.engine.database.Get_Connection()
		cursor = connection.cursor()
		if data.type == Handle_Triger():
			if global_is_call_me:
				data.engine.Send_Message(data, text=data.Get_Answer("help", "input"),
										 keyboard=data.Get_Keyboard(name="main_call"))
			else:
				data.engine.Send_Message(data, text=data.Get_Answer("help", "input"),
										 keyboard=data.Get_Keyboard(name="cancel"))
		else:
			if data.update.message.contact != None:
				message = "Користувач "
				name = data.update.message.from_user.first_name + " "
				last_name = ""
				if data.update.message.from_user.last_name != None:
					last_name = data.update.message.from_user.last_name + " "
				message += name + last_name + "(#" + str(
					data.user_id) + ")" + " захотів, щоб ви йому зателефонували: " + data.update.message.contact.phone_number
				data.engine.Send_Message(data, text=message, chat_id=admin_chat_id)
				data.engine.Send_Message(data, text=data.Get_Answer("help", "great"),
										 keyboard=data.Get_Keyboard(name="main"))

			else:
				database.create_row_question(user_id=data.user_id, message=data.message)
				data.engine.Send_Message(data, text=data.Get_Answer("help", "great"),
										 keyboard=data.Get_Keyboard(name="main"))
				local_b = database.get_last_row(user_id=data.user_id)
				keyboard = InlineKeyboardMarkup(
					[[InlineKeyboardButton("Відповісти", callback_data=data.engine.Callback_Data(
						{"i": "help", "s": "answer", "P": "T", "id": str(local_b["id"])}))],
					 [InlineKeyboardButton("Запит номену телефону", callback_data=data.engine.Callback_Data(
						 {"i": "help", "s": "telephone", "P": "T", "id": str(data.user_id)}))],
					 [InlineKeyboardButton("Історія листування", callback_data=data.engine.Callback_Data(
						 {"i": "help", "s": "history", "id": str(data.user_id)}))]
					 ])

				message = "Нове повідомленя від "
				name = data.update.message.from_user.first_name + " "
				last_name = ""
				if data.update.message.from_user.last_name != None:
					last_name = data.update.message.from_user.last_name + " "
				message += name + last_name + "(#" + str(data.user_id) + ")" + "\nЗміст: " + data.message
				message_id = data.engine.Send_Message(data, text=message, keyboard=keyboard, chat_id=admin_chat_id)
				date_time = datetime.datetime.now()
				date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
				cursor.execute("UPDATE help SET message_id='%s',question_time='%s'  WHERE id=%s" % (
					message_id["message_id"], date_time, local_b["id"]))
				connection.commit()
			data.engine.Set_Position_Passive(data, "main", "menu", MAIN_HANDLER)

		# ----------------------------------------------------------------------------------------------------------------

	@Step(bot.callback_handler, "help", "answer")
	def callback_main_start(data):
		data.storage["ask_id"] = int(data.message["id"])
		data.storage["platform"] = data.message["P"]
		if data.storage["platform"] == "V":
			data.storage["version"] = data.message["V"]
		data.engine.Send_Message(data, text=data.Get_Answer("help", "otvet"),
								 keyboard=data.Get_Keyboard(name="cancel"))
		data.engine.Set_Position_Passive(data, "help", "answer", MAIN_HANDLER)

	# ----------------------------------------------------------------------------------------------------------------
	@Step(bot.callback_handler, "help", "telephone")
	def callback_main_start(data):
		print (data.message)
		if data.message["P"] == "T":
			data.engine.Send_Photo(data, link="https://grusha.tech/Cosmetico/telegram_telephone.jpeg")
			data.engine.Send_Message(data, text=data.Get_Answer("help", "give_phone_to_mennager"),
									 keyboard=data.Get_Keyboard(name="call_me"),
									 chat_id=data.engine.database.Get_User_Info(int(data.message["id"]))["chat_id"])
			buffer = data.engine.database.Get_Buffer(int(data.message["id"]))
			data.engine.handler.Set_Instruction(buffer, "help")
			data.engine.handler.Set_Step(buffer, "mennager")
			data.engine.database.Set_Buffer(int(data.message["id"]), buffer)
		elif data.message["P"] == "facebook":
			facebook_bot.Send_Callback_Keyboard(None, text=data.Get_Answer("help", "send_phone_to_mennager"),
												keyboard=["❌ Відміна"],
												callback=[{"i": "main", "s": "menu"}],
												chat_id=data.engine.database.Get_User_Info(int(data.message["id"]))[
													"chat_id"])
			buffer = data.engine.database.Get_Buffer(int(data.message["id"]))
			facebook_bot.handler.Set_Instruction(buffer, "help")
			facebook_bot.handler.Set_Step(buffer, "write_telephone")
			facebook_bot.database.Set_Buffer(int(data.message["id"]), buffer)
		else:
			if int(data.message["V"]) >= 3:
				keyboard = {
					"Type": "keyboard",
					"Buttons": [{
						"Columns": 6,
						"Rows": 1,
						"Text": "📞 Зателефонуйте мені",
						"TextSize": "medium",
						"TextHAlign": "center",
						"TextVAlign": "bottom",
						"ActionType": "share-phone",
						"ActionBody": "📞 Зателефонуйте мені",

					}, {
						"Columns": 6,
						"Rows": 1,
						"Text": "❌ Відміна",
						"TextSize": "medium",
						"TextHAlign": "center",
						"TextVAlign": "bottom",
						"ActionType": "reply",
						"ActionBody": "❌ Відміна",
					}]
				}
				viber_bot.Send_Message(None, text=data.Get_Answer("help", "send_phone"), min_api_version=3,
									   keyboard=keyboard,
									   chat_id=data.engine.database.Get_User_Info(int(data.message["id"]))["chat_id"])

				buffer = data.engine.database.Get_Buffer(int(data.message["id"]))
				viber_bot.handler.Set_Instruction(buffer, "help")
				viber_bot.handler.Set_Step(buffer, "mennager")
				viber_bot.database.Set_Buffer(int(data.message["id"]), buffer)

			else:
				viber_bot.Send_Message(None, text=data.Get_Answer("help", "send_phone"),
									   keyboard=[["❌ Відміна"]],
									   chat_id=data.engine.database.Get_User_Info(int(data.message["id"]))["chat_id"])
				buffer = data.engine.database.Get_Buffer(int(data.message["id"]))
				viber_bot.handler.Set_Instruction(buffer, "help")
				viber_bot.handler.Set_Step(buffer, "write_telephone")
				viber_bot.database.Set_Buffer(int(data.message["id"]), buffer)

	# ----------------------------------------------------------------------------------------------------------------
	@Step(bot.callback_handler, "help", "call_me")
	def callback_main_start(data):
		data.engine.Send_Photo(data, link="https://grusha.tech/Cosmetico/telegram_telephone.jpeg")

		data.engine.Send_Message(data, text=data.Get_Answer("help", "push_telephone_button"),
								 keyboard=data.Get_Keyboard(name="call_me"))
		data.engine.Set_Position_Passive(data, "help", "mennager", MAIN_HANDLER)

	# ----------------------------------------------------------------------------------------------------------------
	@Step(bot.callback_handler, "help", "user_answer")
	def callback_main_start(data):
		data.engine.Send_Message(data, text=data.Get_Answer("help", "otvet"),
								 keyboard=data.Get_Keyboard(name="cancel"))
		data.engine.Set_Position_Passive(data, "help", "mennager", MAIN_HANDLER)

	# ----------------------------------------------------------------------------------------------------------------
	@Step(bot.callback_handler, "help", "history")
	def callback_main_start(data):
		data.engine.Send_Message(data, text=database.get_list_of_messeging(user_id=data.message["id"]))

	# ----------------------------------------------------------------------------------------------------------------
	@Step(bot.handler, "help", "answer")
	def main_start(data):
		if data.type == Handle_Triger():
			pass
		else:
			connection = data.engine.database.Get_Connection()
			cursor = connection.cursor()
			date_time = datetime.datetime.now()
			date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
			cursor.execute("UPDATE help SET answer=%s,answer_time=%s WHERE id=%s",
						   (data.message, date_time, data.storage["ask_id"]))
			connection.commit()
			cursor.execute("SELECT * FROM help WHERE id=%s", (data.storage["ask_id"]))
			local_a = cursor.fetchone()
			if data.storage["platform"] == "T":
				keyboard = InlineKeyboardMarkup(
					[
						[InlineKeyboardButton("Запит номера телефону", callback_data=data.engine.Callback_Data(
							{"i": "help", "s": "telephone", "P": data.storage["platform"],
							 "id": str(local_a["user_id"])}))],
						[InlineKeyboardButton("Історія листування", callback_data=data.engine.Callback_Data(
							{"i": "help", "s": "history", "id": str(local_a["user_id"])}))]
					])
			elif data.storage["platform"] == "facebook":
				keyboard = InlineKeyboardMarkup(
					[
						[InlineKeyboardButton("Запит номера телефону", callback_data=data.engine.Callback_Data(
							{"i": "help", "s": "telephone", "P": data.storage["platform"],
							 "id": str(local_a["user_id"])}))],
						[InlineKeyboardButton("Історія листування", callback_data=data.engine.Callback_Data(
							{"i": "help", "s": "history", "id": str(local_a["user_id"])}))]
					])
			else:
				keyboard = InlineKeyboardMarkup(
					[
						[InlineKeyboardButton("Запит номера телефону", callback_data=data.engine.Callback_Data(
							{"V": str(data.storage["version"]), "i": "help", "s": "telephone",
							 "P": data.storage["platform"],
							 "id": str(local_a["user_id"])}))],
						[InlineKeyboardButton("Історія листування", callback_data=data.engine.Callback_Data(
							{"i": "help", "s": "history", "id": str(local_a["user_id"])}))]
					])

			data.engine.Edit_Message(data, local_a["message_id"], keyboard=keyboard)
			cursor.execute("SELECT * FROM users WHERE id=%s", (local_a["user_id"]))
			local_a = cursor.fetchone()
			answer = "Відповідь менеджера: " + data.message
			keyboard = 1
			if local_a["platform"] == "telegram":
				keyboard = InlineKeyboardMarkup(
					[[InlineKeyboardButton("Відповісти", callback_data=data.engine.Callback_Data(
						{"i": "help", "s": "user_answer", "P": "T"}))],
					 [InlineKeyboardButton("Зателефонуйте мені",
										   callback_data=data.engine.Callback_Data(
											   {"i": "help", "s": "call_me", "P": "T",
												"id": str(data.user_id)}))]
					 ])
			elif local_a["platform"] == "facebook":
				pass
			else:

				user_id = data.storage["ask_id"]
				keyboard = {
					"Type": "rich_media",
					"ButtonsGroupColumns": 6,
					"ButtonsGroupRows": 2,
					"BgColor": "#FFFFFF",
					"Buttons": [
						{
							"ButtonId": "1",
							"Columns": 6,
							"Rows": 1,
							"BgColor": "#5540C9",
							"ActionType": "reply",
							"ActionBody": json.dumps(
								{"cb_token": "CALLBACK_TnpnNQ==", "i": "help", "s": "user_answer", "P": "T",
								 "id": str(user_id)}),
							"Text": "<font color=\"#FFFFFF\">Відповісти</font>",
							"Silent": True
						}, {
							"ButtonId": "2",
							"Columns": 6,
							"Rows": 1,
							"BgColor": "#5540C9",
							"ActionType": "reply",
							"ActionBody": json.dumps(
								{"cb_token": "CALLBACK_TnpnNQ==", "i": "help", "s": "write_telephone2"}),
							"Text": "<font color=\"#FFFFFF\">Зателефонуйте мені</font>",
							"Silent": True
						}]}

			if data.storage["platform"] == "T":
				data.engine.Send_Message(data, text=answer, chat_id=local_a["chat_id"], keyboard=keyboard)
			elif data.storage["platform"] == "facebook":
				facebook_bot.Send_Callback_Keyboard(None, text=answer,
													keyboard=["Відповісти", "📞 Зателефонуйте мені"],
													chat_id=local_a["chat_id"],
													callback=[{"i": "help", "s": "user_answer"},
															  {"i": "help", "s": "write_telephone"}])

			else:

				viber_bot.Send_Message(None, text=answer, chat_id=local_a["chat_id"])
				viber_bot.Send_Callback_Keyboard(None, keyboard, chat_id=local_a["chat_id"], min_api_version=3)
				log.I(viber_bot.Get_Current_Keyboard(local_a["id"]))
				viber_bot.Send_Keyboard(None, keyboard=viber_bot.Get_Current_Keyboard(local_a["id"]),
										chat_id=local_a["chat_id"])
			data.engine.Send_Message(data, text="Повідомлення відправлено!", keyboard=data.Get_Keyboard("main"))
			data.engine.Set_Position_Passive(data, "main", "menu", MAIN_HANDLER)


		# ----------------------------------------------------------------------------------------------------------------

		# ----------------------------------------------------------------------------------------------------------------

	return bot
