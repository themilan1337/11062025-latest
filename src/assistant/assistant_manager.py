from typing import Dict, Any, List, Optional
from enum import Enum
import logging

from .openai_assistant import OpenAIAssistant
from .mistral_assistant import MistralAssistant

logger = logging.getLogger(__name__)

class AssistantType(Enum):
    OPENAI = "openai"
    MISTRAL = "mistral"

class AssistantManager:
    def __init__(self):
        self.assistants = {
            AssistantType.OPENAI: OpenAIAssistant(),
            AssistantType.MISTRAL: MistralAssistant()
        }
        self.active_assistants = {}
    
    async def initialize_assistants(self) -> Dict[str, str]:
        """
        Initialize both OpenAI and Mistral assistants
        """
        results = {}
        
        try:
            # Initialize OpenAI assistant
            openai_id = await self.assistants[AssistantType.OPENAI].create_assistant(
                name="OpenAI Task Assistant",
                instructions="""
                You are an advanced task management assistant powered by OpenAI. You excel at:
                1. Complex task analysis and breakdown
                2. Strategic planning and prioritization
                3. Detailed project management advice
                4. Code analysis and technical task assistance
                5. Research and information synthesis
                
                Provide thorough, well-structured responses with actionable insights.
                """
            )
            self.active_assistants[AssistantType.OPENAI] = openai_id
            results["openai"] = openai_id
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI assistant: {str(e)}")
            results["openai"] = f"Error: {str(e)}"
        
        try:
            # Initialize Mistral assistant
            mistral_id = await self.assistants[AssistantType.MISTRAL].create_assistant(
                name="Mistral Task Assistant",
                instructions="""
                You are a fast and efficient task management assistant powered by Mistral AI. You specialize in:
                1. Quick task organization and scheduling
                2. Concise productivity tips
                3. Rapid problem-solving approaches
                4. Efficient workflow optimization
                5. Clear, actionable advice
                
                Always provide direct, practical solutions with minimal overhead.
                """
            )
            self.active_assistants[AssistantType.MISTRAL] = mistral_id
            results["mistral"] = mistral_id
            
        except Exception as e:
            logger.error(f"Failed to initialize Mistral assistant: {str(e)}")
            results["mistral"] = f"Error: {str(e)}"
        
        return results
    
    async def send_message(
        self, 
        message: str, 
        assistant_type: AssistantType, 
        thread_id: str = None
    ) -> Dict[str, Any]:
        """
        Send a message to the specified assistant
        """
        try:
            if assistant_type not in self.assistants:
                return {
                    "response": "Invalid assistant type",
                    "status": "error"
                }
            
            assistant = self.assistants[assistant_type]
            response = await assistant.send_message(message, thread_id)
            
            # Add assistant type to response
            response["assistant_type"] = assistant_type.value
            
            return response
            
        except Exception as e:
            logger.error(f"Error sending message to {assistant_type.value} assistant: {str(e)}")
            return {
                "response": f"Error: {str(e)}",
                "status": "error",
                "assistant_type": assistant_type.value
            }
    
    async def create_thread(self, assistant_type: AssistantType) -> str:
        """
        Create a new conversation thread for the specified assistant
        """
        try:
            assistant = self.assistants[assistant_type]
            return await assistant.create_thread()
            
        except Exception as e:
            logger.error(f"Error creating thread for {assistant_type.value} assistant: {str(e)}")
            raise
    
    async def get_conversation_history(
        self, 
        thread_id: str, 
        assistant_type: AssistantType
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history for a specific thread and assistant
        """
        try:
            assistant = self.assistants[assistant_type]
            return await assistant.get_conversation_history(thread_id)
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {str(e)}")
            return []
    
    async def compare_responses(
        self, 
        message: str, 
        thread_ids: Dict[AssistantType, str] = None
    ) -> Dict[str, Any]:
        """
        Send the same message to both assistants and compare responses
        """
        results = {}
        
        for assistant_type in [AssistantType.OPENAI, AssistantType.MISTRAL]:
            try:
                thread_id = None
                if thread_ids and assistant_type in thread_ids:
                    thread_id = thread_ids[assistant_type]
                
                response = await self.send_message(message, assistant_type, thread_id)
                results[assistant_type.value] = response
                
            except Exception as e:
                logger.error(f"Error getting response from {assistant_type.value}: {str(e)}")
                results[assistant_type.value] = {
                    "response": f"Error: {str(e)}",
                    "status": "error",
                    "assistant_type": assistant_type.value
                }
        
        return results
    
    def get_assistant_status(self) -> Dict[str, Any]:
        """
        Get status of all assistants
        """
        return {
            "active_assistants": {
                assistant_type.value: assistant_id 
                for assistant_type, assistant_id in self.active_assistants.items()
            },
            "available_types": [assistant_type.value for assistant_type in AssistantType]
        }

# Global assistant manager instance
assistant_manager = AssistantManager()