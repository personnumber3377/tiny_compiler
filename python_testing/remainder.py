
'''
        mov $0, 44570       # load values to registers $0, $1
        mov $1, 574
'''

x0 = 44570
x1 = 574

x3 = x1

# Scale up
while x3 < x0:
    print("x3 at start of loop: "+str(x3))
    x4 = x3 << 1
    print("x4 after shifting: "+str(x4))
    if x4 > x0:
        print("breaking since x0 == "+str(x0))
        break
    else:
        x3 = x4

# Division phase
print("x3 going into division phase: "+str(x3))
while x3 > 0:
    print("x0 in the comparison: "+str(x0))
    if x0 > x3:
        print("assigning "+str(x0 - x3)+" to x0")
        x0 = x0 - x3
    else:
        if x0 == x3:
            print("x0 == x3")
            x0 = 0
    print("x3 = x3 >> 1")
    x3 = x3 >> 1
print("final x0: "+str(x0))
x2 = x0

print(x2)
