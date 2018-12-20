def from_file(filename):
    file = open(filename)
    f = open('/home/victor/Bureau/EGTS-master/data_files/lfpg_3Dflights.txt', 'x')
    for line in file:
        res =''
        words = line.strip().split()
        try:
            for i in range(len(words[8:])):
                words[i+8] += ',0'
        except Exception as error:
            print(error, line)
        for word in words:
            res += (word +' ')
        f.write(res + '\n')
    f.close()
    file.close()


from_file('/home/victor/Bureau/EGTS-master/data_files/lfpg_flights.txt')

def from_file1(filename):
    file = open(filename)
    f = open('/home/victor/Bureau/EGTS-master/data_files/lfpg_3Dmap.txt', 'x')
    for line in file:
        res =''
        words = line.strip().split()
        try:
            if words[0] == 'P':  # Point description
                words[3] +=",0"
            elif words[0] == 'L':  # Taxiway description
                for i in range(len(words[5:])):
                    words[i+5] += ",0"
            elif words[0] == 'R':  # Runway description
                l = len(words)
                words[l-2] += ",0"
                words[l-1] += ",0"
        except Exception as error:
            print(error, line)
        for word in words:
            res += (word +' ')
        f.write(res + '\n')
    f.close()
    file.close()


from_file1('/home/victor/Bureau/EGTS-master/data_files/lfpg_map.txt')
