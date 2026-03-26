mov $7, 0
mov $0, $7
mov $7, 5
mov $1, $7
@whilestart16:
mov $6, $0
mov $5, $1
cmp $6, $5
bae >whileend17
mov $6, $0
and $7, $6, 1
mov $3, $7
mov $6, $3
cmp $6, 0
beq >else18
mov $6, $2
add $7, $6, 1
mov $2, $7
jmp >ifend19
@else18:
mov $6, $2
add $7, $6, 2
mov $2, $7
@ifend19:
mov $6, $0
add $7, $6, 1
mov $0, $7
jmp >whilestart16
@whileend17:
hlt
