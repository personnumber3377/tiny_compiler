mov $0, 7
mov $1, 0
cmp $0, 5
bge >ifend3
mov $1, 1
@ifend3:
cmp $0, 5
ble >ifend4
mov $1, 2
@ifend4:
hlt
