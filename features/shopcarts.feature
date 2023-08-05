Feature: The shopcarts service backend
    As an E-Commerce Owner
    I need a RESTful shopcarts service
    So that I can keep track of all the shopcarts in the system

Background:
    Given the following shopcarts
        | name       |
        | Emily      |
        | Kangle     |
        | Wan-Yu     |
        | Yuzhao     |
        | Zihan      |
        | Lily       |

    Given the following items
        | shopcart_name | name       | quantity  | price |
        | Wan-Yu        | Apple      | 1         | 1.99  |
        | Wan-Yu        | Mango      | 1         | 5.00  |
        | Wan-Yu        | Orange     | 1         | 3.99  |
        | Yuzhao        | Apple      | 1         | 1.99  |

Scenario: The server is running
    When I visit the "home page"
    Then I should see "Shopcarts Service" in the title
    And  I should not see "404 Not Found"

Scenario: Create a Shopcart
    When I visit the "Shopcart" api page
    And I set the "Name" to "Jerry" in "Shopcart" page
    And I press the "Create" button in "Shopcart" page
    Then I should see the message "Shopcart created!"
    When I copy the "Id" field in "Shopcart" page
    And I press the "Reset Form" button on "Shopcart" page
    Then the "Id" field should be empty in "Shopcart" page
    Then the "Name" field should be empty in "Shopcart" page
    When I paste the "Id" field in "Shopcart" page
    And I press the "Retrieve" button in "Shopcart" page
    Then I should see the message "Success"
    And I should see "Jerry" in the "Name" field in "Shopcart" page

Scenario: Get a Shopcart
    When I visit the "Shopcart" api page
    And I set the "Name" to "Wan-Yu" in "Shopcart" page
    And I press the "Search" button in "Shopcart" page
    Then I should see the message "Success"
    And I should see "Wan-Yu" in the results in "Shopcart" page
    And I should see "Orange" in the results in "Shopcart" page
    And I should see "3.99" in the results in "Shopcart" page
    And I should not see "Erica" in the results in "Shopcart" page
    And I should not see "Peach" in the results in "Shopcart" page    

Scenario: Update a Shopcart
    When I visit the "Shopcart" api page
    And I set the "Name" to "Yuzhao" in "Shopcart" page
    And I press the "Search" button in "Shopcart" page
    Then I should see the message "Success"
    And I should see "Yuzhao" in the "Name" field in "Shopcart" page
    When I change "Name" to "Erica" in "Shopcart" page
    And I press the "Update" button in "Shopcart" page
    Then I should see the message "Shopcart updated!"
    When I copy the "Id" field in "Shopcart" page
    And I press the "Reset Form" button on "Shopcart" page
    And I paste the "Id" field in "Shopcart" page
    And I press the "Retrieve" button in "Shopcart" page
    Then I should see the message "Success"
    And I should see "Erica" in the "Name" field in "Shopcart" page
    When I press the "Reset Form" button on "Shopcart" page
    And I press the "Search" button in "Shopcart" page
    Then I should see the message "Success"
    And I should see "Erica" in the results in "Shopcart" page
    And I should not see "Yuzhao" in the results in "Shopcart" page

Scenario: Delete a Shopcart
    When I visit the "Shopcart" api page
    And I set the "Name" to "Lily" in "Shopcart" page
    And I press the "Search" button in "Shopcart" page
    Then I should see the message "Success"
    And I should see "Lily" in the results in "Shopcart" page
    When I copy the "Id" field in "Shopcart" page
    And I press the "Reset Form" button on "Shopcart" page
    And I paste the "Id" field in "Shopcart" page
    When I press the "Delete" button in "Shopcart" page
    Then I should see the message "Shopcart deleted!"
    When I press the "Search" button in "Shopcart" page
    Then I should see the message "Success"
    And I should not see "Lily" in the results in "Shopcart" page

Scenario: Clear shopcart items
    When I visit the "Shopcart" api page
    And I set the "Name" to "Wan-Yu" in "Shopcart" page
    And I press the "Search" button in "Shopcart" page
    Then I should see the message "Success"
    And I should see "Wan-Yu" in the results in "Shopcart" page
    And I should see "Apple" in the results in "Shopcart" page
    And I should see "Mango" in the results in "Shopcart" page
    And I should see "Orange" in the results in "Shopcart" page
    When I copy the "Id" field in "Shopcart" page
    And I press the "Reset Form" button on "Shopcart" page
    And I paste the "Id" field in "Shopcart" page
    When I press the "Clear" button in "Shopcart" page
    Then I should see the message "Shopcart items cleared!"
    When I paste the "Id" field in "Shopcart" page
    And I set the "Name" to "Wan-Yu" in "Shopcart" page
    And I press the "Search" button in "Shopcart" page
    Then I should see the message "Success"
    And I should see "Wan-Yu" in the results in "Shopcart" page
    And I should not see "Apple" in the results in "Shopcart" page
    And I should not see "Mango" in the results in "Shopcart" page
    And I should not see "Orange" in the results in "Shopcart" page

