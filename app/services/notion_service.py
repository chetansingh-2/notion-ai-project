from notion_client import Client
from ..config import NOTION_API_KEY, NOTION_DB_ID

class NotionService:
    def __init__(self):
        self.notion = Client(auth=NOTION_API_KEY)
        self.database_id=NOTION_DB_ID

    async def create_task(self, title: str, due_date: str = None, priority: str = "Medium"):
        try:
            properties = {
                "Task": {
                    "title": [{"text": {"content": title}}]
                },
                "Status": {
                    "status": {
                        "name": "Not started"  # Exactly as shown in your database
                    }
                },
                "Priority": {
                    "select": {
                        "name": priority
                    }
                }
            }

            if due_date:
                properties["Due Date"] = {"date": {"start": due_date}}

            new_page = self.notion.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            return new_page
        except Exception as e:
            print(f"Error happened while creating task: {e}")
            raise


    async def update_task(self, page_id:str, status:str):
        """ update task status"""
        try:
            return self.notion.pages.update(
                page_id=page_id,
                properties={
                    "Status": {
                        "status":{
                            "name":status
                        }
                    }

                }
            )

        except Exception as e:
            print(f"Error updating task : {e}")
            raise


    async def get_tasks(self):
        """Get all tasks"""
        try:
            response = self.notion.databases.query(
                database_id=self.database_id,
                filter={
                    "property": "Status",
                    "status": {
                        "does_not_equal": "Done"
                    }
                }
            )
            return response["results"]
        except Exception as e:
            print(f"Error fetching tasks: {e}")
            raise

    async def search_tasks(self, criteria):  # Remove async
        try:
            filter_conditions = []
            if criteria.get('search_criteria', {}).get('title_keywords'):
                filter_conditions.append({
                    "property": "Task",
                    "title": {
                        "contains": criteria['search_criteria']['title_keywords']
                    }
                })

            response = self.notion.databases.query(  # Remove await
                database_id=self.database_id,
                filter={
                    "and": filter_conditions
                }
            )
            return response["results"]
        except Exception as e:
            print(f"Error searching tasks: {e}")
            raise

    async def delete_task(self, task_id: str):  # Remove async
        try:
            return self.notion.pages.update(  # Remove await
                page_id=task_id,
                archived=True
            )
        except Exception as e:
            print(f"Error deleting task: {e}")
            raise

    async def update_task_time(self, task_id: str, new_date: str):
        try:
            return self.notion.pages.update(
                page_id=task_id,
                properties={
                    "Due Date": {"date": {"start": new_date}}
                }
            )
        except Exception as e:
            print(f"Error updating task time: {e}")
            raise



