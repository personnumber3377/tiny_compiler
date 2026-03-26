mov $7, 0
mov $0, $7
mov $7, 10
mov $1, $7
@whilestart22:
mov $6, $0
mov $5, $1
cmp $6, $5
bae >whileend23
mov $6, $0
add $7, $6, 1
mov $0, $7
jmp >whilestart22
@whileend23:
hlt
