import asyncio
import sys
import time
import re
import tempfile
import os

sys.path.append(".")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("dotenv not installed - skipping env load")

async def test_mcp_client():
    from src.utils.mcp_client import setup_mcp_client_and_tools, create_tool_param_model

    test_server_config = {
        "mcpServers": {
            "desktop-commander": {
                "command": "npx",
                "args": ["-y", "@wonderwhy-er/desktop-commander"]
            },
        }
    }

    mcp_tools, mcp_client = await setup_mcp_client_and_tools(test_server_config)
    # Test tool loading
    assert mcp_tools, "No MCP tools loaded"

async def test_controller_with_mcp():
    from src.controller.custom_controller import CustomController
    try:
        from browser_use.controller.registry.views import ActionModel
    except ImportError:
        print("browser_use module not found - skipping ActionModel import")
        return

    mcp_server_config = {
        "mcpServers": {
            "desktop-commander": {
                "command": "npx",
                "args": ["-y", "@wonderwhy-er/desktop-commander"]
            },
        }
    }

    controller = CustomController()
    await controller.setup_mcp_client(mcp_server_config)
    
    action_name = "mcp.desktop-commander.execute_command"
    action_info = controller.registry.registry.actions[action_name]
    param_model = action_info.param_model
    
    # Create temp test script
    test_script = tempfile.NamedTemporaryFile(suffix='.py', delete=False)
    test_script.write(b'print("Test output from temp script")\\nprint("PID logged for demo")\\n')
    test_script.close()
    
    params = {"command": f'python "{test_script.name}"'}
    validated_params = param_model(**params)
    ActionModel_ = controller.registry.create_action_model()
    action_model = ActionModel_(**{action_name: validated_params})
    
    result = await controller.act(action_model)
    result = result.extracted_content
    assert result, "No result from execute_command"
    
    # Improved PID extraction
    pid_match = re.search(r'PID[:\\s]*(\\d+)', result)
    if pid_match:
        pid = int(pid_match.group(1))
        print(f"Extracted PID: {pid}")
        
        # Read output with timeout
        action_name = "mcp.desktop-commander.read_output"
        action_info = controller.registry.registry.actions[action_name]
        param_model = action_info.param_model
        params = {"pid": pid}
        validated_params = param_model(**params)
        action_model = ActionModel_(**{action_name: validated_params})
        
        output_result = ""
        for iterations in range(5):
            await asyncio.sleep(1)
            result = await controller.act(action_model)
            result = result.extracted_content
            if result and "Test output" in result:
                output_result = result
                assert "Test output from temp script" in output_result
                print("Test passed: Output verified")
                break
        else:
            print("Timeout waiting for output")
    
    # Cleanup
    try:
        os.unlink(test_script.name)
    except:
        pass
    
    await controller.close_mcp_client()

if __name__ == '__main__':
    asyncio.run(test_controller_with_mcp())

