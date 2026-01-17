import os
import yaml
import copy
from robot.api import SuiteVisitor

class DataLoader(SuiteVisitor):
    def __init__(self, env_name="UAT"):
        self.env_name = env_name
        self.root_dir = os.getcwd()

    def start_suite(self, suite):
        # FIX: Handle PosixPath (Robot 7.0+) vs String
        source_path = str(suite.source) if suite.source else ""
        
        if not source_path.endswith('.robot'):
            return

        # 1. ROBUST PATH CALCULATION
        try:
            abs_source = os.path.normpath(source_path)
            testcases_dir = os.path.join(self.root_dir, 'testcases')
            rel_path = os.path.relpath(abs_source, testcases_dir)
            
            yaml_rel_path = os.path.splitext(rel_path)[0] + '.yaml'
            yaml_path = os.path.join(
                self.root_dir, 
                'resources', 'config', 'testdata', 
                self.env_name, 
                yaml_rel_path
            )
        except ValueError as e:
            print(f"⚠️ Path Error: {e}")
            return

        # 2. DEBUGGING
        if not os.path.exists(yaml_path):
            print(f"ℹ️ YAML Not Found: {yaml_path}")
            return

        print(f"✅ Loaded Data: {yaml_path}")
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f) or {}

        # 3. EXPAND TESTS
        for test in list(suite.tests):
            if test.name in data:
                self._expand_test_case(suite, test, data[test.name])

    def _expand_test_case(self, suite, template_test, test_config):
        suite.tests.remove(template_test)
        scenarios = test_config.get('TestScenarios', [])
        
        for index, scenario in enumerate(scenarios):
            vars = scenario.get('ScenarioVars', {})
            settings = scenario.get('RunSettings', {})
            
            new_test = copy.deepcopy(template_test)
            iter_name = settings.get('IterationName', f"iter_{index+1}")
            new_test.name = f"{template_test.name} - {iter_name}"
            
            for key, value in vars.items():
                if value is not None:
                    self._inject_variable(new_test, key, value)
            
            suite.tests.append(new_test)

    def _inject_variable(self, test, name, value):
        kw = test.body.create_keyword(name="BuiltIn.Set Test Variable")
        kw.args = (f"${{{name}}}", str(value))
        
        if len(test.body) > 0:
            last_item = test.body.pop() 
            test.body.insert(0, last_item)