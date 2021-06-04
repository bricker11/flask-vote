from math import log
import operator
import matplotlib.pyplot as plt
import pandas as pd
import os

plt.rcParams['font.sans-serif']=['SimHei'] #显示中文标签
plt.rcParams['axes.unicode_minus']=False   #这两行需要手动设置

def readcsv(df):
    return pd.read_csv(df,error_bad_lines=False)

# 删除缺失值
def all_delete_empty(df):
    return df.dropna()

# 计算信息熵
def calcShannonEnt(dataSet):
    numEntries = len(dataSet)  # 样本数
    labelCounts = {}
    for featVec in dataSet:  # 遍历每个样本
        currentLabel = featVec[-1]  # 当前样本的类别# 每行数据的最后一个字（类别）
        if currentLabel not in labelCounts.keys():  # 生成类别字典
            labelCounts[currentLabel] = 0
        labelCounts[currentLabel] += 1# 统计有多少个类以及每个类的数量
    shannonEnt = 0.0
    for key in labelCounts:  # 计算信息熵
        prob = float(labelCounts[key]) / numEntries# 计算单个类的熵值
        shannonEnt = shannonEnt - prob * log(prob, 2)# 累加每个类的熵值
    return shannonEnt

# 划分数据集，axis:按第几个属性划分，value:要返回的子集对应的属性值
def splitDataSet(dataSet,axis,value): # 按某个特征分类后的数据
    retDataSet=[]
    for featVec in dataSet:
        if featVec[axis]==value:
            reducedFeatVec =featVec[:axis]
            reducedFeatVec.extend(featVec[axis+1:])
            retDataSet.append(reducedFeatVec)
    return retDataSet

# 选择最好的数据集划分方式
def chooseBestFeatureToSplit(dataSet):
    numFeatures = len(dataSet[0]) - 1  # 属性的个数
    baseEntropy = calcShannonEnt(dataSet)# 原始的熵
    bestInfoGain = 0.0
    bestFeature = -1
    for i in range(numFeatures):  # 对每个属性技术信息增益
        featList = [example[i] for example in dataSet]
        uniqueVals = set(featList)  # 该属性的取值集合
        newEntropy = 0.0
        for value in uniqueVals:  # 对每一种取值计算信息增益
            subDataSet = splitDataSet(dataSet, i, value)
            prob = len(subDataSet) / float(len(dataSet))
            newEntropy += prob * calcShannonEnt(subDataSet)# 按特征分类后的熵
        infoGain = baseEntropy - newEntropy# 原始熵与按特征分类后的熵的差值
        if (infoGain > bestInfoGain):  # 若按某特征划分后，熵值减少的最大，则次特征为最优分类特征
            bestInfoGain = infoGain
            bestFeature = i
    return bestFeature

def majorityCnt(classList):    #按分类后类别数量排序，比如：最后分类为2男1女，则判定为男；
    classCount={}
    for vote in classList:
        if vote not in classCount.keys():
            classCount[vote]=0
        classCount[vote]+=1
    sortedClassCount = sorted(classCount.items(),key=operator.itemgetter(1),reverse=True)
    return sortedClassCount[0][0]

# 递归构建决策树
def createTree(dataSet, labels):
    classList = [example[-1] for example in dataSet]  # 类别向量
    if classList.count(classList[0]) == len(classList):  # 如果只有一个类别，返回
        return classList[0]
    if len(dataSet[0]) == 1:  # 如果所有特征都被遍历完了，返回出现次数最多的类别
        return majorityCnt(classList)
    bestFeat = chooseBestFeatureToSplit(dataSet)  # 最优划分属性的索引
    bestFeatLabel = labels[bestFeat]  # 最优划分属性的标签
    myTree = {bestFeatLabel: {}}#分类结果以字典形式保存
    del (labels[bestFeat])  # 已经选择的特征不再参与分类
    featValues = [example[bestFeat] for example in dataSet]
    uniqueValue = set(featValues)  # 该属性所有可能取值，也就是节点的分支
    for value in uniqueValue:  # 对每个分支，递归构建树
        subLabels = labels[:]
        myTree[bestFeatLabel][value] = createTree(
            splitDataSet(dataSet, bestFeat, value), subLabels)
    return myTree

# 设置决策节点和叶节点的边框形状、边距和透明度，以及箭头的形状
# 定义判断结点形状,其中boxstyle表示文本框类型,fc指的是注释框颜色的深度
decisionNode = dict(boxstyle="square,pad=0.5", fc="0.9", color='r')
# 定义叶结点形状
leafNode = dict(boxstyle="circle, pad=0.5", fc="0.9", color='m')
# 定义父节点指向子节点或叶子的箭头形状
arrow_args = dict(arrowstyle="<-", connectionstyle="arc3", shrinkA=0,
                  shrinkB=16,color='g')

def plot_node(node_txt, center_point, parent_point, node_style):
    '''
    绘制父子节点，节点间的箭头，并填充箭头中间上的文本
    :param node_txt:文本内容
    :param center_point:文本中心点
    :param parent_point:指向文本中心的点
    '''
    createPlot.ax1.annotate(node_txt,
                            xy=parent_point,
                            xycoords='axes fraction',
                            xytext=center_point,
                            textcoords='axes fraction',
                            va="center",
                            ha="center",
                            bbox=node_style,
                            arrowprops=arrow_args)

