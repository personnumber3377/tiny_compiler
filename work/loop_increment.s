mov $0, 0
mov $1, 10
@whilestart12:
cmp $0, $1
bae >whileend13
add $0, $0, 1
jmp >whilestart12
@whileend13:
hlt
