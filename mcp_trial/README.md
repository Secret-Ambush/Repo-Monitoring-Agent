# MCP Repository Monitor Email Agent

This is the **MCP (Model Context Protocol)** version of the Repository Monitor Email Agent. It demonstrates how to build the same functionality using MCP instead of direct API calls.

## 🔄 **MCP vs Direct API Comparison**

### **Architecture Differences**

**Direct API Version (main folder):**
```
GitHub API ←→ PyGithub ←→ Our Code ←→ SMTP ←→ Email Server
```

**MCP Version (mcp_trial folder):**
```
GitHub API ←→ MCP GitHub Server ←→ MCP Client ←→ Our Code ←→ MCP Email Server ←→ Email Server
```

### **Key Differences**

| Aspect | Direct API | MCP |
|--------|------------|-----|
| **Interface** | API-specific libraries | Unified MCP interface |
| **Authentication** | Manual token handling | Handled by MCP servers |
| **Error Handling** | Custom implementation | Standardized MCP errors |
| **Setup Complexity** | Simple dependencies | Requires MCP servers |
| **AI Integration** | Manual integration | Designed for AI models |
| **Performance** | Direct, fast | Additional abstraction layer |

## 🚀 **Quick Start**

### **1. Install Dependencies**

```bash
cd mcp_trial
pip install -r requirements.txt
```

### **2. Set Up Environment**

```bash
# Create .env file
cp ../env.example .env

# Edit .env with your credentials
GITHUB_TOKEN=your_github_token
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

### **3. Install MCP Servers**

**Note:** MCP servers are still in development. For this demo, we're using mock implementations.

```bash
# Install MCP servers (when available)
pip install mcp-github mcp-email

# Or use mock servers for testing
```

### **4. Test the Setup**

```bash
# Run tests
python test_mcp.py

# Run the agent
python main.py --once
```

## 📁 **Project Structure**

```
mcp_trial/
├── src/
│   ├── __init__.py
│   ├── mcp_client.py      # MCP client wrapper
│   ├── state.py           # State management
│   └── workflow.py        # LangGraph workflow
├── main.py                # Application entry point
├── test_mcp.py           # Test suite
├── config.yaml           # MCP configuration
├── requirements.txt      # Dependencies
└── README.md            # This file
```

## 🔧 **Configuration**

The MCP version uses a different configuration structure:

```yaml
# MCP Configuration
mcp:
  servers:
    github:
      command: "mcp-github"
      args: ["--token", "${GITHUB_TOKEN}"]
    email:
      command: "mcp-email"
      args: ["--smtp-host", "${SMTP_HOST}", "--smtp-port", "${SMTP_PORT}", "--username", "${EMAIL_USERNAME}", "--password", "${EMAIL_PASSWORD}"]

# Repository Configuration
repository:
  owner: "Secret-Ambush"
  name: "testingIssues"

# Monitoring Configuration
monitoring:
  issue_threshold_days: 7
  check_interval_hours: 24
  pr_lookback_hours: 24

# Email Configuration
email:
  recipients:
    - "test@example.com"
```

## 🔄 **MCP Workflow**

The MCP workflow is similar to the direct API version but uses MCP calls:

```python
# MCP Version
async def _fetch_data_node(self, state):
    # Use MCP client instead of direct API
    issues = await self.mcp_client.get_open_issues(state.repo_owner, state.repo_name)
    prs = await self.mcp_client.get_recent_prs(state.repo_owner, state.repo_name)
    return state

# Direct API Version
def _fetch_data_node(self, state):
    # Use direct API calls
    issues = self.github_client.get_open_issues(state.repo_owner, state.repo_name)
    prs = self.github_client.get_recent_prs(state.repo_owner, state.repo_name)
    return state
```

## 🧪 **Testing**

### **Run Tests**

```bash
python test_mcp.py
```

### **Test Components**

1. **State Management**: Tests data models and state handling
2. **Workflow Logic**: Tests decision-making logic
3. **Configuration**: Tests config loading and validation
4. **MCP Client**: Tests MCP client functionality (mock)

## 📊 **Performance Comparison**

### **Direct API Advantages**
- ✅ **Faster**: No additional abstraction layer
- ✅ **More Control**: Direct access to all API features
- ✅ **Simpler Setup**: Fewer dependencies
- ✅ **Better Error Handling**: Custom error handling

### **MCP Advantages**
- ✅ **Unified Interface**: Same pattern for all services
- ✅ **AI-Optimized**: Designed for AI model interaction
- ✅ **Standardized**: Consistent across different tools
- ✅ **Extensible**: Easy to add new MCP servers

## 🔮 **Future Enhancements**

### **Potential MCP Improvements**
1. **Real MCP Servers**: Use actual MCP GitHub and email servers
2. **More Services**: Add MCP servers for Slack, Discord, etc.
3. **AI Integration**: Integrate with LLM models for intelligent analysis
4. **Dynamic Configuration**: Load MCP servers dynamically

### **Hybrid Approach**
Consider using a hybrid approach:
- **Direct APIs** for performance-critical operations
- **MCP** for AI model integration and extensibility

## 🚨 **Current Limitations**

1. **MCP Servers**: Real MCP servers are still in development
2. **Documentation**: MCP documentation is evolving
3. **Community**: Smaller community compared to direct APIs
4. **Maturity**: Less mature than direct API approaches

## 📚 **Learning Resources**

- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [MCP GitHub Repository](https://github.com/modelcontextprotocol)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

## 🤝 **Contributing**

This MCP version is experimental and designed for learning purposes. Contributions are welcome!

---

**This MCP version demonstrates the potential of using standardized protocols for AI agent development, even though the technology is still evolving.** 