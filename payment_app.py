# Local imports
import datetime
import re
import unittest
from decimal import Decimal
from decimal import getcontext
#import unittest
import secrets
import sys

# External imports
from flask import Flask, escape, request, Response, render_template
from flask_wtf.csrf import CSRFProtect

# Script import
from payment_form import PaymentForm

csrf = CSRFProtect()
app = Flask(__name__, template_folder="templates")
csrf.init_app(app)

key = secrets.token_urlsafe(16)

# Setup App config incl. secret key
app.config.update(
    TESTING=True,
    DEBUG=True,
    FLASK_ENV='development',
    SECRET_KEY=key,
)

output = ""

# ====================
# Payment Gateways
# ====================

def CheapPaymentGateway(CreditCardNumber, CardHolder, ExpirationDate, SecurityCode, Amount):

    last4_cc = str(CreditCardNumber)[-4:]
    output = "\nProcessed Payment of ${:,.2f} for {} with CheapPaymentGateway, Card ending in {}\n".format(Amount, CardHolder, last4_cc)
    print(output)
    return (1, output)

def ExpensivePaymentGateway(CreditCardNumber, CardHolder, ExpirationDate, SecurityCode, Amount):

    last4_cc = str(CreditCardNumber)[-4:]
    output = "\nProcessed Payment of ${:,.2f} for {} with ExpensivePaymentGateway, Card ending in {}\n".format(Amount, CardHolder, last4_cc)
    print(output)
    return (1, output)

def PremiumPaymentGateway(CreditCardNumber, CardHolder, ExpirationDate, SecurityCode, Amount):

    last4_cc = str(CreditCardNumber)[-4:]
    output = "\nProcessed Payment of ${:,.2f} for {} with PremiumPaymentGateway, Card ending in {}\n".format(Amount, CardHolder, last4_cc)
    print(output)
    return (1, output)

