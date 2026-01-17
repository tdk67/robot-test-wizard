import os
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from robot.api.deco import keyword, library

@library
class ContextBuilder:
    """
    The Core Engine for the Data-Driven Architecture.
    Handles Registry Loading, Input Validation, and Jinja2 Templating.
    """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        self.registry_cache = {}
        # Setup Jinja2 to load from resources/templates
        template_dir = os.path.join(os.getcwd(), 'resources', 'templates')
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['json'])
        )

    @keyword
    def load_registry(self, product, component, version):
        """Loads the YAML registry for a specific component version."""
        file_path = os.path.join(
            os.getcwd(), 'resources', 'registry', product, component, f"{version}.yaml"
        )
        with open(file_path, 'r') as f:
            self.registry_cache[f"{product}.{component}"] = yaml.safe_load(f)
        print(f"✅ Loaded Registry: {product}.{component} ({version})")

    @keyword
    def build_payload(self, product, component, command, input_data):
        """
        Constructs the JSON payload by combining:
        1. Registry Rules (Structure, Defaults)
        2. Input Data (Test Data)
        3. Jinja2 Templates
        """
        registry = self.registry_cache.get(f"{product}.{component}")
        if not registry:
            raise ValueError(f"Registry not loaded for {product}.{component}")

        cmd_def = registry['commands'].get(command)
        if not cmd_def:
            raise ValueError(f"Command '{command}' not found in registry.")

        # 1. Validate Inputs (Contract Check)
        self._validate_inputs(cmd_def.get('inputs', {}), input_data)

        # 2. Build Structure (The "Context Builder" Pattern)
        active_sections = self._process_structure(cmd_def.get('structure', {}), input_data, registry)

        # 3. Render Master Template
        template_name = cmd_def['template']
        template = self.env.get_template(template_name)
        
        # Inject the pre-processed sections into the template
        final_json = template.render(
            active_sections=active_sections, 
            **input_data # Pass raw data too for simple fields
        )
        
        return final_json

    def _validate_inputs(self, rules, data):
        """Enforces the 'Input Contract'."""
        required = rules.get('required', [])
        missing = [key for key in required if key not in data]
        if missing:
            raise ValueError(f"❌ Contract Violation! Missing required inputs: {missing}")

    def _process_structure(self, structure_map, data, registry):
        """
        Iterates over the structure map to decide what to include.
        Handles: optionality, lists, and recursive fragments.
        """
        active_sections = {}
        component_map = registry.get('components', {})

        for section_name, rules in structure_map.items():
            json_key = rules['key']
            
            # CHECK 1: Is this a List?
            if rules.get('type') == 'list':
                source_list = data.get(rules['source'], [])
                if not source_list and rules.get('omit_if_empty', True):
                    continue # Skip empty list
                
                # Render list items
                item_template_ref = rules['item_template']
                item_template_file = component_map.get(item_template_ref)
                
                rendered_items = []
                for item_data in source_list:
                    t = self.env.get_template(item_template_file)
                    rendered_items.append(t.render(item=item_data))
                
                # Jinja will receive this as a list of strings (JSON objects)
                # We join them here or handle in template. Let's return the list.
                # Actually, better to return the list object so Jinja can loop cleanly.
                active_sections[json_key] = "[" + ",".join(rendered_items) + "]"
                continue

            # CHECK 2: Is this Optional?
            if not rules.get('required', True):
                # Heuristic: If none of the input data relevant to this block exists, skip it?
                # Simpler: If the specific input variable is None/Missing.
                # For now, let's assume if it's in the structure, we try to render it 
                # unless explicitly toggled off in input data? 
                # (Refinement needed based on your specific logic preferences)
                pass 

            # CHECK 3: Standard Fragment Render
            template_ref = rules.get('template_ref') # e.g., "Standard_Contact"
            if template_ref:
                template_file = component_map.get(template_ref)
                t = self.env.get_template(template_file)
                active_sections[json_key] = t.render(**data)
        
        return active_sections