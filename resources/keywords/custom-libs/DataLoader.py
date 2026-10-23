"""
DataLoader.py
Pre-run modifier (SuiteVisitor) and Config Library for Robot Framework 7.x.
Enforces the LEGO architecture: separates test logic (.robot), test data (.yaml),
shared entity registries (users.yaml), and environment configurations.

Features:
- Loads .env secrets automatically at initialization.
- Dynamically clones test cases for each scenario defined in YAML.
- Injects environment configuration (BaseURL, Browser, Headless, Timeout).
- Supports explicit entity lookup keywords: `Get User Config` and `Get Config Entity`.
- Encapsulates sensitive variables in robot.api.types.Secret without fallback leakage.
"""

import os
import re
import copy
import yaml
from pathlib import Path
from dotenv import load_dotenv

from robot.api import SuiteVisitor
from robot.api.types import Secret
from robot.api.deco import keyword, library
from robot.libraries.BuiltIn import BuiltIn

# Load secrets from .env file in project root
load_dotenv()

ENV_VAR_PATTERN = re.compile(r"%\{([A-Za-z0-9_]+)(?:=([^}]*))?\}")

def resolve_env_vars(value):
    """Resolves %{VAR} or %{VAR=default} patterns from os.environ."""
    if isinstance(value, str):
        def _repl(match):
            var_name = match.group(1)
            default_val = match.group(2) if match.group(2) is not None else ""
            return os.environ.get(var_name, default_val)
        return ENV_VAR_PATTERN.sub(_repl, value)
    elif isinstance(value, dict):
        return {k: resolve_env_vars(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [resolve_env_vars(item) for item in value]
    return value


@library(scope='GLOBAL')
class DataLoader(SuiteVisitor):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    # Class-level store for scenario contexts
    _scenario_store = {}

    def __init__(self, env_config="default.yaml"):
        self.root_dir = Path.cwd()
        self.env_arg = env_config
        self.env_path = self._resolve_env_path(env_config)
        self.env_name = self.env_path.parent.name if self.env_path.name in ('env.yaml', 'config.yaml') else self.env_path.stem
        
        # Load global .env, then environment-specific .env (e.g., .env.default, .env.staging) if present
        load_dotenv(self.root_dir / '.env')
        env_specific_dot = self.root_dir / f".env.{self.env_name}"
        if env_specific_dot.exists():
            load_dotenv(env_specific_dot, override=True)

        self.env_config = self._load_env_config()

    def _resolve_env_path(self, env_arg: str) -> Path:
        """Resolves environment config file path from folder, filename, or alias."""
        clean_name = Path(env_arg).stem
        candidates = [
            self.root_dir / 'resources' / 'config' / 'environments' / clean_name / 'env.yaml',
            self.root_dir / 'resources' / 'config' / 'environments' / clean_name / 'config.yaml',
            self.root_dir / 'resources' / 'config' / 'environments' / f"{clean_name}.yaml",
            self.root_dir / env_arg,
            self.root_dir / 'resources' / 'config' / 'environments' / 'default' / 'env.yaml',
            self.root_dir / 'resources' / 'config' / 'environments' / 'default.yaml',
        ]
        for c in candidates:
            if c.is_file():
                return c.resolve()
        return (self.root_dir / 'resources' / 'config' / 'environments' / 'default' / 'env.yaml').resolve()

    def _load_env_config(self) -> dict:
        """Loads environment configuration (BaseURL, Browser, Timeout, etc.)."""
        if self.env_path.exists():
            print(f"[OK] DataLoader environment loaded: {self.env_name} ({self.env_path.name})")
            with open(self.env_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {}

    @keyword
    def load_scenario_context(self, scenario_id: str):
        """Loads scenario variables into test scope, keeping Secret objects masked in logs."""
        context = self._scenario_store.get(scenario_id, {})
        for key, value in context.items():
            BuiltIn().set_test_variable(f"${{{key}}}", value)

    @keyword
    def get_user_config(self, user_ref: str) -> dict:
        """Looks up a user profile by user_id or reference (e.g. 'demouser' or 'users.demouser').
        Resolves from environment-specific users.yaml first, then fallback to global users.yaml.
        Resolves secrets from .env or system environment, wrapping passwords in Secret objects.
        Raises ValueError if required secrets are missing (no fallback allowed).
        """
        # Support namespaced reference like 'users.demouser' or 'users:demouser'
        user_id = user_ref.split('.')[-1].split(':')[-1]
        
        candidates = [
            self.root_dir / 'resources' / 'config' / 'environments' / self.env_name / 'users.yaml',
            self.root_dir / 'resources' / 'config' / 'users.yaml'
        ]
        users_file = None
        for cand in candidates:
            if cand.is_file():
                users_file = cand
                break

        if not users_file:
            raise FileNotFoundError(f"Users configuration not found in {[str(c) for c in candidates]}")
            
        with open(users_file, 'r', encoding='utf-8') as f:
            registry = yaml.safe_load(f) or {}
            
        if user_id not in registry:
            raise KeyError(f"User '{user_id}' not found in {users_file}. Available: {list(registry.keys())}")
            
        user_data = copy.deepcopy(registry[user_id])
        user_data['user_id'] = user_id
        
        # Enforce strict secret loading: no fallback password permitted
        secret_env = user_data.pop('secret_env', None)
        user_data.pop('fallback_secret', None)
        if secret_env:
            secret_val = os.environ.get(secret_env)
            if not secret_val:
                raise ValueError(
                    f"Required secret environment variable '{secret_env}' is not set in .env or system environment for user '{user_id}'!"
                )
            user_data['password'] = Secret(secret_val)
            
        return user_data

    @keyword
    def get_config_entity(self, entity_ref: str) -> dict:
        """Looks up a configuration entity using format '<config_name>.<entity_id>' or '<config_name>:<entity_id>'.
        Example: 'users.demouser' or 'users:demouser'.
        """
        delimiter = '.' if '.' in entity_ref else (':' if ':' in entity_ref else None)
        if not delimiter:
            return self.get_user_config(entity_ref)
            
        config_name, entity_id = entity_ref.split(delimiter, 1)
        if config_name == 'users':
            return self.get_user_config(entity_id)
            
        config_file = self.root_dir / 'resources' / 'config' / f"{config_name}.yaml"
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
            
        with open(config_file, 'r', encoding='utf-8') as f:
            registry = yaml.safe_load(f) or {}
            
        if entity_id not in registry:
            raise KeyError(f"Entity '{entity_id}' not found in {config_file}. Available: {list(registry.keys())}")
            
        return copy.deepcopy(registry[entity_id])

    def start_suite(self, suite):
        source_path = str(suite.source) if suite.source else ""
        if not source_path.endswith('.robot'):
            return

        # Register DataLoader as a library in the suite AST
        suite.resource.imports.library(Path(__file__).resolve().as_posix())

        # Inject environment configuration into suite variables so Test Setup can access them
        for env_k, env_v in self.env_config.items():
            suite.resource.variables.create(name=f"${{{env_k}}}", value=[str(env_v)])

        try:
            abs_source = Path(source_path).resolve()
            testcases_dir = (self.root_dir / 'testcases').resolve()
            
            try:
                rel_path = abs_source.relative_to(testcases_dir)
            except ValueError:
                rel_path = Path(abs_source.name)
            
            yaml_rel = rel_path.with_suffix('.yaml')
            
            candidates = [
                self.root_dir / 'resources' / 'config' / 'testdata' / self.env_name / yaml_rel,
                self.root_dir / 'resources' / 'config' / 'testdata' / yaml_rel
            ]
            
            yaml_path = None
            for cand in candidates:
                if cand.exists():
                    yaml_path = cand
                    break
                    
            if not yaml_path:
                print(f"[INFO] No matching YAML data found for suite: {abs_source.name}")
                return

            print(f"[OK] DataLoader loaded: {yaml_path}")
            with open(yaml_path, 'r', encoding='utf-8') as f:
                raw_data = yaml.safe_load(f) or {}

            data = resolve_env_vars(raw_data)

            for test in list(suite.tests):
                if test.name in data:
                    self._expand_test_case(suite, test, data[test.name])

        except Exception as e:
            print(f"[WARN] DataLoader error: {e}")

    def _expand_test_case(self, suite, template_test, test_config):
        suite.tests.remove(template_test)
        scenarios = test_config.get('TestScenarios', [])
        
        for index, scenario in enumerate(scenarios):
            vars_dict = scenario.get('ScenarioVars', {})
            settings = scenario.get('RunSettings', {})
            
            # 1. Merge environment config (BaseURL, Browser, Headless, Timeout)
            merged_vars = {}
            for env_k, env_v in self.env_config.items():
                merged_vars[env_k] = env_v

            # 2. Merge specific scenario variables (product_name, expected_price, user_id, etc.)
            # NOTE: User profile data is NOT flattened here; tests explicitly call `Get User Config`
            merged_vars.update(vars_dict)
            if 'expected_error' not in merged_vars:
                merged_vars['expected_error'] = None

            # Wrap any sensitive scenario fields in Secret objects before storing
            sanitized_vars = {}
            for k, v in merged_vars.items():
                if v is not None and any(sec in k.lower() for sec in ('password', 'secret', 'token', 'key', 'credential', 'auth')):
                    sanitized_vars[k] = Secret(str(v))
                else:
                    sanitized_vars[k] = v

            new_test = copy.deepcopy(template_test)
            iter_name = settings.get('IterationName', f"iter_{index+1}")
            new_test.name = f"{template_test.name} - {iter_name}"
            scenario_key = f"{suite.name}_{new_test.name}"
            self._scenario_store[scenario_key] = sanitized_vars
            
            if 'Documentation' in settings:
                new_test.doc = settings['Documentation']
                
            # Inject context loader at the beginning of the test body
            kw = new_test.body.create_keyword(name="DataLoader.Load Scenario Context")
            kw.args = (scenario_key,)
            if len(new_test.body) > 0:
                new_test.body.insert(0, new_test.body.pop())
            
            suite.tests.append(new_test)
