


def main():
    
    words = get_words("words.txt")

    lowercase_words = [word.lower() for word in words ]
    counts = {word: words.count(word) for word in words}

    save_words(counts)
main()