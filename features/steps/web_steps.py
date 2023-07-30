"""
Web Steps

Steps file for web interactions with Selenium

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""

import logging
from behave import when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

# uncomment if we use 'shopcart_' as id prefix in the index page
# ID_PREFIX = 'shopcart_'
SHOPCART_PREFIX = 'shopcart_'
ITEM_PREFIX = 'item_'


@when('I visit the "home page"')
def step_impl(context):  # pylint: disable=E223
    """ Make a call to the base URL """
    context.driver.get(context.base_url)
    # Uncomment next line to take a screenshot of the web page
    # context.driver.save_screenshot('home_page.png')


@then('I should see "{message}" in the title')
def step_impl(context, message):  # pylint: disable=E223
    """ Check the document title for a message """
    assert (message in context.driver.title)


@then('I should not see "{text_string}"')
def step_impl(context, text_string):
    element = context.driver.find_element(By.TAG_NAME, 'body')
    assert (text_string not in element.text)


@when('I visit the "{page}" api page')
def step_impl(context, page):
    if page == "Shopcart":
        context.driver.get(context.shopcart_url)
    else:
        context.driver.get(context.item_url)


@when('I press the "{button}" button in "{page}" page')
def step_impl(context, button, page):
    # button_id = 'search-shopcart-btn'
    button_id = button.lower() + '-' + page.lower() + '-btn'
    context.driver.find_element(By.ID, button_id).click()


@then('I should see the message "{message}"')
def step_impl(context, message):
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'flash_message'),
            message
        )
    )
    assert (found)


@then('I should see "{name}" in the results in "{page}" page')
def step_impl(context, name, page):
    if page == "Shopcart":
        search_results = 'search_shopcarts_results'
    else:
        search_results = 'search_items_results'
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, search_results),
            name
        )
    )
    assert (found)


@then('I should not see "{name}" in the results in "{page}" page')
def step_impl(context, name, page):
    if page == "Shopcart":
        search_results = 'search_shopcarts_results'
    else:
        search_results = 'search_items_results'
    element = context.driver.find_element(By.ID, search_results)
    assert (name not in element.text)


@when('I set the "{element_name}" to "{text_string}" in "{page}" page')
def step_impl(context, element_name, text_string, page):
    if page == "Shopcart":
        ID_PREFIX = SHOPCART_PREFIX
    else:
        ID_PREFIX = ITEM_PREFIX
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(text_string)


@then('the "{element_name}" field should be empty in "{page}" page')
def step_impl(context, element_name, page):
    if page == "Shopcart":
        ID_PREFIX = SHOPCART_PREFIX
    else:
        ID_PREFIX = ITEM_PREFIX
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = context.driver.find_element(By.ID, element_id)
    assert (element.get_attribute('value') == u'')


##################################################################
# These two function simulate copy and paste
##################################################################
@when('I copy the "{element_name}" field in "{page}" page')
def step_impl(context, element_name, page):
    if page == "Shopcart":
        ID_PREFIX = SHOPCART_PREFIX
    else:
        ID_PREFIX = ITEM_PREFIX
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute('value')
    logging.info('Clipboard contains: %s', context.clipboard)


@when('I paste the "{element_name}" field in "{page}" page')
def step_impl(context, element_name, page):
    if page == "Shopcart":
        ID_PREFIX = SHOPCART_PREFIX
    else:
        ID_PREFIX = ITEM_PREFIX
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)


@when('I set the "{element_name}" within clipboard in "{page}" page')
def step_impl(context, element_name, page):
    if page == "Shopcart":
        ID_PREFIX = SHOPCART_PREFIX
    else:
        ID_PREFIX = ITEM_PREFIX
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(context.clipboard)


@then('I should see "{text_string}" in the "{element_name}" field in "{page}" page')
def step_impl(context, text_string, element_name, page):
    if page == "Shopcart":
        ID_PREFIX = SHOPCART_PREFIX
    else:
        ID_PREFIX = ITEM_PREFIX
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id),
            text_string
        )
    )
    assert (found)


@when('I change "{element_name}" to "{text_string}" in "{page}" page')
def step_impl(context, element_name, text_string, page):
    if page == "Shopcart":
        ID_PREFIX = SHOPCART_PREFIX
    else:
        ID_PREFIX = ITEM_PREFIX
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)
