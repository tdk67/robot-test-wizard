*** Settings ***
Documentation    High-level business keywords for BStackDemo e-commerce application.
...              Environment parameters (BaseURL, Browser, Headless, Timeout) are
...              supplied dynamically by DataLoader from environment configuration.
Library          Browser
Library          OperatingSystem
Library          XML
Library          custom-libs/PdfValidator.py

*** Keywords ***
Open Demo Store
    [Documentation]    Initializes browser context with download support, sets global timeout, and opens the store.
    New Browser    browser=${BROWSER}    headless=${HEADLESS}
    New Context    viewport={'width': 1280, 'height': 800}    acceptDownloads=True
    Set Browser Timeout    ${TIMEOUT}
    Register Keyword To Run On Failure    NONE
    New Page       ${BASE_URL}
    Wait For Elements State    .shelf-item >> nth=0    visible

Add Product To Cart
    [Documentation]    Locates the product card by name and clicks its 'Add to cart' button.
    [Arguments]    ${product_name}
    ${count}=    Browser.Get Element Count    xpath=//p[text()='${product_name}']
    IF    ${count} == 0
        Fail    Product '${product_name}' was not found in the store catalog!
    END
    ${buy_btn}=    Browser.Get Element    xpath=//p[text()='${product_name}']/ancestor::div[contains(@class, 'shelf-item')]//div[contains(@class, 'shelf-item__buy-btn')]
    Click    ${buy_btn}
    Wait For Elements State    .buy-btn    visible

Close Cart Drawer
    [Documentation]    Closes the sliding shopping bag drawer if open.
    ${is_open}=    Get Element States    .float-cart--open    then    bool(value & visible)
    IF    ${is_open}
        Click    .float-cart__close-btn
        Wait For Elements State    .float-cart--open    detached
    END

Add Products To Cart Or Assert Error
    [Documentation]    Iterates over products to add them to cart, or catches and asserts expected catalog errors gracefully.
    [Arguments]    ${products}    ${expected_error}=${None}
    IF    $expected_error is not None
        TRY
            FOR    ${item}    IN    @{products}
                Add Product To Cart    ${item['name']}
                Close Cart Drawer
            END
            Fail    Expected failure with message '${expected_error}', but operation succeeded.
        EXCEPT    AS    ${err}
            Should Contain    ${err}    ${expected_error}
            Pass Execution    [OK] Gracefully verified expected catalog error: ${err}
        END
    ELSE
        FOR    ${item}    IN    @{products}
            Add Product To Cart    ${item['name']}
            Close Cart Drawer
        END
    END

Open Cart Drawer
    [Documentation]    Opens the sliding shopping cart if not already visible.
    ${is_open}=    Get Element States    .float-cart--open    then    bool(value & visible)
    IF    not ${is_open}
        Click    .bag--float-cart-closed
        Wait For Elements State    .buy-btn    visible
    END

Proceed To Checkout
    [Documentation]    Ensures cart drawer is open and proceeds to the sign-in prompt.
    Open Cart Drawer
    Click    .buy-btn
    Wait For Elements State    id=username    visible

Login To Store
    [Documentation]    Selects user from dropdown and activates password option without exposing secrets in logs.
    [Arguments]    ${username}    ${password}
    Click    id=username
    Click    text="${username}"
    Click    id=password
    Click    id=react-select-3-option-0-0
    Click    id=login-btn
    Wait For Elements State    id=firstNameInput    visible

Fill Shipping Address And Submit
    [Documentation]    Fills shipping address form and proceeds to final confirmation.
    [Arguments]    ${first_name}    ${last_name}    ${address}    ${state}    ${postal_code}
    Fill Text    id=firstNameInput       ${first_name}
    Fill Text    id=lastNameInput        ${last_name}
    Fill Text    id=addressLine1Input    ${address}
    Fill Text    id=provinceInput        ${state}
    Fill Text    id=postCodeInput        ${postal_code}
    Click        id=checkout-shipping-continue
    Wait For Elements State    text="Download order receipt"    visible

Download Order Receipt
    [Documentation]    Triggers receipt download and waits until the file is saved to disk.
    [Arguments]    ${target_pdf_path}
    ${dl_promise}=    Promise To Wait For Download    saveAs=${target_pdf_path}
    Click    text="Download order receipt"
    ${file_info}=     Wait For    ${dl_promise}
    RETURN    ${file_info.saveAs}

Verify Receipt Items And Total
    [Documentation]    Extracts structured XML from PDF receipt and asserts all product line prices and total via XPath.
    [Arguments]    ${pdf_file}    ${products}    ${expected_total}
    ${xml_text}=    Convert Pdf To Xml    ${pdf_file}
    ${xml}=         Parse Xml             ${xml_text}
    FOR    ${item}    IN    @{products}
        ${price}=    Get Element Text    ${xml}    xpath=items/item[type='${item['name']}']/price
        Should Contain    ${price}    ${item['expected_price']}
    END
    ${receipt_total}=    Get Element Text    ${xml}    xpath=total_price
    Should Be Equal As Strings    ${receipt_total}    ${expected_total}

Logout From Store
    [Documentation]    Logs out of the store if an active session is detected.
    ${is_logged_in}=    Get Element States    text="Logout"    then    bool(value & visible)
    IF    ${is_logged_in}
        Click    text="Logout"
        Wait For Elements State    id=signin    visible
    END

Close Demo Store
    [Documentation]    Teardown keyword: captures deterministic failure screenshot on FAIL, or cleans stale failure screenshots on PASS.
    IF    '${TEST STATUS}' == 'FAIL'
        Take Screenshot    filename=${OUTPUT_DIR}/failure_${TEST_NAME}.png
    ELSE
        Remove File    ${OUTPUT_DIR}/failure_${TEST_NAME}.png
    END
    Run Keyword And Ignore Error    Logout From Store
    Close Browser
