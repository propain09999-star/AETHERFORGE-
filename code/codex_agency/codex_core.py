# Codex Core

## Overview
This module serves as the core of the Codex Agency, providing comprehensive support for multi-threaded project management, Git worktree integration, configurability for diff tools, terminal interaction, and automation features inspired by OpenAI's Codex app.

## Features
- **Multi-threaded Project Management**: Framework to manage multiple threads for project operations, improving efficiency and responsiveness.
- **Git Worktree Support**: Allows management and interaction with Git worktrees, enabling developers to work on multiple branches simultaneously without the need for multiple clones.
- **Diff Tools Integration**: Customizable support for various diff tools to facilitate code comparison and version tracking.
- **Terminal Integration**: Seamless integration with terminal commands for executing tasks directly from the command line.
- **Automations**: Automation scripts and functionalities to streamline repetitive tasks, modelled from the automation capabilities of OpenAI Codex.

## Getting Started
### Installation
```bash
pip install codex-agency
```

### Usage
```python
from codex_agency import CodexCore

# Initialize the core module
codex = CodexCore()

# Example of using the multi-threaded project manager
codex.start_project('Project A')
```

## Multi-threaded Project Management
The module utilizes Python's `threading` library to allow for concurrent execution of project tasks.

```python
import threading

class ProjectManager:
    def __init__(self):
        self.threads = []

    def run_task(self, task):
        # Implementation for task execution
        pass

    def start_project(self, project_name):
        # Example task
        thread = threading.Thread(target=self.run_task, args=(project_name,))
        thread.start()
        self.threads.append(thread)
```

## Git Worktree Support
To leverage Git worktree functionality, use the following command structure:
```bash
git worktree add <path> <branch>
```

## Diff Tools Configuration
Set your preferred diff tool in the configuration settings:
```python
codex.set_diff_tool('meld')  # or 'vimdiff', 'kdiff3'
```

## Terminal Integration
You can run shell commands directly:
```python
import os

os.system('ls -l')  # Example command
```

## Automation Example
Here’s how to set up a simple automation:
```python
codex.automate('git pull', 'Update the local repository')
```

## Conclusion
This module is designed to streamline development workflows and integrate various tools and automations inspired by state-of-the-art design principles, enhancing productivity in coding projects.