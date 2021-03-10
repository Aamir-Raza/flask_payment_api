Module payment_app
==================

Functions
---------
  
`ProcessPayment()`
:   Process a Credit Card payment given the following request:
    
    - CreditCardNumber (mandatory, string, it should be a valid credit card number)
    - CardHolder: (mandatory, string)
    - ExpirationDate (mandatory, DateTime, it cannot be in the past)
    - SecurityCode (optional, string, 3 digits)
    - Amount (mandatory decimal, positive amount) - Capped to anything under a million