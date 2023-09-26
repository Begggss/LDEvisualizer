from operations import Operation


def adapt_words(words, dashCount):
    while True:
        if words[0] == "MAIN":
            break
        words.pop(0);
        dashCount.pop(0);
    for label in words:
        if label[0] == '.':
            index = words.index(label)
            label = "func: " + label.split(':')[2]
            words[index] = label
    n = 1
    for i in range(len(words)):
        if 'MAIN' in words[i] or 'func' in words[i] or 'CP' in words[i] or 'SPARK' in words[i]:
            continue
        num = str(n)
        words[i] = words[i] + " " + num
        n += 1


def extract_words(path):
    file = open(path)
    words = []
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
        word = line.split()
        if word[0] == 'FUNCTION':
            words.append(word[1])
            dashCount.append(numDash)
        else:
            words.append(word[0])
            dashCount.append(numDash)
    adapt_words(words, dashCount)
    return words, dashCount


def extract_tree_labels(words, dashCount):
    labels = []
    dashCountTree = []
    for i in range(len(words)):
        if 'CP' in words[i] or 'SPARK' in words[i]:
            continue
        labels.append(words[i])
        dashCountTree.append(dashCount[i])
    return labels, dashCountTree


def add_tree_nodes(path):
    words, dashCount = extract_words(path)
    labels, dashCountTree = extract_tree_labels(words, dashCount)

    names = []
    parents = []
    dashCountMain = dashCountTree[0]
    index = 1

    while index < len(labels):
        if dashCountTree[index] < dashCountMain:
            break
        index += 1
    names.append('MAIN')
    parents.append('')

    for i in range(1, index):
        names.append(labels[i])
        numDash = dashCountTree[i]
        x = i - 1
        while x >= 0:
            if numDash - dashCountTree[x] == 2:
                parents.append(labels[x])
                break
            x -= 1

    for i in range(index, len(labels)):
        if 'MAIN' in labels[i] or 'func' in labels[i]:
            continue
        names.append(labels[i])
        numDash = dashCountTree[i]
        x = i - 1
        while x >= index:
            if numDash - dashCountTree[x] == 2:
                parents.append((labels[x]))
                break
            x -= 1
    return names, parents


def tree_to_sankey(path):
    names, parents = add_tree_nodes(path)
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
    return labels, source, target, value







def sankey_index(path, treeNode):
    words, dashCount = extract_words(path)
    i = words.index(treeNode)
    startIndex = i + 1

    parentDash = dashCount[i]
    childDash = parentDash + 2
    index = startIndex
    while dashCount[index] == childDash:
        if index == len(words) - 1:
            break
        index += 1

    endingIndex = index - 1
    return startIndex, endingIndex

def extract_operators(path, treeNode):
    startIndex, endingIndex = sankey_index(path, treeNode)
    file = open(path)
    lines = []
    operations = []
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
    for i in range(startIndex, endingIndex + 1):
        operations.append(lines[i])
    length = len(operations)
    x = 0
    for i in range(length):
        if x > length:
            break
        line = operations[x]
        if line[1] == 'createvar' or line[1] == 'rmvar':
            operations.pop(x)
        else:
            x += 1
    return operations

def group_operators(name):
    group1 = ['>', '<', '>=', '<=', '==', '!=', '-', '^2', '/', '*', 'cpmm', '&&', 'max', 'mapmm', 'xor', 'ba+*']
    group2 = ['seq']
    group3 = ['rand']
    group4 = ['rightIndex', 'ctable', 'ctableexpand', 'groupedagg']
    group5 = ['uppertri', 'replace', 'ifelse', 'append']
    group6 = ['leftIndex']
    group7 = ['+', 'log']
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
    elif name in group7:
        return 7
    else:
        return 8

