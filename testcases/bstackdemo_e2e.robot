*** Settings ***
Documentation    End-to-End E-Commerce Flow: Multi-Product Selection, Checkout, Login, and Structured PDF Receipt Verification.
...              All test data and environment configurations are injected dynamically
...              by the DataLoader pre-run modifier following the LEGO architecture.
Resource         ../resources/keywords/BStackDemoKeywords.resource
Test Setup       Open Demo Store
Test Teardown    Close Demo Store

*** Test Cases ***
BStackDemo E2E Checkout Flow
    [Documentation]    Executes product selection, checkout, and receipt verification as a clear, sequential workflow.
    ${user}=    Get User Config    ${user_id}
    
    Add Products To Cart Or Assert Error    ${products}              expected_error=${expected_error}
    Proceed To Checkout
    Login To Store                          ${user['username']}      ${user['password']}
    Fill Shipping Address And Submit        ${user['first_name']}    ${user['last_name']}    ${user['address']}    ${user['state']}    ${user['postal_code']}
    ${pdf_file}=    Download Order Receipt  ${OUTPUT_DIR}/receipt_${TEST_NAME}.pdf
    Verify Receipt Items And Total          ${pdf_file}              ${products}             ${expected_total}
