mov $0, 0
mov $1, 10
@whilestart1:
cmp $0, $1
bge >whileend2
add $0, $0, 1
jmp >whilestart1
@whileend2:
hlt
