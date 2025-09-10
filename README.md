# Agentic Apps - ADK Agent Playground

This repository serves as a playground for testing and experimenting with Google's Agent Development Kit (ADK) capabilities. It contains various AI agents designed to demonstrate different use cases and functionalities.

## Repository Structure

```
agentic-apps/
├── designer_agent/           # Interior design and Airbnb optimization agent
│   ├── __init__.py          # Package initialization
│   ├── agent.py             # Main agent implementation
│   ├── prompt.txt           # Sample prompts and use cases
│   └── requirements.txt     # Python dependencies
└── README.md                # This file
```

## Available Agents

### Designer Agent (`designer_agent/`)

**Purpose**: Interior design and Airbnb property optimization specialist

**Capabilities**:

- Creates comprehensive Airbnb design proposals
- Generates step-by-step renovation plans
- Provides room-by-room design recommendations
- Suggests color palettes and furniture selections
- Creates professional PDF reports with custom formatting

**Key Features**:

- Uses Google's Gemini 2.5 Flash Lite model
- Integrates with Google Cloud AI Platform
- Generates PDF documents with custom styling and borders
- Provides actionable design recommendations based on property specifications

**Dependencies**:

- `google-adk` - Google Agent Development Kit
- `google-cloud-aiplatform` - Google Cloud AI services
- `reportlab` - PDF generation
- `pdfplumber` - PDF processing
- `google-cloud-storage` - Cloud storage integration

**Usage Example**:
The agent can analyze property details (size, budget, location, target guests) and generate comprehensive design proposals including:

- High-level action plans
- Design concepts and mood boards
- Paint and color recommendations
- Room-specific furniture and decor suggestions
- Essential amenities checklists

## Getting Started

1. Install dependencies for each agent:

   ```bash
   cd designer_agent/
   pip install -r requirements.txt
   ```

2. Set up environment variables:

   - `GOOGLE_API_KEY`: Your Google API key
   - `GOOGLE_GENAI_USE_VERTEXAI`: Vertex AI configuration

3. Run the agent:
   ```python
   from designer_agent import agent
   # Use the agent as needed
   ```

## Contributing

This playground is designed for experimentation and learning. Feel free to:

- Add new agents with different capabilities
- Enhance existing agents with new features
- Share interesting use cases and examples
- Contribute improvements and optimizations

## License

This project is for educational and experimental purposes. Please ensure compliance with Google's ADK terms of service when using the provided agents.
