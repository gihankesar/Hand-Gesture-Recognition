import re

# text = "Enter text: I have 3 apples and 25 oranges"

# print(re.findall(r"(\d+)", text))

# text = "Hello WORLD Python"

# new = re.findall(r"[A-Z]", text)
# print(new)

# text = "My phone is 0771234567"

# new = re.sub(r"[0-9]","#",text)

# text = "12 5 123 9999 42"

# new = re.findall(r"\b\d{2,3}\b", text)

# text = "Kesara is Studying Python With Regex"

# new = re.findall(r"([A-Z][a-z]+)", text)


# text = "0721231231"

# new = re.fullmatch(r"\b0\d{9}\b", text)

# text = "kesara@gmail"

# new = re.fullmatch(r"\b([a-z]|[0-9])+@[a-z]+.com\b", text)

# text = "Mr. Smith met Mrs. Jones and Mr. Brown."


# new = re.findall(r"((?:Mr\.|Mrs\.)\s[A-Z]+[a-z]+)", text)

text = "My numbers are 123-456-7890 and 077-123-4567."

new = re.findall(r"(\b(?:\d-?){10}\b)", text)

print(new)