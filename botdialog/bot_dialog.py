from botbuilder.core import TurnContext,ActivityHandler,ConversationState,MessageFactory
from botbuilder.ai.luis import LuisApplication,LuisPredictionOptions,LuisRecognizer
from botbuilder.dialogs import DialogSet,WaterfallDialog,WaterfallStepContext
from botbuilder.dialogs.prompts import TextPrompt,NumberPrompt,PromptOptions
import requests
class BotDialog(ActivityHandler):
    def __init__(self,conversation:ConversationState):
        self.con_statea = conversation
        self.state_prop = self.con_statea.create_property("dialog_set")
        self.dialog_set = DialogSet(self.state_prop)
        self.dialog_set.add(NumberPrompt("Employee_id"))
        self.dialog_set.add(WaterfallDialog("main_dialog",[self.GetUserID,self.GetBuhr,self.Completed]))
        self.dialog_set.add(WaterfallDialog("asset_dialog",[self.GetUserID,self.GetAsset,self.Completed]))
        self.API_username = "A0000262@C0016585093P"
        self.API_password = "Nec@0987"
        self.base_url = "https://api10.successfactors.com/odata/v2/"
        self.api_type = "User"
        luis_app = LuisApplication("8e82ab3b-1f2d-4a4e-923d-51c4d25d3e8f","4ff0baa675e041bcb234713b5a7e127b","https://luminous-chat-bot-authoring.cognitiveservices.azure.com/")
        luis_option = LuisPredictionOptions(include_all_intents=True,include_instance_data=True)
        self.LuisReg = LuisRecognizer(luis_app,luis_option,True)

    async def GetUserID(self,waterfall_step:WaterfallStepContext):
        return await waterfall_step.prompt("Employee_id",PromptOptions(prompt=MessageFactory.text("Please enter the Employee ID")))
    
    async def GetAsset(self,waterfall_step:WaterfallStepContext):
        """Code Here"""
        await waterfall_step._turn_context.send_activity("Hello World.")
        
    async def GetBuhr(self,waterfall_step:WaterfallStepContext):
        employee_id = waterfall_step._turn_context.activity.text
        #waterfall_step.values["employee_id"] = employee_id
        api_filter = "({empId})/hr?$format=json".format(empId = employee_id)
        api_response = requests.get(self.base_url + self.api_type + api_filter,
                                auth=(self.API_username, self.API_password))
        if api_response.status_code == 200 and len(api_response.json()["d"]) != 0:
            buhr_name = api_response.json()["d"]["defaultFullName"]
            buhr_email = api_response.json()["d"]["email"]
            print(buhr_name)
            self.bot_reply = f"Your BUHR is {buhr_name} and contact info is {buhr_email}."
            await waterfall_step._turn_context.send_activity(self.bot_reply)
        else:
            self.bot_reply = "Unable to find your BUHR."
            await waterfall_step._turn_context.send_activity(self.bot_reply)

        
    async def Completed(self,waterfall_step:WaterfallStepContext):
        await waterfall_step._turn_context.send_activity("Have a Nice Day.")
        return await waterfall_step.end_dialog()
        
    async def on_turn(self,turn_context:TurnContext):
        response = {"utter_greet": "Hey! How are you?",
                     "utter_cheer_up": "Here is something to cheer you up: :-)",
                     "utter_did_that_help": "Did that help you?",
                     "utter_happy": "Great, carry on!",
                     "utter_goodbye": "Bye",
                     "utter_iamabot": "I am a bot, powered by Luis.",
                     "test_demo": "" }
        luis_result = await self.LuisReg.recognize(turn_context)
        intent = LuisRecognizer.top_intent(luis_result)
        result = luis_result.properties["luisResult"]
        print(result)
        dialog_context = await self.dialog_set.create_context(turn_context)
        entity = ""
        if result.entities:
            entity = result.entities[0]
            entity = entity.type
        else:
            await dialog_context.continue_dialog()
        
        if entity == "get_bu_hr":
            await dialog_context.begin_dialog("main_dialog")
            await self.con_statea.save_changes(turn_context)
        elif entity == "test_demo":
            await dialog_context.begin_dialog("asset_dialog")
            await self.con_statea.save_changes(turn_context)
        else:
            await turn_context.send_activity(f"{response[str(entity)]}")
