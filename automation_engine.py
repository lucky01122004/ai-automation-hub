import json
import uuid
import os
from datetime import datetime
from typing import Dict, List, Any
import openai

class AutomationEngine:
    def __init__(self, storage_path='automations.json'):
        self.storage_path = storage_path
        self.automations = self._load_automations()
        # Set your OpenAI API key here or via environment variable
        openai.api_key = os.getenv('OPENAI_API_KEY', '')
    
    def _load_automations(self) -> Dict:
        """Load automations from storage"""
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_automations(self):
        """Save automations to storage"""
        with open(self.storage_path, 'w') as f:
            json.dump(self.automations, f, indent=2)
    
    def create_from_description(self, description: str) -> Dict:
        """Create an automation from natural language description using AI"""
        automation_id = str(uuid.uuid4())
        
        # Use AI to parse the description and create automation steps
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an automation assistant. Convert user descriptions into structured automation steps. Return JSON with: name, description, trigger, actions (array of steps), parameters."},
                    {"role": "user", "content": f"Create an automation from this description: {description}"}
                ]
            )
            
            automation_data = json.loads(response.choices[0].message.content)
        except Exception as e:
            # Fallback to simple parsing if AI fails
            automation_data = {
                "name": f"Automation-{automation_id[:8]}",
                "description": description,
                "trigger": "manual",
                "actions": [{"type": "log", "message": description}],
                "parameters": {}
            }
        
        automation = {
            "id": automation_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "active",
            **automation_data
        }
        
        self.automations[automation_id] = automation
        self._save_automations()
        
        return {"success": True, "automation": automation}
    
    def list_automations(self) -> List[Dict]:
        """List all automations"""
        return list(self.automations.values())
    
    def get_automation(self, automation_id: str) -> Dict:
        """Get a specific automation"""
        return self.automations.get(automation_id)
    
    def delete_automation(self, automation_id: str) -> bool:
        """Delete an automation"""
        if automation_id in self.automations:
            del self.automations[automation_id]
            self._save_automations()
            return True
        return False
    
    def execute(self, automation_id: str, parameters: Dict = None) -> Dict:
        """Execute an automation"""
        automation = self.automations.get(automation_id)
        
        if not automation:
            return {"success": False, "error": "Automation not found"}
        
        results = []
        params = parameters or {}
        
        try:
            for action in automation.get('actions', []):
                action_type = action.get('type')
                
                if action_type == 'log':
                    message = action.get('message', '')
                    results.append({"type": "log", "message": message})
                    print(f"LOG: {message}")
                
                elif action_type == 'http_request':
                    url = action.get('url')
                    method = action.get('method', 'GET')
                    results.append({"type": "http_request", "url": url, "method": method})
                
                elif action_type == 'email':
                    to = action.get('to')
                    subject = action.get('subject')
                    results.append({"type": "email", "to": to, "subject": subject})
                
                # Add more action types as needed
            
            return {
                "success": True,
                "automation_id": automation_id,
                "results": results,
                "executed_at": datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "automation_id": automation_id
            }
