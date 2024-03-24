#myd = {'app4.py': [['app4.py', 'db.py', 2, 4.72], ['app4.py', 'db2.py', 1, 7.3]], 'db.py': [['db.py', 'db2.py', 2, 62.67]]}
myd = {'app3.py': [['app3.py', 'app4.py', 8, 88.89], ['app3.py', 'db.py', 2, 4.7], ['app3.py', 'db2.py', 2, 3.85]], 'app4.py': [['app4.py', 'db.py', 2, 4.72], ['app4.py', 'db2.py', 1, 7.3]], 'db.py': [['db.py', 'db2.py', 2, 62.67]]}
print(f'myd = {myd}')

# myd3={}
# c=0
# for key, value in myd.items():
#     # Add the original list
#     print(f'myd keys = {myd.keys()}')
    
#     if (c==0):
#         myd3[key] = value
#         c+=1
#     temp_list=None
#     # Iterate through the original list
#     for sublist in value:
#         # Create a new list with swapped elements
#         new_sublist = [sublist[1], sublist[0], sublist[2], sublist[3]]
#         # Append the new list to myd3 under the swapped key
#         if sublist[1] not in myd3.keys():
#             myd3[sublist[1]] = []
#             print("temp = ",myd3)
#         myd3[sublist[1]].append(new_sublist)
#         print("temp2 = ",myd3)
#         myd3[key].append(temp_list)
    
# print(f'myd3 = {myd3}')

# unique_dict = {}

# for key, sublists in myd3.items():
#     # Use a set to store unique sublists
#     unique_sublists = set()
#     for sublist in sublists:
#         # Convert the sublist to a tuple to make it hashable
#         sublist_tuple = tuple(sublist)
#         # Add the sublist tuple to the set
#         unique_sublists.add(sublist_tuple)
#     # Convert the set back to a list of lists
#     unique_dict[key] = [list(sublist) for sublist in unique_sublists]

# print('a = ',unique_dict)



myd3 = {}
for key, value in myd.items():
    if key in myd3:
        myd3[key].extend(value)
    else:    
        myd3[key] = value
    # Iterate through the original list
    for sublist in value:
        # Create a new list with swapped elements
        new_sublist = [sublist[1], sublist[0], sublist[2], sublist[3]]
        # Append the new list to myd3 under the swapped key
        if sublist[1] not in myd3.keys():
            myd3[sublist[1]] = []
        myd3[sublist[1]].append(new_sublist)

print(f'myd3 = {myd3}')