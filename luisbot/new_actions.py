# -*- coding: utf-8 -*-
"""
Created on Sun Oct 11 12:48:57 2020

@author: T_jubin.ben
"""
from botbuilder.core import BotFrameworkAdapter,BotFrameworkAdapterSettings,TurnContext,ActivityHandler,RecognizerResult,MessageFactory,ConversationState,MemoryStorage
from botbuilder.ai.luis import LuisApplication,LuisPredictionOptions,LuisRecognizer
from botbuilder.dialogs import DialogSet,WaterfallDialog,WaterfallStepContext
from botbuilder.dialogs.prompts import TextPrompt,NumberPrompt,PromptOptions
import requests
import asyncio

class buhr(ActivityHandler):
    def __init__(self, conversation:ConversationState):
        self.con_statea = conversation
        self.state_prop = self.con_statea.create_property("dialog_set")
        self.dialog_set = DialogSet(self.state_prop)
        self.dialog_set.add(NumberPrompt("e_id"))
        self.dialog_set.add(WaterfallDialog("main_dialog",[self.GetUserNumber,self.get_buhr,self.Completed]))
        self.API_username = "A0000262@C0016585093P"
        self.API_password = "Nec@0987"
        self.base_url = "https://api10.successfactors.com/odata/v2/"
        self.api_type = "User"
        self.loop = asyncio.get_event_loop()
        self.botsettings = BotFrameworkAdapterSettings("","")
        self.botadapter = BotFrameworkAdapter(self.botsettings)
    

    async def GetUserNumber(self,waterfall_step:WaterfallStepContext):
        print('------- Get Employee ID')
        return await waterfall_step.prompt("e_id",PromptOptions(prompt=MessageFactory.text("Please enter the Emp ID")))

    async def get_buhr(self, waterfall_step:WaterfallStepContext):
        print('-------Get Buhr')
        employee_id = waterfall_step.turn_context.activity.text
        waterfall_step.values["employee_id"] = employee_id
        api_filter = "({empId})/hr?$format=json".format(empId = employee_id)
        api_response = requests.get(self.base_url + self.api_type + api_filter,
                                auth=(self.API_username, self.API_password))
        if api_response.status_code == 200 and len(api_response.json()["d"]) != 0:
            buhr_name = api_response.json()["d"]["defaultFullName"]
            buhr_email = api_response.json()["d"]["email"]
            print(buhr_name)
            self.bot_reply = f"Your BUHR is {buhr_name} and contact info is {buhr_email}."
            await waterfall_step.turn_context.send_activity(self.bot_reply)
        else:
            self.bot_reply = "Unable to find your BUHR."
            await waterfall_step.turn_context.send_activity(self.bot_reply)

    async def Completed(self,waterfall_step:WaterfallStepContext):
        return await waterfall_step.end_dialog()

    async def on_turn(self,turn_context:TurnContext):
        self.dialog_context = await self.dialog_set.create_context(turn_context)
        await self.dialog_context.begin_dialog("main_dialog")
        await self.con_statea.save_changes(turn_context)
        task = self.loop.create_task(
                self.botadapter.process_activity(self.get_buhr)
                )
        self.loop.run_until_complete(task)
        