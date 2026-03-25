mov $7, 0
mov $0, $7
mov $7, 5
mov $1, $7
mov $7, 0
mov $2, $7
@whilestart7:
mov $6, $2
mov $5, $1
cmp $6, $5
bae >whileend8
mov $7, 0
mov $3, $7
@whilestart9:
mov $6, $3
mov $5, $2
cmp $6, $5
bae >whileend10
mov $6, $0
add $7, $6, 1
mov $0, $7
mov $6, $3
add $7, $6, 1
mov $3, $7
jmp >whilestart9
@whileend10:
mov $6, $2
add $7, $6, 1
mov $2, $7
jmp >whilestart7
@whileend8:
hlt
