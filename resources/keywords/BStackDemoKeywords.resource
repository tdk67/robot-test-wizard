*** Settings ***
Documentation    High-level business keywords for BStackDemo e-commerce application.
...              Environment parameters (BaseURL, Browser, Headless, Timeout) are
...              supplied dynamically by DataLoader from environment configuration.
Library          Browser
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

Logout From Store
    [Documentation]    Logs out of the store if an active session is detected.
    ${is_logged_in}=    Get Element States    text="Logout"    then    bool(value & visible)
    IF    ${is_logged_in}
        Click    text="Logout"
        Wait For Elements State    id=signin    visible
    END

Close Demo Store
    [Documentation]    Teardown keyword: captures deterministic failure screenshot and ensures clean logout.
    Run Keyword If Test Failed    Take Screenshot    filename=${OUTPUT_DIR}/failure_${TEST_NAME}.png
    Run Keyword And Ignore Error    Logout From Store
    Close Browser
