# Scratchwork to make sure individual bits of code work the way I think it will
d = {'a': 5, 'b': 7}
e = d.copy()

print(str(d) + 'c')
print(e)

e['b'] -= 1

print(d)
print(e)