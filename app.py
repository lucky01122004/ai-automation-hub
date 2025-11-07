from flask import Flask, render_template, request, jsonify
from automation_engine import AutomationEngine
import json
import os

app = Flask(__name__)
automation_engine = AutomationEngine()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/automations', methods=['GET'])
def get_automations():
    """Get all available automations"""
    automations = automation_engine.list_automations()
    return jsonify(automations)

@app.route('/api/automation/create', methods=['POST'])
def create_automation():
    """Create a new automation from natural language description"""
    data = request.json
    description = data.get('description')
    
    if not description:
        return jsonify({'error': 'Description is required'}), 400
    
    result = automation_engine.create_from_description(description)
    return jsonify(result)

@app.route('/api/automation/execute', methods=['POST'])
def execute_automation():
    """Execute an automation"""
    data = request.json
    automation_id = data.get('automation_id')
    parameters = data.get('parameters', {})
    
    if not automation_id:
        return jsonify({'error': 'Automation ID is required'}), 400
    
    result = automation_engine.execute(automation_id, parameters)
    return jsonify(result)

@app.route('/api/automation/<automation_id>', methods=['GET', 'DELETE'])
def manage_automation(automation_id):
    """Get or delete a specific automation"""
    if request.method == 'GET':
        automation = automation_engine.get_automation(automation_id)
        if automation:
            return jsonify(automation)
        return jsonify({'error': 'Automation not found'}), 404
    
    elif request.method == 'DELETE':
        success = automation_engine.delete_automation(automation_id)
        if success:
            return jsonify({'message': 'Automation deleted successfully'})
        return jsonify({'error': 'Automation not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
