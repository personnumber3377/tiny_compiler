mov $7, 0
mov $0, $7
mov $7, 10
mov $1, $7
@whilestart12:
cmp $0, $1
bae >whileend13
mov $6, $0
add $7, $6, 1
mov $0, $7
jmp >whilestart12
@whileend13:
hlt
