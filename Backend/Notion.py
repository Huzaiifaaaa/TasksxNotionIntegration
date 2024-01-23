import requests
from datetime import datetime, timezone

#Reference: https://www.python-engineer.com/posts/notion-api-python/

#class for notion
class Notion:
    def __init__(self,backend):
        self.headers = {
            "Authorization": "Bearer " + backend.NOTION_API_KEY,
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }

    #add tasks to notion
    #tasks is a list of tasks
    #notion_database_id is the id of the notion database
    #auto is True if auto sync, False if manual sync
    #this will return True if success, False if error
    def add_tasks_to_notion(self, tasks, notion_database_id, auto):
        try: 
            create_url = "https://api.notion.com/v1/pages" #url to create a new page in notion
            data=self.transform_to_notion_format(tasks) #transform tasks to notion format

            for i in range(len(data)): #for each task
                payload = {"parent": {"database_id": notion_database_id}, "properties": data[i]} #payload to create a new page
                res = requests.post(create_url, headers=self.headers, json=payload) #make a post request to create a new page

            return True #return True if success
        except:
            return False #return False if error

    #transform tasks to notion format
    #tasks is a list of tasks
    #this will return a list of tasks in notion format
    def transform_to_notion_format(self,tasks):
        notion_tasks = []

        for task in tasks: #for each task
            title = task.get('title', '')
            notes = task.get('notes', '')
            due_date = task.get('due', '')
            due_date = datetime.now().astimezone(timezone.utc).isoformat()

            notion_task = {
                "Title": {"title": [{"text": {"content": title}}]},
                "Notes": {"rich_text": [{"text": {"content": notes}}]},
                "Due": {"date": {"start": due_date, "end": None}} if due_date else None
            }

            notion_tasks.append(notion_task) #append notion task to notion tasks list

        return notion_tasks #return notion tasks list

    