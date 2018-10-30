I can show this and only this project because its development was stopped.

The test version of this bot is still working
you can check it on telegram(@CarAmericaBot)

-- bot.py
bot.py is the main file of project
It consists from decorated Database functions and decorated Step functions
The step function is close to view function in Django
it consists from executing of Step start (if data.type == Handle_Triger():)
and input calculating(exectes when person input some information)

Functions Go_To, Set_Position_Active and Set_Position_Passive
are created to change the step. 
Go_To, Set_Position_Active are executing the Steps start
while Set_Position_Passive is only changes the step


--Product_Sorting_module
This module is created to work with data which we are getting from
https://www.copart.com/ and https://www.iaai.com/
We are getting this data using parsers(There is no API) which
are located in CopartAPI and IaaIAPI modules


--  mannager_connection
This module appends some data into JSONs and Steps into engine
It can be connected to every project to perform connection with 
mannager via bot

-- telegram.json and viber.json
This files are static and they have some settings for project

-- telegram_answers.json and viber_answers.json
All text is in this files

-- Auto_Ria 
Created to search the cost of cars

-- site_support
Created to push cars into customer web-site

This bot crated using the old version of our framework
It WOULD NOT work on youre server without our database 
and BotEngine Rocket. 
I also can not give you the BotEngine Rocket documentation 