Scenario: List all shopcarts
    When I visit the "Shopcart" api page
    And I press the "Search" button in "Shopcart" page
    Then I should see the message "Success"
    And I should see "Emily" in the results in "Shopcart" page
    And I should see "Kangle" in the results in "Shopcart" page
    And I should see "Wan-Yu" in the results in "Shopcart" page
    And I should see "Apple" in the results in "Shopcart" page
    And I should see "Mango" in the results in "Shopcart" page
    And I should see "Orange" in the results in "Shopcart" page
    And I should see "Yuzhao" in the results in "Shopcart" page
    And I should see "Apple" in the results in "Shopcart" page
    And I should see "Zihan" in the results in "Shopcart" page
    And I should see "Lily" in the results in "Shopcart" page

Scenario: Create an item under a shopcart
    When I visit the "Shopcart" api page
    And I set the "Name" to "Yuzhao" in "Shopcart" page
    And I press the "Search" button in "Shopcart" page
    Then I should see the message "Success"
    When I copy the "Id" field in "Shopcart" page
    And I visit the "Item" api page
    And I set the "Shopcart ID" within clipboard in "Item" page
    And I press the "List" button in "Item" page
    Then I should see the message "Success"
    And I should see "Apple" in the results in "Item" page
    And I should see "1.99" in the results in "Item" page
    And I should not see "Peach" in the results in "Item" page
    And I should not see "4.99" in the results in "Item" page
    When I press the "Reset Form" button on "Item" page
    And I set the "Name" to "Peach" in "Item" page
    And I set the "Quantity" to "1" in "Item" page
    And I set the "Price" to "4.99" in "Item" page
    And I press the "Create" button in "Item" page
    Then I should see the message "Shopcart item created!"
    When I press the "Reset Form" button on "Item" page
    And I press the "List" button in "Item" page
    Then I should see the message "Success"
    And I should see "Apple" in the results in "Item" page
    And I should see "1.99" in the results in "Item" page
    And I should see "Peach" in the results in "Item" page
    And I should see "4.99" in the results in "Item" page

Scenario: List all items in a shopcart
    When I visit the "Shopcart" api page
    And I set the "Name" to "Wan-Yu" in "Shopcart" page
    And I press the "Search" button in "Shopcart" page
    Then I should see the message "Success"
    When I copy the "Id" field in "Shopcart" page
    And I visit the "Item" api page
    And I set the "Shopcart ID" within clipboard in "Item" page
    And I press the "List" button in "Item" page
    Then I should see the message "Success"
    And I should see "Apple" in the results in "Item" page
    And I should see "1" in the results in "Item" page
    And I should see "1.99" in the results in "Item" page
    And I should see "Mango" in the results in "Item" page
    And I should see "5" in the results in "Item" page
    And I should see "Orange" in the results in "Item" page
    And I should see "3.99" in the results in "Item" page
    And I should not see "Peach" in the results in "Item" page

Scenario: Get a shopcart item
    When I visit the "Shopcart" api page
    And I set the "Name" to "Wan-Yu" in "Shopcart" page
    And I press the "Search" button in "Shopcart" page
    Then I should see the message "Success"
    And I should see "Wan-Yu" in the results in "Shopcart" page
    And I should see "Apple" in the results in "Shopcart" page
    And I should see "Mango" in the results in "Shopcart" page
    And I should see "Orange" in the results in "Shopcart" page
    When I copy the "Id" field in "Shopcart" page
    And I visit the "Item" api page
    And I set the "Shopcart ID" within clipboard in "Item" page
    When I press the "List" button in "Item" page
    Then I should see the message "Success"
    And I should see "Apple" in the results in "Item" page
    And I should see "Mango" in the results in "Item" page
    And I should see "Orange" in the results in "Item" page
    When I copy the "Id" field in "Item" page
    And I press the "Reset Form" button on "Item" page
    And I paste the "Id" field in "Item" page
    And I press the "Retrieve" button in "Item" page
    Then I should see the message "Success"
    And I should see "Apple" in the results in "Item" page

Scenario: Delete a shopcart item
    When I visit the "Shopcart" api page
    And I set the "Name" to "Wan-Yu" in "Shopcart" page
    And I press the "Search" button in "Shopcart" page
    Then I should see the message "Success"
    And I should see "Wan-Yu" in the results in "Shopcart" page
    And I should see "Apple" in the results in "Shopcart" page
    And I should see "Mango" in the results in "Shopcart" page
    And I should see "Orange" in the results in "Shopcart" page
    When I copy the "Id" field in "Shopcart" page
    And I visit the "Item" api page
    And I set the "Shopcart ID" within clipboard in "Item" page
    When I press the "List" button in "Item" page
    Then I should see the message "Success"
    And I should see "Apple" in the results in "Item" page
    And I should see "Mango" in the results in "Item" page
    And I should see "Orange" in the results in "Item" page
    When I copy the "Id" field in "Item" page
    And I press the "Reset Form" button on "Item" page
    And I paste the "Id" field in "Item" page
    And I press the "Delete" button in "Item" page
    Then I should see the message "Item deleted from shopcart!"
    When I press the "List" button in "Item" page
    Then I should see the message "Success"
    And I should not see "Apple" in the results in "Item" page
    And I should see "Mango" in the results in "Item" page
    And I should see "Orange" in the results in "Item" page
