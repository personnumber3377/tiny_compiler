mov $0, 0
mov $1, 5
sto $0, $1
mov $1, 3
add $2, $0, 1
sto $2, $1
loa $3, $0
loa $4, $2
cmp $3, $4
bbe >ifend16
sto $0, $4
sto $2, $3
@ifend16:
loa $5, $0
loa $6, $2
hlt
