import sys

# if len(sys.argv) < 2:
#     sys.exit("too few")
# elif len(sys.argv) > 2:
#     sys.exit("too many")

# print("hello, my name is", sys.argv[1])

if len(sys.argv) < 2:
    sys.exit("too few")

for arg in sys.argv[1:-1]:
    print("hello, my name is", arg)
          