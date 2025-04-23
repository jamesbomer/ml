import csv
import re

#A script to deal with a particular excel sheet giving me info about feeds and clients
#one of the problems is that repeated fields are left blank, need to add these back in.
csvinput = open ('feeds-clients.csv')
reader = csv.DictReader(csvinput)
#fieldnames=reader.fieldnames + ['Service', 'Name', 'EID', 'Level', 'Ref', 'L1', 'MBL', 'MBO', 'Flavor']
fieldnames=reader.fieldnames + ['Service', 'Name', 'EID', 'Level', 'Depth', 'Flavor']

csvoutput = open('feeds-clients-modified.csv', "w")
writer = csv.DictWriter(csvoutput, fieldnames)
writer.writeheader()

lastrow = None

#from the second row on, carry any previous values forward in place of blank fields
for row in reader:
    dict = {}
    
    #if a field in the new row has no value, repeat the value of the previous row, if there is a previous row.
    if (lastrow):
        for j in reader.fieldnames:
            if row[j]:
                dict[j] = row[j]
            else:
                dict[j] = lastrow[j]
    else:
        dict = row

    #My sheet has rows that show subtotals from sections above - remove these, I'll calculate them myself if I want them.
    if ("Total" in dict['Product']) or ("Total" in dict['Datacenter']):
        #print('skipping: ', end=None)
        #print(dict)
        None
    else:
        #My sheet has a combination of useful info in the 'Project Product' field.  Split this into sub-fields.
        details = dict['Project Product'].split(" - ")
        print(details)
        dict['Service'] = details[0]

        #Various possibilities for how to interpret this:
        #   e.g. ConsolidatedFEED Business Model - Per Feed
        if ("ConsolidatedFEED Business Model" in dict['Service']):
            dict['Name'] = details[1]
        
        else:
        #   e.g.: QuantFEED Market Data - Vienna Cash Market & Structured Products RapidADH - CERT (1121:VIR) - Ref, L1 - Real-Time
        #   e.g.: "QuantFEED Market Data - Cboe Europe BXE and CXE (1007:BAE) - Ref, L1, L2 MBL Depth10 - Real-Time"
        #   Need to separate out:
        #   Service: QuantFEED Market Data
        #   Name: Cboe Europe BXE and CXE
        #   CERT: y/n
        #   EID: (1007:BAE)
        #   Level: Ref, L1, L2 MBL Depth10
        #   Flavor: Real-Time

            dict['Name'] = details[1]
            
            #easiest to use regex to extract the EID
            EID = re.search(r"\(.*?\)", details[1])
            if (EID):
                dict['EID'] = EID.group(0)
            else:
                dict['EID'] = "NOMATCH"

            level = details[2]
            
            #If there is only ref data, there is no separate flavor field
            if level != 'Ref':
                dict['Flavor'] = details[3]

            #now unroll (canonicalise) the 'level' field, writing a separate line for each level.
            written = False
            for lvl in level.split(", "):
                if "Ref" in lvl:
                    dict['Level'] = 'Ref'
                    writer.writerow(dict)
                    written = True

                if "L1" in lvl:
                    dict['Level'] = 'L1'
                    writer.writerow(dict)
                    written = True
                
                if "MBO" in lvl:
                    dict['Level'] = 'MBO'
                    writer.writerow(dict)
                    written = True
            
                if "MBL" in lvl:
                    dict['Level'] = 'MBL'
                    #extract the number of levels of MBL
                    dict['Depth'] = lvl.replace("L2 MBL Depth", "")
                    writer.writerow(dict)
                    written = True

        if not (written):
            dict['Level'] = 'NOLEVEL'
            writer.writerow(dict)

    #remember this as the last row so that undefined values can be carried forward.
    lastrow = dict
    



        