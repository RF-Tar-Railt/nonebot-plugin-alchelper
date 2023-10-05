def cals(data: list):
    table = {}
    for i, r in enumerate(data):
        if r not in table:
            table[r] = 0
        table[r] += ( i) / len(data)

    return sorted(table.items(), key=lambda x: x[1], reverse=False)

print(cals(["a", "b", "a", "a"]))