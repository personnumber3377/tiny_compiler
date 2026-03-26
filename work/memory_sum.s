mov $7, 0
mov $0, $7
mov $7, 4
mov $1, $7
mov $7, 1
mov $2, $7
mov $6, $0
mov $7, $2
sto $6, $7
mov $7, 2
mov $2, $7
mov $6, $0
add $7, $6, 1
mov $3, $7
mov $6, $3
mov $7, $2
sto $6, $7
mov $7, 3
mov $2, $7
mov $6, $0
add $7, $6, 2
mov $3, $7
mov $6, $3
mov $7, $2
sto $6, $7
mov $7, 4
mov $2, $7
mov $6, $0
add $7, $6, 3
mov $3, $7
mov $6, $3
mov $7, $2
sto $6, $7
mov $7, 0
mov $2, $7
mov $7, 0
mov $3, $7
@whilestart10:
mov $6, $3
mov $5, $1
cmp $6, $5
bae >whileend11
mov $6, $0
mov $5, $3
add $7, $6, $5
mov $4, $7
mov $6, $4
loa $7, $6
mov $6, $7
mov $7, 1000
sto $7, $6
mov $6, $2
mov $7, 1000
loa $5, $7
add $7, $6, $5
mov $2, $7
mov $6, $3
add $7, $6, 1
mov $3, $7
jmp >whilestart10
@whileend11:
hlt
