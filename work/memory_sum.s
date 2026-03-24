mov $0, 0
mov $1, 4
mov $2, 1
sto $0, $2
mov $2, 2
add $3, $0, 1
sto $3, $2
mov $2, 3
add $3, $0, 2
sto $3, $2
mov $2, 4
add $3, $0, 3
sto $3, $2
mov $2, 0
mov $3, 0
@whilestart5:
cmp $3, $1
bge >whileend6
add $4, $0, $3
loa $5, $4
add $2, $2, $5
add $3, $3, 1
jmp >whilestart5
@whileend6:
hlt
