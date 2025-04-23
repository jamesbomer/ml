import csv
import re

#A script to deal with a particular excel sheet giving me info about feeds and clients
#one of the problems is that repeated fields are left blank, need to add these back in.
csvinput = open ('feeds-clients.csv')
reader = csv.DictReader(csvinput)
#fieldnames=reader.fieldnames + ['Service', 'Name', 'EID', 'Level', 'Ref', 'L1', 'MBL', 'MBO', 'Flavor']
fieldnames=reader.fieldnames + ['Service', 'Name', 'EID', 'CERT', 'Level', 'Depth', 'Flavor']

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
        #My sheet has a combination of useful info in the 'Project Product' field, with cases that need to be handled differently. Some examples:
        #   ConsolidatedFEED Business Model - Per Feed
        #   QuantFEED Market Data - Cboe Europe BXE and CXE (1007:BAE) - Ref, L1, L2 MBL Depth10 - Real-Time # this is the most common form
        #   QuantFEED Market Data - Vienna Cash Market & Structured Products RapidADH - CERT (1121:VIR) - Ref, L1 - Real-Time # additional "- CERT"
        #   QuantFEED Market Data - ICE Futures US - US Softs & Financials (1042:ICU) - Ref, L1, L2 MBL Depth5 - Real-Time # addtional "- US Softs & Financials"
        #   QuantFEED Market Data - Citadel SI - EU stocks (1386:CIA) - Ref, L1 - Real-Time # additional "- EU Stocks"
        #   ConsolidatedFEED Market Data - OPRA NBBO - 5s conflation - Managed Solution (1081:OPA) - Ref, L1 - Real-Time #additional "- 5s conflation - Managed Solution"
        #   QuantFEED Market Data - Boerse Frankfurt Certificates and Warrants (ex SCOACH) - CERT (1118:XEA) - Ref, L1 - Real-Time # extra "(ex SCOACH)"
        #   QuantFEED Market Data - XTX Markets SI (below SMS) EU Stocks - CERT (1385:XTC) - Ref, L1 - Real-Time # extra "(below SMS)"
        #   QuantFEED Market Data - LSE European Market, LSE International Market (1054:LEE,1055:LEI) - Ref, L1 - Real-Time # two EIDS!!

        details = dict['Project Product'].split(" - ")
        if ("ConsolidatedFEED Business Model" in details[0]):
            dict['Service'] = details[0] + details[1]
            #done, move on to next row.
        else:
            #   Want to separate out:
            #   Service: e.g. QuantFEED Market Data
            #   Name: e.g. Cboe Europe BXE and CXE
            #   CERT: y/n
            #   EID: e.g. (1007:BAE)
            #   Level: e.g. Ref, L1, L2 MBL Depth10
            #   Flavor: e.g. Real-Time

            dict['Service'] = details[0]
            details.pop(0)

            #if we ecountered " - CERT" or " - US" (an extra minus sign) then we need to interpret this.
            #easiest to look for the EID as its format is quite distinctive.  Keep eating additional minus signs and combining fields unti we get there.
            pattern = r"[0-9]+:[A-Z]+"
            name = ""
            cert = ""

            while (len(details) > 0):
                if (name == ""):
                    name = details[0]
                else:
                    name += " " + details[0]

                #strictly, not expecting CERT before the first "-" but whatever
                if "CERT" in details[0]:
                    cert = 'y'

                #look for the EID (or a comma separated list of EIDs)
                eids = re.findall(pattern, details[0])
                details.pop(0)

                if (eids):
                    #found the EIDs
                    break;

            if (len(eids) == 0):
                raise Exception("Format error, no EID found")        

            level = details[0]
            details.pop(0)
            
            #If there is only ref data, there is no separate flavor field
            if level != 'Ref':
                flavor = details[0]
                details.pop(0)

            #canonicalise in the case of multiple EIDs - one set of rows per EID
            for eid in eids:
                dict['Name'] = name
                dict['CERT'] = cert
                dict['EID'] = eid
                dict['Flavor'] = flavor

                #now canonicalise the 'level' field, writing a separate line for each level.
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
    



        