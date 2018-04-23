#import sklearn
import matplotlib.pyplot as plt
import pandas as pd


def importData(file):
    df=pd.read_excel(file,sheetname="final", header=None)
    data=df.as_matrix()

    """
    numDataPoints=len(data)
    numParametersPlusGoal = len(data[0])
    dataMeans = np.array([])
    dataSig = np.array([])
 
    for k in range(0, len(data[0])):
        dataMeans = np.append(dataMeans, np.mean(data[:,k]))
        dataSig = np.append(dataSig, np.std(data[:,k]))

        #Rewrite Mean and Sig of binary data
        if data[0,k]==-1 or data[0,k]==1 or data[0,k]==0:
            dataMeans[k]=0
            dataSig[k]=1

    dataNormed=np.empty(shape=(numDataPoints,numParametersPlusGoal))

    for p in range(0,len(data)):
        dataNormed[p]=(data[p]-dataMeans)/dataSig

    #Overwrite data the doesn't need normalization
    dataNormed[:,27]=data[:,27]

    return dataNormed,dataMeans,dataSig
    """

    print data

importData("testDATA.xlsx")


fig = plt.figure(figsize=(6,6))