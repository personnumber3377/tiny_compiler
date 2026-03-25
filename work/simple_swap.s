mov $7, 0
mov $0, $7
mov $7, 5
mov $1, $7
mov $6, $0
mov $5, $1
sto $6, $5
mov $7, 3
mov $1, $7
mov $6, $0
add $7, $6, 1
mov $2, $7
mov $6, $2
mov $5, $1
sto $6, $5
mov $6, $0
loa $5, $6
mov $3, $5
mov $6, $2
loa $5, $6
mov $4, $5
mov $6, $3
mov $5, $4
cmp $6, $5
bbe >ifend0
mov $6, $0
mov $5, $4
sto $6, $5
mov $6, $2
mov $5, $3
sto $6, $5
@ifend0:
mov $6, $0
loa $5, $6
mov $7, 1000
sto $7, $5
mov $6, $2
loa $5, $6
mov $7, 1001
sto $7, $5
hlt
