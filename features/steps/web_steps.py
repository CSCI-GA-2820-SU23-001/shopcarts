"""
Web Steps

Steps file for web interactions with Selenium

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
from behave import when, then
from selenium.webdriver.common.by import By

# uncomment if we use 'shopcart_' as id prefix in the index page
# ID_PREFIX = 'shopcart_'


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
