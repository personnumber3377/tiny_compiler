mov $0, 7
mov $1, 0
cmp $0, 5
bae >ifend3
mov $1, 1
@ifend3:
cmp $0, 5
bbe >ifend4
mov $1, 2
@ifend4:
hlt
