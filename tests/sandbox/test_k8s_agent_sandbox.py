import unittest
from unittest.mock import MagicMock, patch

# You may need to adjust this import based on Aider's exact directory structure
from aider.coders.base_coder import Coder
from aider.io import InputOutput

class TestK8sSandbox(unittest.TestCase):
    def setUp(self):
        # Create a mock Coder instance with standard attributes
        self.coder = MagicMock(spec=Coder)
        self.coder.io = MagicMock(spec=InputOutput)
        self.coder.sandbox_type = "k8s-agent-sandbox"
        self.coder.k8s_sandbox_namespace = "default"
        self.coder.k8s_sandbox_warmpool = "default-pool"
        self.coder.partial_response_content = ""

        # Bind the methods under test to our mock coder instance
        # Assumes these methods were added directly to the Coder class
        self.coder.parse_sandbox_command = Coder.parse_sandbox_command.__get__(self.coder, Coder)
        self.coder.run_k8s_sandbox = Coder.run_k8s_sandbox.__get__(self.coder, Coder)

    def test_parse_sandbox_command_success(self):
        self.coder.partial_response_content = "Some text before\n```sandbox\necho 'hello world'\nls -la\n```\nSome text after."
        cmd = self.coder.parse_sandbox_command()
        self.assertEqual(cmd, "echo 'hello world'\nls -la")

    def test_parse_sandbox_command_no_type(self):
        self.coder.sandbox_type = None
        self.coder.partial_response_content = "```sandbox\necho 'hello'\n```"
        cmd = self.coder.parse_sandbox_command()
        self.assertIsNone(cmd)

    def test_parse_sandbox_command_no_match(self):
        self.coder.partial_response_content = "```bash\necho 'hello'\n```"
        cmd = self.coder.parse_sandbox_command()
        self.assertIsNone(cmd)

    @patch.dict('sys.modules', {'k8s_agent_sandbox': MagicMock(), 'k8s_agent_sandbox.models': MagicMock()})
    def test_run_k8s_sandbox_success(self):
        # Setup the mocked SDK
        import k8s_agent_sandbox
        mock_client_instance = MagicMock()
        mock_sandbox_instance = MagicMock()
        mock_result = MagicMock()

        mock_result.stdout = "hello world\n"
        mock_result.stderr = ""
        mock_sandbox_instance.commands.run.return_value = mock_result
        mock_client_instance.create_sandbox.return_value = mock_sandbox_instance
        k8s_agent_sandbox.SandboxClient.return_value = mock_client_instance

        # Execute
        feedback = self.coder.run_k8s_sandbox("echo 'hello world'")

        # Assertions
        self.assertIn("Executed `echo 'hello world'`", feedback)
        self.assertIn("STDOUT:\nhello world", feedback)
        mock_sandbox_instance.commands.run.assert_called_once_with("echo 'hello world'")
        mock_sandbox_instance.terminate.assert_called_once()
        self.coder.io.tool_output.assert_called()

    @patch.dict('sys.modules', {'k8s_agent_sandbox': MagicMock(), 'k8s_agent_sandbox.models': MagicMock()})
    def test_run_k8s_sandbox_creation_failure(self):
        # Setup the mocked SDK to throw an error on creation
        import k8s_agent_sandbox
        mock_client_instance = MagicMock()
        mock_client_instance.create_sandbox.side_effect = Exception("Cluster unavailable")
        k8s_agent_sandbox.SandboxClient.return_value = mock_client_instance

        # Execute
        feedback = self.coder.run_k8s_sandbox("echo 'test'")

        # Assertions
        self.assertIn("Sandbox execution failed: Cluster unavailable", feedback)
        self.coder.io.tool_error.assert_called_once()

    def test_run_k8s_sandbox_import_error(self):
        # Force an ImportError by mocking sys.modules with None for the target module
        with patch.dict('sys.modules', {'k8s_agent_sandbox': None}):
            feedback = self.coder.run_k8s_sandbox("echo 'test'")

            self.assertIn("k8s_agent_sandbox SDK is not installed", feedback)
            self.coder.io.tool_error.assert_called_once()

if __name__ == '__main__':
    unittest.main()
