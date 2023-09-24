from operators import Operator


def extract_words(path):
    file = open(path)
    labels = []
    dashCount = []
    while True:
        line = file.readline()
        if not line:
            break
        if line[0] != '-':
            continue
        numDash = 0
        for char in line:
            if char != '-':
                break
            numDash += 1
        line = line.strip('-')
        words = line.split()

        if words[0] == 'FUNCTION':
            labels.append(words[1])
            dashCount.append(numDash)
        else:
            labels.append(words[0])
            dashCount.append(numDash)

    return labels, dashCount



def adapt_node_label(labels, dashCount):
    while True:
        if labels[0] == "MAIN":
            break
        labels.pop(0);
        dashCount.pop(0);
    for label in labels:
        if ".builtinNS::" in label:
            index = labels.index(label)
            label = "func: " + label[12:]
            labels[index] = label
    n= 1
    for i in range(len(labels)):
        if 'MAIN' in labels[i] or 'func' in labels[i] or 'CP' in labels[i] or 'SPARK' in labels[i]:
            continue
        num = str(n)
        labels[i] = labels[i] + " " +num
        n +=1


def extract_tree_labels(words, dashCount):
    labels = []
    dashCountTree = []
    for i in range(len(words)):
        if 'CP' in words[i] or 'SPARK' in words[i]:
            continue
        labels.append(words[i])
        dashCountTree.append(dashCount[i])
    return labels, dashCountTree



def add_tree_nodes(labels, dashCount):

    names = []
    parents = []
    dashCountMain = dashCount[0]
    index = 1

    while index < len(labels):
        if dashCount[index] < dashCountMain:
            break
        index += 1
    names.append('MAIN')
    parents.append('')

    for i in range(1, index):
        names.append(labels[i])
        numDash = dashCount[i]
        x = i-1
        while x >= 0:
            if numDash - dashCount[x] == 2:
                parents.append(labels[x])
                break
            x -= 1

    for i in range(index,len(labels)):
        if 'MAIN' in labels[i] or 'func' in labels[i]:
            continue
        names.append(labels[i])
        numDash = dashCount[i]
        x= i-1
        while x >= index:
            if numDash - dashCount[x] == 2:
                parents.append((labels[x]))
                break
            x -= 1
    return names, parents


def sankey_index(words, dashCount, treeNode):
    i = words.index(treeNode)
    startIndex = i+1

    parentDash = dashCount[i]
    childDash = parentDash + 2
    index = startIndex
    while dashCount[index] == childDash:
        if index == len(words)-1:
            break
        index += 1

    endingIndex = index-1
    return startIndex, endingIndex

def extract_sankey_lines(path, startIndex, endingIndex):
    file = open(path)
    lines = []
    sankeylines = []
    while True:
        line = file.readline()
        if not line:
            break
        if line[0] != '-':
            continue
        line = line.strip('-')
        line = line.split()
        lines.append(line)
    while True:
        line = lines[0]
        if line[0] == "MAIN":
            break
        lines.pop(0)
    for i in  range(startIndex, endingIndex+1):
        sankeylines.append(lines[i])

    length = len(sankeylines)
    x=0
    for i in range(length):
        if x > length:
            break
        line = sankeylines[x]
        if line[1] == 'createvar' or line[1] == 'rmvar':
            sankeylines.pop(x)
        else:
            x += 1

    return sankeylines

def sankey_versions(lines):
    cp = []
    spark = []
    for line in lines:
        if line[0] == "CP":
            cp.append(line)
        else:
            spark.append(line)
    return cp, spark




def tree_to_sankey(names, parents):
    labels = []
    source = []
    target = []
    value = []
    for name in names:
        labels.append(name)
    for i in range(len(labels)):
        if labels[i] == 'MAIN':
            continue
        parent = parents[i]
        indexParent = labels.index(parent)
        source.append(indexParent)
        target.append(i)
        value.append(1)
    return labels, source,target,value

def group_operators(name):
    group1 = ['>', '<', '>=', '<=', '==', '!=', '+', '-', '^2', '/', '*', 'cpmm', '&&', 'max', 'mapmm', 'log', 'xor']
    group2 = ['seq']
    group3 = ['rand']
    group4 = ['rightIndex','ctable', 'ctableexpand']
    group5 = ['uppertri', 'replace', 'ifelse', 'append']
    group6 = ['leftIndex']
    if name in group1:
        return 1
    elif name in group2:
        return 2
    elif name in group3:
        return 3
    elif name in group4:
        return 4
    elif name in group5:
        return 5
    elif name in group6:
        return 6
    else:
        return 7

def get_input_output(number, line):
    if number == 1:
        return [line[2], line[3]] , line[4]
    if number == 2:
        return [line[5], line[6], line[7]], line[8]
    if number == 3:
        return  [line[2], line[3]], line[len(line)-1]
    if number == 4:
        return  [line[2], line[3], line[4], line[5], line[6]], line[7]
    if number == 5:
        return [line[2], line[3], line[4]], line[5]
    if number == 6:
        return [line[2], line[3], line[4], line[5], line[6], line[7]], line[8]
    else:
        return [line[2]], line[3]





def create_operations(lines):
    operators = []
    for line in  lines:
        name = line[1]
        number = group_operators(name)
        inputs, output = get_input_output(number, line)
        operator = Operator(name, inputs, output)
        operators.append(operator)
    return operators


def create_sankey_nodes(operators):
    labels = []
    source = []
    target = []
    value = []
    for operator in operators:
        labels.append(operator.get_name())

    for x in range(len(operators)-1):
        operator1 = operators[x]
        output1 = operator1.get_output()
        name1 = operator1.get_name()
        for y in range(x+1, len(operators)):
            operator2 = operators[y]
            input2 = operator2.get_input()
            name2 = operator2.get_name()
            for input in input2:
                if output1 in input or input in output1:
                    source.append(x)
                    target.append(y)
                    value.append(1)
    if len(source) == 0:
        source.append(0)
        target.append(1)
        value.append(1)
    return labels, source, target, value














