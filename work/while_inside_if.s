mov $7, 0
mov $0, $7
mov $7, 5
mov $1, $7
mov $7, 0
mov $2, $7
mov $6, $1
cmp $6, 0
bbe >else36
@whilestart38:
mov $6, $0
mov $5, $1
cmp $6, $5
bae >whileend39
mov $6, $2
add $7, $6, 2
mov $2, $7
mov $6, $0
add $7, $6, 1
mov $0, $7
jmp >whilestart38
@whileend39:
jmp >ifend37
@else36:
@ifend37:
hlt
