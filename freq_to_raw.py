string = ""
with open("_word_frequency") as f:
    for line in iter(f.readline, ''):
        word = line.split(': ')
        if len(word) == 2:
            if '\n' in word[1]:
                word[1] = word[1][:word[1].find('\n')]
            if int(word[1]) >= 5:
                string += (word[0] + " ") * int(word[1])

with open('_output', mode='x') as f:
    f.write(string)
print('done')