@app.route("/", methods=("GET","POST"))
def ProcessPayment():
    """
    Process a Credit Card payment given the following request:

    - CreditCardNumber (mandatory, string, it should be a valid credit card number)
    - CardHolder: (mandatory, string)
    - ExpirationDate (mandatory, DateTime, it cannot be in the past)
    - SecurityCode (optional, string, 3 digits)
    - Amount (mandatory decimal, positive amount) - Capped to anything under a million

    """

    form = PaymentForm(request.form)

    if form.validate_on_submit():

        card_num = form.CreditCardNumber.data.strip().replace(" ","")
        card_holder = str(form.CardHolder.data).strip().upper()
        expiry_date = form.ExpirationDate.data
        security_code = str(form.SecurityCode.data)
        amount = form.Amount.data

        card_num_len = len(card_num)

        try:

            # ====================
            # Card Number Check
            # "Assume" provided card numbers pass MOD 10 algorithm
            # if they satisfy provided conditions below
            # ====================
            if card_num_len in [13,15,16] and card_num.isdigit():
                # Visa Card
                if (card_num_len == 13 or card_num_len == 16) and card_num.startswith('4'):
                    pass
                # Mastercard
                elif card_num_len == 16 and card_num.startswith('5'):
                    pass
                # AMEX
                elif card_num_len == 15 and (card_num.startswith('34') or card_num.startswith('37')):
                    pass
                # Discover
                elif card_num_len == 16 and card_num.startswith('6'):
                    pass
                else:
                    print("Invalid Card Number\n")
                    return 'The request is invalid', 400
            else:
                print("Invalid Card Number: {}\n".format(card_num))
                return 'The request is invalid', 400

            card_num = int(card_num)

            print("Passed Card Num check")

            # ====================
            # CardHolder Check
            # Assume min/max 2-24 characters for First Name and same for Last Name
            # Min Length 5: 2 characters for First Name, 1 for space, 2 for Last Name
            # ====================

            if len(card_holder) > 4:

                verify_name = bool(re.match(r'^[A-Z]{2,24} [A-Z]{2,24}$', card_holder))
                print("Card Holder ({}) Verified: {}".format(card_holder,verify_name))

                if not verify_name:
                    print("Card Holder Value Invalid!\n")
                    return 'The request is invalid', 400
                else:
                    print("Valid Card Holder")

            else:
                print("Card Holder Value Invalid!\n")
                return 'The request is invalid', 400

            # ====================
            # Expiration Check
            # ====================
            if type(expiry_date) is not datetime.date:

                print("Invalid Expiry Date: {}\n".format(expiry_date))
                # bad request
                return 'The request is invalid', 400

            # ====================
            # Amount Check
            # 1-2 decimal places should be present - invalid if more
            # Positive values only, example: 0.50, 1.51, 520.55
            # Max: 999999.99
            # ====================

            # Precision of digits which Decimal lib will use to return
            # any calculated number
            getcontext().prec = 8

            # Use regex to match what an amount would look like
            # Max amount is limited to 999999.99 (assumption)
            # 6 digits before & 2 after decimal
            if bool(re.match(r'^[0-9]{1,6}\.[0-9]{1,2}$', str(amount))):
                amount = Decimal(amount).quantize(Decimal('1.00'))
                print("Amount valid: {}".format(str(amount)))
            else:
                print("Amount Invalid: {}\n".format(str(amount)))
                # bad request
                return 'The request is invalid', 400

            # ====================
            # If Security Code is present, verify (ignore if not)
            # This assumes a security code field is present or not (it would be empty if not)
            # ====================
            if security_code != "":

                security_str = str(security_code).strip()

                if security_str.isdigit() and len(security_str) == 3:
                    print("Valid Security Code")
                    security_code = int(security_code)
                else:
                    print("Invalid Security Code: {}\n".format(str(security_code)))
                    # bad request
                    return 'The request is invalid', 400

        except Exception as e:
            print("Exception Raised: {}\n".format(e))
            return 'Internal server error', 500

        retry = 0

        # ====================
        # Payment Processor
        # Assume payment processor has boolean return on successful payment
        # ====================

        if amount <= 20:

            last4_cc = str(CreditCardNumber)[-4:]
            ret, output = CheapPaymentGateway(card_num,card_holder, expiry_date,security_code,amount)
            if ret:
                #return 'Payment is processed', 200
                return output, 200
            else:
                return 'Internal server error: PaymentProcessor Failed', 500

        elif 20 < amount < 501:
            while retry < 2:
                ret, output = ExpensivePaymentGateway(card_num,card_holder, expiry_date,security_code,amount)
                if ret:
                    #return 'Payment is processed', 200
                    return output, 200
                else:
                    retry += 1

            print("Could not process payment with ExpensivePaymentGateway")
            return 'Internal server error: PaymentProcessor Failed', 500

        else:
            while retry < 3:
                ret, output = PremiumPaymentGateway(card_num, card_holder, expiry_date, security_code, amount)
                if ret:
                    #return 'Payment is processed', 200
                    return output, 200
                else:
                    retry += 1
            print("Could not process payment with PremiumPaymentGateway")
            return 'Internal server error: PaymentProcessor Failed', 500


    return render_template("layout.html", form=form)

# =======================================================================================
# Unit Tests were run without Flask
# =======================================================================================
# class PaymentTests(unittest.TestCase):

#     def test_invalidCardNum(self):
#         self.assertEqual(ProcessPayment("4520 8505 0505 123", "Andrew Jackson", datetime.date(2022, 5, 13), None, 5), 400)

#     def test_invalidCardNum2(self):
#         self.assertEqual(ProcessPayment("6520 8505 0505 1234", "Kim Possible", datetime.date(2022, 5, 13), None, 5), 400)

#     def test_invalidCardNum3(self):
#         self.assertEqual(ProcessPayment("3520 8505 0505 1234", "Kristen StEWarT", datetime.date(2022, 5, 13), None, 5), 400)

#     def test_invalidCardNum3(self):
#         self.assertEqual(ProcessPayment("4520 8505 0505/1234", "Matt damon", datetime.date(2022, 5, 13), None, 5), 400)

