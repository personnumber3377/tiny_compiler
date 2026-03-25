mov $7, 0
mov $0, $7
mov $7, 5
mov $1, $7
mov $7, 0
mov $2, $7
mov $6, $1
cmp $6, 0
bbe >ifend17
@whilestart18:
mov $6, $0
mov $5, $1
cmp $6, $5
bae >whileend19
mov $6, $2
add $7, $6, 2
mov $2, $7
mov $6, $0
add $7, $6, 1
mov $0, $7
jmp >whilestart18
@whileend19:
@ifend17:
hlt
