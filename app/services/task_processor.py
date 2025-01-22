from groq import Groq
from datetime import datetime, timedelta
import pytz
import json
from dotenv import load_dotenv
import os


class TaskProcessor:
    def __init__(self):
        load_dotenv()
        self.client = Groq()
        self.ist = pytz.timezone('Asia/Kolkata')

    async def process_input(self, user_input: str):
        current_time = datetime.now(self.ist)

        # Calculate dates for all weekdays
        weekdays = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2,
            'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
        }

        # Calculate this week's dates for all days
        this_week_dates = {}
        for day_name, day_number in weekdays.items():
            days_until = (day_number - current_time.weekday()) % 7
            this_date = current_time + timedelta(days=days_until)
            this_week_dates[day_name] = this_date.strftime('%B %d')

        prompt = f"""You are a task management assistant that operates in Indian Standard Time (IST).
        Current time: {current_time.strftime("%Y-%m-%d %H:%M:%S IST")}

        UNDERSTAND THESE PATTERNS:
        1. Specific Dates:
           - When user says "this [weekday]" or "coming [weekday]", use the very next occurrence
           - If today is {current_time.strftime('%A')}, then:
             * This Monday is {this_week_dates['monday']}
             * This Tuesday is {this_week_dates['tuesday']}
             * This Wednesday is {this_week_dates['wednesday']}
             * This Thursday is {this_week_dates['thursday']}
             * This Friday is {this_week_dates['friday']}
             * This Saturday is {this_week_dates['saturday']}
             * This Sunday is {this_week_dates['sunday']}
           - "next [weekday]" means the weekday after the coming one
           - Always calculate dates based on current date {current_time.strftime('%Y-%m-%d')}

        2. Time Rules:
           - Keep times exactly as specified (like 13:00)
           - If no time specified, ask for clarification
           - Use 24-hour format for clarity

        3. Current Calendar Context:
        - Today is {current_time.strftime('%A, %B %d, %Y')}

        Return a valid JSON with:
        - title (string): task description including meeting purpose
        - due_date (string): YYYY-MM-DD HH:MM format or null
        - priority (string): "High", "Medium", or "Low"
        - needs_clarification (boolean): true if time needs to be clarified
        - clarification_question (string): ask about specific time if needed
        - participants (array): list of people mentioned in the task"""

        try:
            completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_input}
                ],
                model="mixtral-8x7b-32768",
                response_format={"type": "json_object"}
            )

            return json.loads(completion.choices[0].message.content)
        except Exception as e:
            print(f"Error processing input: {e}")
            return {
                "title": "",
                "due_date": None,
                "priority": "Medium",
                "needs_clarification": True,
                "clarification_question": "Could you please provide more details about the task?",
                "participants": []
            }

    async def process_deletion_request(self, user_input: str):
        current_time = datetime.now(self.ist)

        prompt = f"""You are a task management assistant. Current time: {current_time.strftime("%Y-%m-%d %H:%M:%S IST")}
        Extract information about which task to delete.

        Given the user's request, identify:
        1. Any specific task or meeting titles
        2. Any dates mentioned
        3. Any person names mentioned

        Return ONLY a valid JSON with this EXACT structure:
        {{
            "search_criteria": {{
                "title_keywords": "string with words to match in title",
                "date": "YYYY-MM-DD format if date mentioned, else null",
                "participants": ["array of names mentioned"]
            }},
            "needs_clarification": false,
            "clarification_question": null
        }}

        If the request is unclear, set needs_clarification to true and provide appropriate question."""

        try:
            completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_input}
                ],
                model="mixtral-8x7b-32768",
                response_format={"type": "json_object"}
            )

            return json.loads(completion.choices[0].message.content)
        except Exception as e:
            print(f"Error processing deletion request: {e}")
            return {
                "search_criteria": {
                    "title_keywords": "",
                    "date": None,
                    "participants": []
                },
                "needs_clarification": True,
                "clarification_question": "Could you provide more details about which task to delete?"
            }

    async def process_reschedule_request(self, user_input: str):
        current_time = datetime.now(self.ist)

        prompt = f"""You are a task management assistant that operates in Indian Standard Time (IST).
        Current time in IST: {current_time.strftime("%Y-%m-%d %H:%M:%S IST")}

        CRITICAL TIME HANDLING:
        - When user says "1pm", use exactly "13:00" (DO NOT ADD +5:30)
        - Keep times EXACTLY as specified by user
        - Convert 12-hour format to 24-hour format directly:
            * 1pm → 13:00
            * 2pm → 14:00
            * 9am → 09:00

        Example Conversions:
        - "tomorrow at 1pm" → "YYYY-MM-DD 13:00"
        - "next Monday 2pm" → "YYYY-MM-DD 14:00"
        - "Friday 9am" → "YYYY-MM-DD 09:00"

        Return this EXACT JSON structure:
        {{
            "search_criteria": {{
                "title_keywords": "string",
                "participants": ["names"]
            }},
            "new_date": "YYYY-MM-DD HH:MM",
            "needs_clarification": false,
            "clarification_question": null
        }}

        DO NOT adjust times by adding hours. Use the exact time mentioned by user."""

        try:
            completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_input}
                ],
                model="mixtral-8x7b-32768",
                response_format={"type": "json_object"}
            )

            response = json.loads(completion.choices[0].message.content)

            # If we have a new_date, convert it to UTC for Notion
            if response.get('new_date'):
                ist_time = datetime.strptime(response['new_date'], "%Y-%m-%d %H:%M")
                ist = pytz.timezone('Asia/Kolkata')
                ist_time = ist.localize(ist_time)
                utc_time = ist_time.astimezone(pytz.UTC)
                response['new_date'] = utc_time.strftime("%Y-%m-%d %H:%M")

            return response

        except Exception as e:
            print(f"Error processing reschedule request: {e}")
            return {
                "search_criteria": {
                    "title_keywords": "",
                    "participants": []
                },
                "new_date": None,
                "needs_clarification": True,
                "clarification_question": "Could you provide more details about the task and new time?"
            }# async def main():
#     processor = TaskProcessor()
#
#     while True:
#         print("\n=== Task Management System ===")
#         print("1. Create task")
#         print("2. Delete task")
#         print("3. Reschedule task")
#         print("4. Quit")
#
#         action = input("\nChoose an action (1-4): ")
#
#         if action == "4":
#             print("Goodbye!")
#             break
#
#         if action == "1":
#             user_input = input("Enter your task: ")
#             result = await processor.process_input(user_input)
#         elif action == "2":
#             user_input = input("Which task would you like to delete?: ")
#             result = await processor.process_deletion_request(user_input)
#         elif action == "3":
#             user_input = input("Enter reschedule details: ")
#             result = await processor.process_reschedule_request(user_input)
#         else:
#             print("Invalid action")
#             continue
#
#         if result:
#             print("\nProcessed Request:")
#             print(json.dumps(result, indent=2))
#
#
