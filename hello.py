# ask user for name 
# name = input("what's your name? ");

# name = input("What is ur name? ").strip().title();
# first , last = name.split(" ");
# print(f"hello {first}");

#remove white space from str
# name = name.strip();

#capitalize result first one
# name = name.capitalize();

#capitalize all first letters
# name = name.title();

#capitalize + str
# name = name.title().strip();

# print(name)

# combine all
# name = input("What is ur name? ").strip().title();

#split names
# first, last = name.split(" ");

#say hello to user 
# print(f"hello, {first}"); 

#defined def keyword to create functions  
# def hello(to = "world"):
#     print(f"hello {to}")
# hello()
# name = input("What is ur name ? ")
# hello(name)

# defined main()

def main():
    name = input("what is ur name? ")
    hello(name)


def hello(to = "world"):
    print(f"hello {to}");


main()