*** Settings ***
Documentation    Enterprise Data-Driven Hello World

*** Variables ***
${log_message}    Default Message
${user_type}      UNKNOWN

*** Test Cases ***
Generic Hello Test
    [Documentation]    Uses ScenarioVars from YAML.
    Log To Console     \n------------------------------
    Log To Console     CASE: ${TEST NAME}
    Log To Console     USER: ${user_type}
    Log To Console     MSG: ${log_message} 
    Log To Console     ------------------------------