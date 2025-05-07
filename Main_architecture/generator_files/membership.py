import csv

headers=[
    "name",
    "L1_Board",
    "L2_Board",
    "L3_Board",
]

board_data = [
    ["Alice", "CDF","DIS","Transaction Processing"],
    ["Bob", "CDF","DIS","Transaction Processing"],
    ["Rishika", "CDF","DIS","Transaction Processing"],
    ["Hari", "CDF","DIS","Transaction Processing"],
    ["Apoorva", "CDF","DIS","Transaction Processing"],
    ["Apoorva", "EBSNF","DIS","Transaction Processing"],
    ["David", "EBSNF","DIS","Transaction Processing"],
    ["Pavithra", "EBSNF","DIS","Transaction Processing"],
    ["Alok", "EBSNF","DIS","Transaction Processing"],
    ["Peter", "EBSNF","DIS","Transaction Processing"],
    ["Sai","TES1","TES","Transaction Processing"],
    ["Krithika","TES1","TES","Transaction Processing"],
    ["David","TES1","TES","Transaction Processing"],
    ["Seetha","TES2","TES","Transaction Processing"],
    ["Rasheed","TES2","TES","Transaction Processing"],
    ["Rachin","TES2","TES","Transaction Processing"],
    ["Nitish","APS1","APS","Transaction Processing"],
    ["Noor","APS1","APS","Transaction Processing"],
    ["Khaleel","APS1","APS","Transaction Processing"],
    ["Vikram","APS2","APS","Transaction Processing"],
    ["Dube","APS2","APS","Transaction Processing"],
    ["Ashwin","APS2","APS","Transaction Processing"],

]


with open("generated_files/members.csv",mode="w") as file:
    writer=csv.writer(file)
    writer.writerow(headers)
    writer.writerows(board_data)


    