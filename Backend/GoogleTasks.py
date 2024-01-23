import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


#class for google tasks
class GoogleTasks:
    def __init__(self, backend):
        self.scope= ['https://www.googleapis.com/auth/tasks.readonly']
        self.tasks_api_version = 'v1'
        self.tasks_api_service_name = 'tasks'
        self.token_path = backend.TOKEN_PATH
        self.credentials_path = backend.CREDENTIALS_PATH
        self.credentials = self.load_credentials()

    #load credentials from token.json
    def load_credentials(self):
        credentials = None
        if os.path.exists('token.json'):
            credentials = Credentials.from_authorized_user_file('token.json')
        return credentials

    #link google account
    #this will open a browser window to login to google account
    #and then save the token in json file
    #this token will be used to make api calls
    #this token will expire after some time
    #so we will need to refresh it
    def link_google_account(self):
        try:
            flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.scope)
            credentials = flow.run_local_server(port=0)
            path=os.path.join(self.token_path, 'token.json') #save token josn file
            with open(path, 'w') as token:
                token.write(credentials.to_json())

            self.credentials = credentials
            return True #return True if success
        except Exception as e: #return False if error
            return False 

    #revoke google account access
    #this will revoke the token by making a request to google and deleting the token.json file
    #so that the user will have to login again
    def revoke_google_access(self):
        try:
            if self.credentials and self.credentials.valid: #if credentials are valid
                self.credentials.revoke(Request()) #revoke the token
            
            path=os.path.join(self.token_path, 'token.json') #delete token.json file
            if os.path.exists(path): #if file exists
                os.remove(path) #delete it

            return True #return True if success
        except Exception as e: #return False if error
            return False

    #get google tasks
    #this will return the tasks list
    #if success then return (tasks, True)
    #if error then return ([], False)
    def get_google_tasks(self):
        try:
            if not self.credentials or not self.credentials.valid: #if credentials are not valid
                raise ValueError("Credentials not available or expired.") #raise error

            service = build(self.tasks_api_service_name, self.tasks_api_version, credentials=self.credentials) #build service
            tasks = service.tasks().list(tasklist='@default').execute() #get tasks

            tasks=self.parse_tasks(tasks) #parse tasks dict
            return (tasks, True) #return tasks and True
        except Exception as e:
            return ([], False) #return empty list and False


    #parse tasks dict
    #this will parse the tasks dict and return a list of tasks
    def parse_tasks(self,data):
        data=data['items'] #get items from dict

        tasks=[] #list of tasks
        for task_item in data: #for each task item
            task={
                "title": task_item.get("title", ""),
                "notes": task_item.get("notes", ""),
                "due": task_item.get("due", "")
            }
            tasks.append(task) #append task to tasks list

        return tasks #return tasks list
    
