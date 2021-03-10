Flask Payment Web API
=====================

Flask Web API I was asked to create as part of a test, does not include the 'MOD 10 algorithm' check for credit card numbers (assume they are correct for test purposes). Written in Python 3.9.

To run the app, download the files, install the External Libraries listed below (manually or using provided Pipfile), and then run the following command in a shell: `flask run`

Functions
---------
  
`ProcessPayment()`
:   Process a Credit Card payment given the following request:
    
    - CreditCardNumber (mandatory, string, it should be a valid credit card number)
    - CardHolder: (mandatory, string)
    - ExpirationDate (mandatory, DateTime, it cannot be in the past)
    - SecurityCode (optional, string, 3 digits)
    - Amount (mandatory decimal, positive amount) - Capped to anything under a million

External Libraries
-------------------
*   Flask-WTF==0.14.3
*   WTForms-Components==0.10.5
