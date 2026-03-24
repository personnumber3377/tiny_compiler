mov $0, 0
mov $1, 5
mov $2, 0
@whilestart7:
cmp $2, $1
bge >whileend8
mov $3, 0
@whilestart9:
cmp $3, $2
bge >whileend10
add $0, $0, 1
add $3, $3, 1
jmp >whilestart9
@whileend10:
add $2, $2, 1
jmp >whilestart7
@whileend8:
hlt
