from paypal_client import create_order

oid, link = create_order(5, "Test logo design")
print("Order:", oid)
print("Approve link:", link)
