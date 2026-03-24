mov $0, 2
mov $1, 8
mov $2, 3
mov $3, 9
mov $4, 5
mov $5, 3
mov $6, 7
mov $7, 2
@whilestart0:
cmp $0, $4
bge >whileend1
add $4, $0, 4
add $0, $0, 1
jmp >whilestart0
@whileend1:
mov $2, 11
cmp $1, $0
bge >ifend2
mov $0, 2
@ifend2:
@whilestart3:
cmp $0, $0
bge >whileend4
mov $3, 5
add $0, $0, 1
jmp >whilestart3
@whileend4:
add $3, $0, 2
add $0, $4, 5
cmp $3, $6
bge >ifend5
add $2, $0, 4
@ifend5:
cmp $1, $2
bge >ifend6
mov $5, 2
@ifend6:
add $5, $0, 0
@whilestart7:
cmp $5, $5
bge >whileend8
add $4, $1, 1
add $5, $5, 1
jmp >whilestart7
@whileend8:
add $2, $7, 2
@whilestart9:
cmp $1, $4
bge >whileend10
mov $0, 4
add $1, $1, 1
jmp >whilestart9
@whileend10:
hlt
