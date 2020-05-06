l = [['Proudly Australian, we have grown from humble beginnings to become the nation’s outright leader in transport fuels, supplying one third of all Australia’s transport fuel needs.'], ['Proudly Australian, we have grown from humble beginnings to become the nation’s outright leader in transport fuels, supplying one third of all Australia’s transport fuel needs.'], []]
print(l)
non_dup = []
for i in l:
    if i not in non_dup:
        non_dup.append(i)

print(non_dup)