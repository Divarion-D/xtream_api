import xmltv

# If you need to change the locale:
xmltv.locale = "Latin-1"

# If you need to change the date format used in the XMLTV file:
xmltv.date_format = "%Y%m%d%H%M%S %Z"

filename = "epg.xml"

# Print info for XMLTV file (source, etc.)
# print(xmltv.read_data(open(filename, 'r')))

# Print channels
# print(xmltv.read_channels(open(filename, 'r')))
# write channels to file
with open("channels.txt", "w") as f:
    f.write(str(xmltv.read_channels(open(filename, "r"))))

# Print programmes
# print(xmltv.read_programmes(open(filename, 'r')))
