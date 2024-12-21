text = "[][[]]"

max_length = 0
cur_length = 0
stack = []
open_bracket = True
for ch in text:
    if ch == '[' and open_bracket:
        stack.append(ch)

    elif ch == ']':
        prev_ch = stack.pop()
        if prev_ch == '[':
            cur_length += 2
            max_length = max(max_length, cur_length)
        open_bracket = False

print(max_length)
        
    