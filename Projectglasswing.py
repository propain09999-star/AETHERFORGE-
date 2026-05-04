def __init__(self):
        # The 'Allowed List' of safe shell/JSON commands
        self.allowed_actions = ["scan_network", "tarpit_ip", "sign_log", "sync_o2o"]

    def validate_execution(self, json_command):
        command = json.loads(json_command)
        if command["action"] in self.allowed_actions:
            return self.execute(command)
        else:
            print("● [CRITICAL] Glasswing Gate Blocked Unauthorized Action!")
            return False

    def execute(self, command):
        print(f"● [GOVERNANCE] Executing Validated Action: {command['action']}")
        return True

# Test Gate
gate = GlasswingGate()
gate.validate_execution('{"action": "tarpit_ip", "target": "192.168.1.50"}')
