from openai import OpenAI
from src.config import settings
from typing import List, Dict, Any, Optional
import logging
import json

logger = logging.getLogger(__name__)

class OpenAIAssistant:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.assistant_id = None
        self.thread_id = None
    
    async def create_assistant(self, name: str = "Task Management Assistant", instructions: str = None) -> str:
        """
        Create a new OpenAI assistant
        """
        try:
            if not instructions:
                instructions = """
                You are a helpful task management assistant. You can help users:
                1. Create and manage tasks
                2. Set reminders and deadlines
                3. Organize and prioritize work
                4. Provide productivity tips
                5. Answer questions about task management
                
                Always be helpful, concise, and professional in your responses.
                """
            
            assistant = self.client.beta.assistants.create(
                name=name,
                instructions=instructions,
                model="gpt-4-1106-preview",
                tools=[
                    {"type": "code_interpreter"},
                    {"type": "retrieval"}
                ]
            )
            
            self.assistant_id = assistant.id
            logger.info(f"Created OpenAI assistant with ID: {self.assistant_id}")
            return self.assistant_id
            
        except Exception as e:
            logger.error(f"Error creating OpenAI assistant: {str(e)}")
            raise
    
    async def create_thread(self) -> str:
        """
        Create a new conversation thread
        """
        try:
            thread = self.client.beta.threads.create()
            self.thread_id = thread.id
            logger.info(f"Created thread with ID: {self.thread_id}")
            return self.thread_id
            
        except Exception as e:
            logger.error(f"Error creating thread: {str(e)}")
            raise
    
    async def send_message(self, message: str, thread_id: str = None) -> Dict[str, Any]:
        """
        Send a message to the assistant and get response
        """
        try:
            if not thread_id:
                thread_id = self.thread_id
            
            if not thread_id:
                thread_id = await self.create_thread()
            
            # Add message to thread
            self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message
            )
            
            # Run the assistant
            run = self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.assistant_id
            )
            
            # Wait for completion
            while run.status in ['queued', 'in_progress', 'cancelling']:
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )
            
            if run.status == 'completed':
                # Get messages
                messages = self.client.beta.threads.messages.list(
                    thread_id=thread_id
                )
                
                # Get the latest assistant message
                for msg in messages.data:
                    if msg.role == "assistant":
                        response_content = msg.content[0].text.value
                        return {
                            "response": response_content,
                            "thread_id": thread_id,
                            "status": "success"
                        }
            
            return {
                "response": "Sorry, I couldn't process your request.",
                "thread_id": thread_id,
                "status": "error",
                "run_status": run.status
            }
            
        except Exception as e:
            logger.error(f"Error sending message to OpenAI assistant: {str(e)}")
            return {
                "response": f"Error: {str(e)}",
                "thread_id": thread_id,
                "status": "error"
            }
    
    async def get_conversation_history(self, thread_id: str) -> List[Dict[str, Any]]:
        """
        Get conversation history from a thread
        """
        try:
            messages = self.client.beta.threads.messages.list(thread_id=thread_id)
            
            conversation = []
            for msg in reversed(messages.data):
                conversation.append({
                    "role": msg.role,
                    "content": msg.content[0].text.value,
                    "timestamp": msg.created_at
                })
            
            return conversation
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {str(e)}")
            return []
    
    async def delete_assistant(self, assistant_id: str = None) -> bool:
        """
        Delete an assistant
        """
        try:
            if not assistant_id:
                assistant_id = self.assistant_id
            
            self.client.beta.assistants.delete(assistant_id)
            logger.info(f"Deleted assistant with ID: {assistant_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting assistant: {str(e)}")
            return False