# 🤖 AI Automation Hub

AI-powered automation platform with endless possibilities - Create, manage, and deploy custom automations using natural language and AI agents.

## ✨ Features

- **Natural Language Automation Creation**: Describe what you want to automate in plain English
- **AI-Powered**: Leverages OpenAI's GPT models to understand and create automations
- **Web Interface**: Beautiful, intuitive UI for managing all your automations
- **REST API**: Full-featured API for programmatic access
- **Extensible**: Easy to add new automation types and actions
- **Persistent Storage**: Automations saved to JSON for easy portability

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key (optional, for AI features)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/lucky01122004/ai-automation-hub.git
cd ai-automation-hub
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (optional):
```bash
export OPENAI_API_KEY='your-api-key-here'
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to:
```
http://localhost:5000
```

## 📖 Usage

### Creating an Automation

1. Open the web interface
2. Enter a natural language description of what you want to automate:
   - "Send me an email every morning at 8am with weather forecast"
   - "Monitor website X and alert me when price drops below $50"
   - "Backup my database every night at midnight"
3. Click "Create Automation"
4. The AI will parse your request and create the automation

### Executing Automations

- Click the "Execute" button on any automation card
- Use the API endpoint: `POST /api/automation/execute`

### API Endpoints

#### Get All Automations
```bash
GET /api/automations
```

#### Create Automation
```bash
POST /api/automation/create
Content-Type: application/json

{
  "description": "Your automation description here"
}
```

#### Execute Automation
```bash
POST /api/automation/execute
Content-Type: application/json

{
  "automation_id": "automation-id-here",
  "parameters": {}
}
```

#### Delete Automation
```bash
DELETE /api/automation/<automation_id>
```

## 🏗️ Architecture

```
ai-automation-hub/
├── app.py                    # Flask application & API routes
├── automation_engine.py      # Core automation logic & AI integration
├── requirements.txt          # Python dependencies
├── templates/
│   └── index.html           # Web interface
└── automations.json         # Persistent storage (auto-created)
```

## 🎯 Automation Types

The platform supports various automation types:

- **Logging**: Simple log messages
- **HTTP Requests**: Make API calls to external services
- **Email**: Send emails (requires configuration)
- **Scheduled Tasks**: Time-based triggers
- **Custom Actions**: Easily extensible

## 🔧 Configuration

### OpenAI Integration

Set your OpenAI API key as an environment variable:
```bash
export OPENAI_API_KEY='sk-your-key-here'
```

Without an API key, the system will use fallback parsing.

### Storage

Automations are stored in `automations.json` by default. You can change this in `automation_engine.py`:

```python
automation_engine = AutomationEngine(storage_path='custom_path.json')
```

## 🌟 Example Use Cases

1. **Website Monitoring**: Track product prices, availability, or content changes
2. **Social Media Automation**: Schedule posts, monitor mentions
3. **Data Pipeline**: Automate ETL processes
4. **Notifications**: Set up custom alert systems
5. **Backup Tasks**: Automated backup routines
6. **Report Generation**: Scheduled report creation and distribution

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with Flask
- Powered by OpenAI GPT models
- Inspired by the possibilities of AI-driven automation

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

---

**Note**: This is a demonstration project. For production use, implement proper security measures, error handling, and authentication.
