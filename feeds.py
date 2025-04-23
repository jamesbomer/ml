import csv

#A script to deal with a particular excel sheet giving me info about feeds and clients
#one of the problems is that repeated fields are left blank, need to add these back in.
csvinput = open ('feeds-clients.csv')
reader = csv.DictReader(csvinput)
fieldnames=reader.fieldnames + ['Service', 'Name', 'Level', 'Ref', 'L1', 'MBL', 'MBO', 'Flavor']

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

    #My sheet has rows that show subtotals from sections above - remove these, I'll calculate them myself.
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
        #   e.g.: "QuantFEED Market Data - Cboe Europe BXE and CXE (1007:BAE) - Ref, L1, L2 MBL Depth10 - Real-Time"
        #   Service: QuantFEED Market Data
        #   Name: Cboe Europe BXE and CXE
        #   EID: (1007:BAE)
        #   Level: Ref, L1, L2 MBL Depth10
        #   Flavor: Real-Time
            dict['Name'] = details[1]
            dict['Level'] = details[2]

            #If there is only ref data, there is no separate flavor field.
            if dict['Level'] == 'Ref':
                None
            else:
                dict['Flavor'] = details[3]

            #now convert the 'level' field into a map of which levels are supported
            for level in dict['Level'].split(", "):
                if "Ref" in level:
                    dict['Ref'] = 'y'

                if "L1" in level:
                    dict['L1'] = 'y'
                
                if "MBO" in level:
                    dict['MBO'] = 'y'
            
                if "MBL" in level:
                    #extract the number of levels of MBL
                    dict['MBL'] = level.replace("L2 MBL Depth", "")
                

        writer.writerow(dict)

    lastrow = dict
    



        