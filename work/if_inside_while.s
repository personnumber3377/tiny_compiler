mov $7, 0
mov $0, $7
mov $7, 10
mov $1, $7
mov $7, 0
mov $2, $7
@whilestart0:
mov $6, $0
mov $5, $1
cmp $6, $5
bae >whileend1
mov $6, $0
cmp $6, 5
bae >else2
mov $6, $2
add $7, $6, 1
mov $2, $7
jmp >ifend3
@else2:
@ifend3:
mov $6, $0
add $7, $6, 1
mov $0, $7
jmp >whilestart0
@whileend1:
hlt
