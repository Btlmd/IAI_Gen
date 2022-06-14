import os
reasonableMd = []

def get_list(target):
    dirs = os.listdir(target)
    file_list = []
    for file in dirs:
        if file.find("solution") != -1:
            file_list.append(f"{target}/{file}")
    return file_list

def changeToProblem(filename):
    return filename.replace("solution", "problem")

def filter_markdown(file_list):
    for file in file_list:
        with open(file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                # print(line)
                index1 = line.find("\\frac")
                index2 = line.find("sign")
                index3 = line.find("alpha_")
                if index1 != -1 and (index2 != -1 or index3 != -1):
                    line = line[index1:]
                    if line[8] == "{":
                        line = line[9:]
                    else:
                        pass
                    if line[0] >= "0" and line[0] <= "9":
                        if line[1] == "}":
                            try:
                                if int(line[0]) <= 5:
                                    reasonableMd.append(file)
                                else:
                                    if(reasonableMd.count(file) != 0):
                                        reasonableMd.remove(file)
                            except ValueError:
                                pass
                        else:
                            if(reasonableMd.count(file) != 0):
                                reasonableMd.remove(file)
                    else:
                        if(reasonableMd.count(file) != 0):
                            reasonableMd.remove(file)

if __name__ == "__main__":
    fileList = get_list(r"./doc/")
    numFile = len(fileList)
    filter_markdown(fileList)
    for md in fileList:
        if md not in reasonableMd:
            os.remove(md)
            os.remove(changeToProblem(md))
    print("精选优质题库: ", len(get_list(r"./doc/")), "/", numFile, "题，值得你拥有！")