#     def test_invalidCardNum3(self):
#         self.assertEqual(ProcessPayment("4520 8505 0505 13ab", "alison Brie", datetime.date(2022, 5, 13), None, 5), 400)

#     def test_missingHolder(self):
#         self.assertEqual(ProcessPayment("4520 8505 0505 1234", "", datetime.date(2020, 5, 13), None, 5), 400)

#     def test_missingHolder2(self):
#         self.assertEqual(ProcessPayment("4520 8505 0505 1234", " ", datetime.date(2020, 5, 13), None, 5), 400)

#     def test_invalidHolder(self):
#         self.assertEqual(ProcessPayment("4520 8505 0505 1234", "Bob?", datetime.date(2020, 5, 13), None, 5), 400)

#     def test_invalidHolder2(self):
#         self.assertEqual(ProcessPayment("4520 8505 0505 1234", "Al A", datetime.date(2020, 5, 13), None, 5), 400)

#     def test_invalidHolder2(self):
#         self.assertEqual(ProcessPayment("4520 8505 0505 1234", 123456, datetime.date(2020, 5, 13), None, 5), 400)

#     def test_expiredDate(self):
#         self.assertEqual(ProcessPayment("4520 8505 0505 1234", "Galistotle Tok", datetime.date(2018, 5, 13), None, 5), 400)

#     def test_expiredDate2(self):
#         self.assertEqual(ProcessPayment("4520 8505 0505 1234", "Mad Max", datetime.date(2021, 1, 22), None, 5), 400)

#     def test_invalidExpiry(self):
#         self.assertEqual(ProcessPayment("4520 8505 0505 1234", "Michael Phelps", "", None, 5), 400)

#     def test_invalidExpiry2(self):
#         self.assertEqual(ProcessPayment("4520 8505 0505 1234", "Andrew Jackson", "12345", None, 5), 400)

#     def test_invalidSecurity(self):
#         self.assertEqual(ProcessPayment("4520 8505 0505 1234", "Dale Odd", datetime.date(2020, 5, 13), 1234, 5), 400)

#     def test_missingSecurity(self):
#         self.assertEqual(ProcessPayment("4520 8505 0505 1234", "Washington Cayote", datetime.date(2022, 5, 23), "", 15), 400)

#     def test_amountSmall(self):
#         self.assertEqual(ProcessPayment("4520 8505 0505 1234", "Mark Xi", datetime.date(2021, 5, 13), 367, 20.0), 200)

#     def test_amountMedium(self):
#         self.assertEqual(ProcessPayment("4520 8505 0505 1234", "Henry Cavill", datetime.date(2021, 5, 13), 456, 500.0), 200)

#     def test_amountLarge(self):
#         self.assertEqual(ProcessPayment("4520 8505 0505 1234", "Christian Bale", datetime.date(2021, 5, 13), 654, 501.01), 200)

#     def test_amountInvalid(self):
#         self.assertEqual(ProcessPayment("4520 8505 0505 1234", "Zoe Saldana", datetime.date(2021, 5, 13), 123, 999999.99), 200)

#     def test_amountInvalid(self):
#         self.assertEqual(ProcessPayment("4520 8505 0505 1234", "Jimmy johns", datetime.date(2022, 5, 13), None, ""), 400)

#     def test_amountInvalid2(self):
#         self.assertEqual(ProcessPayment("4520 8505 0505 1234", "John Doe", datetime.date(2022, 5, 13), None, -5), 400)

#     def test_amountInvalid3(self):
#         self.assertEqual(ProcessPayment("4520 8505 0505 1234", "Jane Dawson", datetime.date(2020, 5, 13), None, "a"), 400)

#     def test_Processed1(self):
#         self.assertEqual(ProcessPayment("4520 8505 0505 1234", "Andrew Jackson", datetime.date(2021, 5, 13), 123, 50.50), 200)

#     def test_Processed1(self):
#         self.assertEqual(ProcessPayment("5520 8505 0505 6331", "MasterCard Guy", datetime.date(2021, 5, 13), 123, 50.50), 200)
# # =======================================================================================

if __name__ == '__main__':
    app.run()