def get_input_output(number, line):
    if number == 1:
        return [line[2], line[3]], line[4]
    if number == 2:
        return [line[5], line[6], line[7]], line[8]
    if number == 3:
        return [line[2], line[3]], line[len(line) - 1]
    if number == 4:
        return [line[2], line[3], line[4], line[5], line[6]], line[7]
    if number == 5:
        return [line[2], line[3], line[4]], line[5]
    if number == 6:
        return [line[2], line[3], line[4], line[5], line[6], line[7]], line[8]
    if number == 7:
        inputs = []
        for i in range(len(line)):
            if 'SCALAR' in line[i] or 'MATRIX' in line[i]:
                inputs.append(line[i])
        output = inputs.pop(len(inputs) - 1)
        return inputs, output
    else:
        return [line[2]], line[3]


def create_operations(path, treeNode):
    operators = extract_operators(path, treeNode)
    operations = []
    for operator in operators:
        name = operator[1]
        number = group_operators(name)
        inputs, output = get_input_output(number, operator)
        operator = Operation(name, inputs, output)
        operations.append(operator)
    return operations


# extract the variable name only from the string
def extract_inputs(operator):
    inputs = operator.get_input()
    for i in range(len(inputs)):
        if 'SCALAR' or 'MATRIX' in inputs[i]:
            inputs[i] = inputs[i].split('.')[0]
        if 'target' in inputs[i]:
            inputs[i] = inputs[i].split('=')[1]
    return inputs


def extract_output(operator):
    output = operator.get_output()
    if 'SCALAR' or 'MATRIX' in output:
        output = output.split('.')[0]
    return output

def remove_node(index, source, target):
    i = len(source)
    x = 0
    while x < len(target):
        a = source[x]
        if target[x] == index:
            sourceIndex = source.pop(x)
            target.pop(x)
            x -= 1
            for y in range(len(source)):
                b = target[y]
                if source[y] == index:
                    source[y] = sourceIndex
        x = x+1


def remove_label(label,source, target, labels):
    for index in range(len(labels)):
        if label == labels[index]:
            remove_node(index, source, target)

def add_flows(indexes, operations, source, target):
    for x in range(len(operations) - 1):
        operation1 = operations[x]
        name1 = operation1.get_name()
        output1 = extract_output(operation1)
        for y in range(x + 1, len(operations)):
            operation2 = operations[y]
            name2 = operation2.get_name()
            input2 = extract_inputs(operation2)
            for input in input2:
                if output1 == input:
                    source.append(indexes[x])
                    target.append(indexes[y])

def add_inputs_outputs(operation,labels,source, target, IndexOperation):
    inputs = extract_inputs(operation)
    out = extract_output(operation)
    x=1
    if '_Var' not in out and '_mVar' not in out:
        labels.append('var: '+ out)
        source.append(IndexOperation)
        target.append(IndexOperation + x)
        x += 1
    for i in inputs:
        if '_Var' in i or '_mVar' in i:
            continue
        labels.append('var: ' + i)
        source.append(IndexOperation + x)
        target.append(IndexOperation)
        x += 1





def create_sankey_nodes(path, treeNode):
    operations = create_operations(path,treeNode)
    labels = []
    source = []
    target = []
    value = []
    indexes = []
    for operation in operations:

        if operation.get_name() == "cpvar" or operation.get_name() == 'mvvar' or operation.get_name() == 'assignvar':
            if 'SCALAR' in operation.get_output():
                labels.append('var: ' + operation.get_output().split('.')[0])
                indexOperation = len(labels) - 1
                indexes.append(indexOperation)
            else:
                labels.append('var: ' + operation.get_output())
                indexOperation = len(labels) - 1
                indexes.append(indexOperation)
        else:
            labels.append(operation.get_name())
            indexOperation = len(labels) - 1
            indexes.append(indexOperation)
            add_inputs_outputs(operation, labels, source, target, indexOperation)

    add_flows(indexes, operations, source, target)
    remove_label('castdts', source, target,labels)
    remove_label('castvti', source, target, label)
    for i in source:
        value.append(1)

    return labels, source, target, value



