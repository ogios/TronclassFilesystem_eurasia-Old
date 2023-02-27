import base64

string = "123456"
a = base64.b64encode(string.encode()).decode()
print(a)
b = base64.b64decode(a.encode()).decode()
print(b)