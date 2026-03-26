x0 = 44570
x1 = 574

x3 = x1

# Scale up
while x3 < x0:
    x4 = x3 << 1
    if x4 > x0:
        break
    else:
        x3 = x4

# Division phase (CORRECT)
while x3 > x1:
    if x0 > x3:
        x0 = x0 - x3
    else:
        if x0 == x3:
            x0 = 0
    x3 = x3 >> 1

# FINAL STEP (this was missing!)
if x0 > x1:
    x0 = x0 - x1
else:
    if x0 == x1:
        x0 = 0

x2 = x0

print("x2: "+str(x2))
