mov $0, 0
mov $1, 10
mov $2, 0
@whilestart0:
cmp $0, $1
bae >whileend1
cmp $0, 5
bae >ifend2
add $2, $2, 1
@ifend2:
add $0, $0, 1
jmp >whilestart0
@whileend1:
hlt
