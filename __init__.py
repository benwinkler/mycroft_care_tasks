from adapt.intent import IntentBuilder
from mycroft import MycroftSkill, intent_handler
from mycroft.skills.context import adds_context, removes_context

class CareReminder(MycroftSkill):
    def __init__(self):
        super().__init__()
        self.learning = True
        #Load pending Tasks from backend
        self.user_id = "1"
        self.care_api_uri = 'https://care.mxfive.at/api/'


    @adds_context('ReminderContext')
    @intent_handler(IntentBuilder('DoYouHaveReminders')
                                                    .require('Hast')
                                                    .require('Erinnerungen'))
    def handle_do_you_have_reminders(self, message):
        import requests,json
        #Load User Data from Backend
        response_user = requests.get(f'{self.care_api_uri}care/user/{self.user_id}')
        if(response_user.status_code == 200):
            self.user = json.loads(response_user.text)       
        
        #Load User Tasks from Backend
        response_tasks = requests.get(f'{self.care_api_uri}care/user/{self.user_id}/tasks')
        if(response_tasks.status_code == 200):
            self.tasks = json.loads(response_tasks.text)
            self.task_count = len(self.tasks)
        else:
            self.speak('Ich habe leider gerade Probleme deine Erinnerungen zu laden, bitte versuche es später noch einmal!')
            return
        
        #Ask User if he wants to listen to the tasks now
        if self.task_count is 1:
            answ_wanna_hear = self.get_response(f'Hallo {self.user["name"]}, ich habe eine Erinnerung für dich, willst du diese jetzt hören?')          
        elif self.task_count > 1:
            answ_wanna_hear = self.get_response(f'Hallo {self.user["name"]}, ich habe {len(self.tasks)} Erinnerungen für dich, willst du diese jetzt hören?') 
        else:
            self.speak(f'Hallo {self.user["name"]}, ich habe heute keine neuen Erinnerungen für dich.')
            return 
            
        if 'ja' in answ_wanna_hear:
        
         # Tell every Task in dict
         for task in self.tasks:
            answ_task_done = self.get_response(task["description"] + ", hast du das bereits erledigt?")  
            if 'ja' in answ_task_done:
                self.speak('Gut, ich enterne diese Erinnerung von deiner Liste!')
                # Send Request to backend
                done_url = f'{self.care_api_uri}care/tasks/{task["id"]}/done'
                # Log Output
                self.log.info(done_url )
                # Save status to backend
                requests.patch(done_url )
                
            elif 'nein' in answ_task_done:
                answ_task_remember = self.get_response('Alles klar, soll ich dich später wieder daran erinnern?')
                 
                if 'ja' in answ_task_remember:
                    ext_time = "30"
                    self.speak(f'Alles klar {self.user["name"]}, ich werde dich in {ext_time} Minuten nochmals daran erinnern')
                    # Send time extend request to backend
                    extent_url = f'{self.care_api_uri}care/tasks/{task["id"]}/extendtime/{ext_time}'
                    requests.patch(extent_url)
                    self.log.info(extent_url)

                elif 'nein' in answ_task_remember:
                    self.speak('Okay, bis später!') 
         self.speak('Das war es auch schon, bis später!')    
         
        elif 'nein' in answ_wanna_hear:
            self.speak('Alles klar, bis später', expect_response=False)           
  
    
def create_skill():
    return CareReminder()
