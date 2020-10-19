from botbuilder.core import UserState,TurnContext,ActivityHandler,RecognizerResult,MessageFactory,ConversationState,MemoryStorage,CardFactory
from botbuilder.ai.luis import LuisApplication,LuisPredictionOptions,LuisRecognizer
from luisbot.new_actions import buhr
from botbuilder.schema import ChannelAccount, CardAction, ActionTypes, SuggestedActions, ActivityTypes, Activity, Attachment
import os
import json

card = "luisbot\\testcard.json"
class LuisBot(ActivityHandler):
    def __init__(self, conversation:ConversationState):
        luis_app = LuisApplication("8e82ab3b-1f2d-4a4e-923d-51c4d25d3e8f","4ff0baa675e041bcb234713b5a7e127b","https://luminous-chat-bot-authoring.cognitiveservices.azure.com/")
        luis_option = LuisPredictionOptions(include_all_intents=True,include_instance_data=True)
        self.LuisReg = LuisRecognizer(luis_app,luis_option,True)

    async def on_message_activity(self,turn_context:TurnContext):
        response = {"utter_greet": "Hey! How are you?",
                     "utter_cheer_up": "Here is something to cheer you up: :-)",
                     "utter_did_that_help": "Did that help you?",
                     "utter_happy": "Great, carry on!",
                     "utter_goodbye": "Bye",
                     "utter_iamabot": "I am a bot, powered by Luis.",
                     "test_demo": "" }
        # turn_context contains the information needed to execute the incomming activity.
        luis_result = await self.LuisReg.recognize(turn_context)
        intent = LuisRecognizer.top_intent(luis_result)
        print('--- Top Intent: ',intent)
        #await turn_context.send_activity(f"Top Intent : {intent}")
        result = luis_result.properties["luisResult"]
        print('--- Result:', result)
        print('---T_context',turn_context.activity)
        if result.entities:
            entity = result.entities[0]
            entity = entity.type
        else:
            entity = None
        print(str(entity))
        
        text = turn_context.activity.text.lower()
        response_text = self._process_input(text)
        
        if response_text:
            await turn_context.send_activity(MessageFactory.text(response_text))
            
        elif entity == "test_demo":
            message = Activity(
            text="Here is an Adaptive Card:",
            type=ActivityTypes.message,
            attachments=[self._create_adaptive_card_attachment()],
            )
            await turn_context.send_activity(message)
            
        else:
            if entity is not None:
                if 'get_bu_hr' in entity:
                    CONMEMORY = ConversationState(MemoryStorage())
                    buhr_obj = buhr(CONMEMORY)
                    await buhr_obj.on_turn(turn_context)
                elif 'get_product_solution' in entity:
                    return await self._send_suggested_actions(turn_context)
                else:
                    print('--- Response: ',response[str(entity)])
                    await turn_context.send_activity(f"{response[str(entity)]}")
            else:
                await turn_context.send_activity("I can't answer that.")
    
    def _create_adaptive_card_attachment(self) -> Attachment:
        """
        Load a random adaptive card attachment from file.
        :return:
        """
        card_path = os.path.join(os.getcwd(), card)
        with open(card_path, "rb") as in_file:
            card_data = json.load(in_file)
        return CardFactory.adaptive_card(card_data)     
    
    def _process_input(self, text: str):        
        if text == "know more":
            return "Solution2: [1] Please check device provisioning status on web portal [2] verify is any primary user already associated with that device. [3] While adding device or product(inverter serial number) should be unique across all the products."
    
    async def _send_suggested_actions(self, turn_context: TurnContext):
        """
        Creates and sends an activity with suggested actions to the user. When the user
        clicks one of the buttons the text value from the "CardAction" will be displayed
        in the channel just as if the user entered the text. There are multiple
        "ActionTypes" that may be used for different situations.
        """

        reply = MessageFactory.text("Please make sure app is of latest version. Please check the internet connection and try to logout and login again. Otherwise escalate to development team.")

        reply.suggested_actions = SuggestedActions(
            actions=[
                CardAction(
                    title="Know More",
                    type=ActionTypes.im_back,
                    value="Know More")
            ]
        )

        return await turn_context.send_activity(reply)