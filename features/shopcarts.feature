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

    Given the following items
        | shopcart_name | name       | quantity  | price |
        | Wan-Yu        | Apple      | 1         | 1.99  |
        | Wan-Yu        | Mango      | 1         | 5.00  |

Scenario: The server is running
    When I visit the "home page"
    Then I should see "Shopcarts Service" in the title
    And  I should not see "404 Not Found"
