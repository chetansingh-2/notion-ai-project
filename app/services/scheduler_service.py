from .notion_service import NotionService
from .task_processor import TaskProcessor


#ye service scheduler(LLM) service and notion service ke liye bridge hogi
class SchedulerService:
    def __init__(self):
        self.notion = NotionService()
        self.processor = TaskProcessor()

    async def create_task_from_text(self, text:str):
        #1. process kro yha pr

        llm_result = await self.processor.process_input(text)
        if not llm_result:
            return {"error":"Failed to process text"}

        if llm_result.get('needs_clarification'):
            return {
                "needs_clarification": True,
                "question": llm_result['clarification_question']
            }

        try:
            notion_task = await self.notion.create_task(
                title=llm_result['title'],
                due_date=llm_result['due_date'],
                priority=llm_result['priority']
            )
            return {
                "success": True,
                "task": notion_task,
                "message": "Task created successfully"
            }
        except Exception as e:
            return {"error": f"Failed to create task in Notion: {str(e)}"}

    async def task_deletion(self, text: str):
        # First, process the deletion request
        search_criteria = await self.processor.process_deletion_request(text)

        if search_criteria.get('needs_clarification'):
            return {
                "needs_clarification": True,
                "question": search_criteria['clarification_question']
            }

        # Search for matching tasks
        matching_tasks = await self.notion.search_tasks(search_criteria)

        if not matching_tasks:
            return {"message": "No matching tasks found"}
        elif len(matching_tasks) > 1:
            return {
                "needs_clarification": True,
                "matching_tasks": matching_tasks,
                "question": "Multiple tasks found. Which one would you like to delete?"
            }

        # Delete the single matching task
        await self.notion.delete_task(matching_tasks[0]["id"])
        return {"message": "Task deleted successfully"}

    async def reschedule_task(self, text: str):
        # Process the rescheduling request
        reschedule_info = await self.processor.process_reschedule_request(text)

        if reschedule_info.get('needs_clarification'):
            return {
                "needs_clarification": True,
                "question": reschedule_info['clarification_question']
            }

        matching_tasks = await self.notion.search_tasks(reschedule_info)

        if not matching_tasks:
            return {"message": "No matching task found"}
        elif len(matching_tasks) > 1:
            return {
                "needs_clarification": True,
                "matching_tasks": matching_tasks,
                "question": "Multiple tasks found. Which one would you like to reschedule?"
            }

        await self.notion.update_task_time(
            matching_tasks[0]["id"],
            reschedule_info['new_date']
        )
        return {"message": "Task rescheduled successfully"}

