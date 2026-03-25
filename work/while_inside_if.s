mov $0, 0
mov $1, 5
mov $2, 0
cmp $1, 0
bbe >ifend17
@whilestart18:
cmp $0, $1
bae >whileend19
add $2, $2, 2
add $0, $0, 1
jmp >whilestart18
@whileend19:
@ifend17:
hlt
