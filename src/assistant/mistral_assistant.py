from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from src.config import settings
from typing import List, Dict, Any, Optional
import logging
import json
import uuid

logger = logging.getLogger(__name__)

class MistralAssistant:
    def __init__(self):
        self.client = MistralClient(api_key=settings.mistral_api_key)
        self.model = "mistral-large-latest"
        self.conversations = {}  # Store conversations in memory (use Redis in production)
    
    async def create_assistant(self, name: str = "Mistral Task Assistant", instructions: str = None) -> str:
        """
        Create a new Mistral assistant (simulated)
        """
        try:
            if not instructions:
                instructions = """
                You are a helpful task management assistant powered by Mistral AI. You can help users:
                1. Create and manage tasks efficiently
                2. Set reminders and organize deadlines
                3. Provide productivity advice and tips
                4. Answer questions about project management
                5. Help with time management strategies
                
                Always provide clear, actionable advice and be concise in your responses.
                """
            
            assistant_id = f"mistral_assistant_{uuid.uuid4().hex[:8]}"
            
            # Store assistant configuration
            self.assistant_config = {
                "id": assistant_id,
                "name": name,
                "instructions": instructions,
                "model": self.model
            }
            
            logger.info(f"Created Mistral assistant with ID: {assistant_id}")
            return assistant_id
            
        except Exception as e:
            logger.error(f"Error creating Mistral assistant: {str(e)}")
            raise
    
    async def create_thread(self) -> str:
        """
        Create a new conversation thread
        """
        try:
            thread_id = f"thread_{uuid.uuid4().hex[:12]}"
            self.conversations[thread_id] = []
            logger.info(f"Created thread with ID: {thread_id}")
            return thread_id
            
        except Exception as e:
            logger.error(f"Error creating thread: {str(e)}")
            raise
    
    async def send_message(self, message: str, thread_id: str = None) -> Dict[str, Any]:
        """
        Send a message to the Mistral assistant and get response
        """
        try:
            if not thread_id:
                thread_id = await self.create_thread()
            
            if thread_id not in self.conversations:
                self.conversations[thread_id] = []
            
            # Add system message if this is the first message
            messages = []
            if not self.conversations[thread_id]:
                system_instructions = getattr(self, 'assistant_config', {}).get(
                    'instructions', 
                    "You are a helpful task management assistant."
                )
                messages.append(ChatMessage(role="system", content=system_instructions))
            
            # Add conversation history
            for msg in self.conversations[thread_id]:
                messages.append(ChatMessage(role=msg["role"], content=msg["content"]))
            
            # Add current user message
            messages.append(ChatMessage(role="user", content=message))
            
            # Get response from Mistral
            response = self.client.chat(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            assistant_response = response.choices[0].message.content
            
            # Store conversation
            self.conversations[thread_id].append({"role": "user", "content": message})
            self.conversations[thread_id].append({"role": "assistant", "content": assistant_response})
            
            return {
                "response": assistant_response,
                "thread_id": thread_id,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error sending message to Mistral assistant: {str(e)}")
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
            if thread_id not in self.conversations:
                return []
            
            conversation = []
            for msg in self.conversations[thread_id]:
                conversation.append({
                    "role": msg["role"],
                    "content": msg["content"],
                    "timestamp": None  # Mistral doesn't provide timestamps
                })
            
            return conversation
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {str(e)}")
            return []
    
    async def clear_conversation(self, thread_id: str) -> bool:
        """
        Clear conversation history for a thread
        """
        try:
            if thread_id in self.conversations:
                self.conversations[thread_id] = []
                logger.info(f"Cleared conversation for thread: {thread_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error clearing conversation: {str(e)}")
            return False
    
    async def get_available_models(self) -> List[str]:
        """
        Get list of available Mistral models
        """
        try:
            models = self.client.list_models()
            return [model.id for model in models.data]
            
        except Exception as e:
            logger.error(f"Error getting available models: {str(e)}")
            return [self.model]  # Return default model