def get_leafs_num(tree_dict):
    '''
    获取叶节点的个数
    :param tree_dict:树的数据字典
    :return tree_dict的叶节点总个数
    '''
    # tree_dict的叶节点总数
    leafs_num = 0

    # 字典的第一个键，也就是树的第一个节点
    root = list(tree_dict.keys())[0]
    # 这个键所对应的值，即该节点的所有子树。
    child_tree_dict = tree_dict[root]
    for key in child_tree_dict.keys():
        # 检测子树是否字典型
        if type(child_tree_dict[key]).__name__ == 'dict':
            # 子树是字典型，则当前树的叶节点数加上此子树的叶节点数
            leafs_num += get_leafs_num(child_tree_dict[key])
        else:
            # 子树不是字典型，则当前树的叶节点数加1
            leafs_num += 1

    # 返回tree_dict的叶节点总数
    return leafs_num

def get_tree_max_depth(tree_dict):
    '''
    求树的最深层数
    :param tree_dict:树的字典存储
    :return tree_dict的最深层数
    '''
    # tree_dict的最深层数
    max_depth = 0

    # 树的根节点
    root = list(tree_dict.keys())[0]
    # 当前树的所有子树的字典
    child_tree_dict = tree_dict[root]

    for key in child_tree_dict.keys():
        # 树的当前分支的层数
        this_path_depth = 0
        # 检测子树是否字典型
        if type(child_tree_dict[key]).__name__ == 'dict':
            # 如果子树是字典型，则当前分支的层数需要加上子树的最深层数
            this_path_depth = 1 + get_tree_max_depth(child_tree_dict[key])
        else:
            # 如果子树不是字典型，则是叶节点，则当前分支的层数为1
            this_path_depth = 1
        if this_path_depth > max_depth:
            max_depth = this_path_depth

    # 返回tree_dict的最深层数
    return max_depth


def plot_mid_text(center_point, parent_point, txt_str):
    '''
    计算父节点和子节点的中间位置，并在父子节点间填充文本信息
    :param center_point:文本中心点
    :param parent_point:指向文本中心点的点
    '''

    x_mid = (parent_point[0] - center_point[0]) / 2.0 + center_point[0]
    y_mid = (parent_point[1] - center_point[1]) / 2.0 + center_point[1]
    createPlot.ax1.text(x_mid, y_mid, txt_str)
    return

def plotTree(tree_dict, parent_point, node_txt):
    '''
    绘制树
    :param tree_dict:树
    :param parent_point:父节点位置
    :param node_txt:节点内容
    '''

    leafs_num = get_leafs_num(tree_dict)
    root = list(tree_dict.keys())[0]
    # plotTree.totalW表示树的深度
    center_point = (plotTree.xOff + (1.0 + float(leafs_num)) / 2.0 / plotTree.totalW, plotTree.yOff)
    # 填充node_txt内容
    plot_mid_text(center_point, parent_point, node_txt)
    # 绘制箭头上的内容
    plot_node(root, center_point, parent_point, decisionNode)
    # 子树
    child_tree_dict = tree_dict[root]
    plotTree.yOff = plotTree.yOff - 1.0 / plotTree.totalD
    # 因从上往下画，所以需要依次递减y的坐标值，plotTree.totalD表示存储树的深度
    for key in child_tree_dict.keys():
        if type(child_tree_dict[key]).__name__ == 'dict':
            plotTree(child_tree_dict[key], center_point, str(key))
        else:
            plotTree.xOff = plotTree.xOff + 1.0 / plotTree.totalW
            plot_node(child_tree_dict[key], (plotTree.xOff, plotTree.yOff), center_point, leafNode)
            plot_mid_text((plotTree.xOff, plotTree.yOff), center_point, str(key))
    # h绘制完所有子节点后，增加全局变量Y的偏移
    plotTree.yOff = plotTree.yOff + 1.0 / plotTree.totalD

    return


def createPlot(tree_dict):
    '''
    绘制决策树图形
    :param tree_dict
    :return 无
    '''
    # 设置绘图区域的背景色
    fig = plt.figure(1, facecolor='white')
    # 清空绘图区域
    fig.clf()
    # 定义横纵坐标轴,注意不要设置xticks和yticks的值!!!
    axprops = dict(xticks=[], yticks=[])
    createPlot.ax1 = plt.subplot(111, frameon=False, **axprops)
    # 由全局变量createPlot.ax1定义一个绘图区，111表示一行一列的第一个，frameon表示边框,**axprops不显示刻度
    plotTree.totalW = float(get_leafs_num(tree_dict))
    plotTree.totalD = float(get_tree_max_depth(tree_dict))
    plotTree.xOff = -0.5 / plotTree.totalW;
    plotTree.yOff = 1.0;
    plotTree(tree_dict, (0.5, 1.0), '')
    basepath = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/csv/img')
    path = basepath + '/dctree.jpg'
    plt.savefig(path)
    #plt.show()

def saveData(titledata,rowdata,filename='dctree.csv'):
    import csv
    basepath = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/csv/dctree')
    path = basepath + '/' + filename
    with open(path, "wt", newline='',encoding='utf-8-sig') as csvfile:
        f = csv.writer(csvfile)
        f.writerow(titledata)
        f.writerows(rowdata)

def generateDctree(filename='dctree.csv'):
    basepath = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/csv/dctree')
    path = basepath + '/' + filename
    df = readcsv(path)
    df = all_delete_empty(df)
    labels = df.columns.tolist()
    print(labels)
    del (labels[-1])
    print(labels)
    df = df.values.tolist()
    print(df)
    # tree_dict = createTree(dataSet, labels)
    tree_dict = createTree(df, labels)
    print(tree_dict)  # 输出决策树模型结果
    createPlot(tree_dict)

if __name__=='__main__':
    pass
