import sqlite3
import json

json_file = open("champions.json",'r',encoding="utf-8")
file_contents = json_file.read()
champ_data = json.loads(file_contents)
json_file.close()

print(type(champ_data))
print(champ_data[1])

conn = sqlite3.connect("championData.sqlite")
cur = conn.cursor()

drop_championID = '''
    DROP TABLE IF EXISTS "championData";
'''

create_championID = '''
    CREATE TABLE IF NOT EXISTS "championData" (
        "Id"       INTEGER NOT NULL,
        "Title"  TEXT NOT NULL,
        "Tag1" TEXT NOT NULL,
        "Tag2" TEXT NOT NULL,
        "Hp" INTEGER NOT NULL,
        "Mp" INTEGER NOT NULL,
        "MoveSpeed" INTEGER NOT NULL,
        "Armor" INTEGER NOT NULL,
        "AttackRange" INTEGER NOT NULL,
        "AttackDamage" INTEGER NOT NULL,
        "AttackSpeed" INTEGER NOT NULL        

    );
'''

insert_championID = '''
    INSERT INTO championData
    VALUES (?,?,?,?,?,?,?,?,?,?,?)
'''

cur.execute(drop_championID)
cur.execute(create_championID)

for champ in champ_data:
    temp = [int(champ["key"]),champ["title"]]
    temp.append(champ["tags"][0])
    if len(champ["tags"]) == 1:
        temp.append('No tag')
    else:
        temp.append(champ["tags"][1])
    
    temp.append(champ["stats"]["hp"])
    temp.append(champ["stats"]["mp"])
    temp.append(champ["stats"]["movespeed"])
    temp.append(champ["stats"]["armor"])
    temp.append(champ["stats"]["attackrange"])
    temp.append(champ["stats"]["attackdamage"])
    temp.append(champ["stats"]["attackspeed"])
    
    cur.execute(insert_championID,temp)

conn.commit()
