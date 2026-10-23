*** Settings ***
Documentation    End-to-End E-Commerce Flow: Multi-Product Selection, Checkout, Login, and Structured PDF Receipt Verification via XML XPath.
...              All test data and environment configurations are injected dynamically
...              by the DataLoader pre-run modifier following the LEGO architecture.
Library          XML
Resource         ../resources/keywords/BStackDemoKeywords.resource
Test Setup       Open Demo Store
Test Teardown    Close Demo Store

*** Test Cases ***
BStackDemo E2E Checkout Flow
    [Documentation]    Executes the e2e product purchase flow and verifies the downloaded PDF receipt via XML XPath.
    ${user}=    Get User Config    ${user_id}
    
    # Handle negative test scenarios using Robot Framework TRY / EXCEPT
    IF    $expected_error is not None
        TRY
            FOR    ${item}    IN    @{products}
                Add Product To Cart    ${item['name']}
                Close Cart Drawer
            END
            Fail    Expected failure with message '${expected_error}', but operation succeeded.
        EXCEPT    AS    ${err}
            Should Contain    ${err}    ${expected_error}
            Log    [OK] Gracefully verified expected catalog error: ${err}
        END
    ELSE
        # Standard positive checkout flow
        FOR    ${item}    IN    @{products}
            Add Product To Cart    ${item['name']}
            Close Cart Drawer
        END
        
        Proceed To Checkout
        Login To Store                      ${user['username']}      ${user['password']}
        Fill Shipping Address And Submit    ${user['first_name']}    ${user['last_name']}    ${user['address']}    ${user['state']}    ${user['postal_code']}
        ${pdf_file}=    Download Order Receipt    ${OUTPUT_DIR}/receipt_${TEST_NAME}.pdf
        
        # Convert PDF receipt to structured XML for transparent XPath verification
        ${xml_text}=    Convert Pdf To Xml    ${pdf_file}
        ${xml}=         Parse Xml             ${xml_text}
        
        # Verify every selected product and its line price via XPath
        FOR    ${item}    IN    @{products}
            ${price}=    Get Element Text    ${xml}    xpath=items/item[type='${item['name']}']/price
            Should Contain    ${price}    ${item['expected_price']}
        END
        
        # Verify calculated total price on the receipt via XPath
        ${receipt_total}=    Get Element Text    ${xml}    xpath=total_price
        Should Be Equal As Strings    ${receipt_total}    ${expected_total}
    END
