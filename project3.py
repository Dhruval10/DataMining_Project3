from numpy import *
import pandas as pd
import csv
import hashlib
import re
from sklearn import *
import random
import os
from math import sqrt
import math
import time

class DrugDiscovery:
    descriptors = None
    targets = None 
    active_descriptors = None  
    X_Train = None
    X_Valid = None  
    X_Test = None
    Y_Train = None
    Y_Valid = None
    Y_Test = None
    Data = None
    binary_model = None
    
    def __init__(self, descriptors_file, targets_file):
        self.descriptors = self.open_descriptor_matrix(descriptors_file)
        self.targets = self.open_target_values(targets_file)
        
 #**********************************************************************************************       
    def processData(self):
        self.descriptors, self.targets = self.removeInvalidData(self.descriptors, self.targets)
        self.descriptors, self.active_descriptors = self.removeNearConstantColumns(self.descriptors)
        # Rescale the descriptor data
        self.descriptors = self.rescale_data(self.descriptors)
        #sort data
        self.descriptors, self.targets = self.sort_descriptor_matrix(self.descriptors, self.targets)
        
#**********************************************************************************************
    def splitData(self):
        self.X_Train, self.X_Valid, self.X_Test, self.Y_Train, self.Y_Valid, self.Y_Test = self.simple_split(self.descriptors, self.targets)
        self.data = {'TrainX': self.X_Train, 'TrainY': self.Y_Train, 'ValidateX': self.X_Valid, 'ValidateY': self.Y_Valid,
                'TestX': self.X_Test, 'TestY': self.Y_Test, 'UsedDesc': self.active_descriptors}

        print(str(self.descriptors.shape[1]) + " valid descriptors and " + str(self.targets.__len__()) + " molecules available.")

#**********************************************************************************************
# Set up the demonstration model
    def setUpDemoModel(self):
        # featured_descriptors = [4, 8, 12, 16]  # These indices are "false", applying only to the truncated post-filter descriptor matrix.
        binary_model = zeros((50, 593))
        count = 0

        for i in range(50):
          for j in range(593):
              r = random.randint(0, 593)
              L = int(0.015 * 593)

              if r < L:
                  binary_model[i][j] = 1
                  count += 1
          if count > 5 and count < 25:
              continue
          else:
              i -= 1

        # self.binary_model = zeros((1, self.X_Train.shape[1]))
        # self.binary_model[0][featured_descriptors] = 1
        
        
#**********************************************************************************************
# Create a Multiple Linear Regression object to fit our demonstration model to the data
    def runModel(self, regressor, instructions):
        trackDesc, trackFitness, trackModel, \
        trackDimen, trackR2train, trackR2valid, \
        trackR2test, testRMSE, testMAE, \
        testAccPred = self.evaluate_population(model=regressor, instructions=instructions, data=self.data,
                                                           population=self.binary_model, exportfile=None)  
        self.outputModelInfo(trackDesc, trackFitness, trackModel, trackDimen, trackR2train, trackR2valid, trackR2test, testRMSE, testMAE, testAccPred)

#**********************************************************************************************

    # def geneticModel(self, regressor, instructions, numGenerations, fileW):
        
    #     fileW.writerow(['Descriptor ID', 'Fitness', 'Algorithm', 'Dimen', 'R2_Train', 'R2_Valid', 'R2_Test', 'Q2', 'RMSE', 'MAE', 'Abs. Errors'])
        
    #     population = zeros((50,self.X_Train.shape[1])) 
        
    #     for i in range(50):
    #         population[i] = self.getValidRow()
        

    #     for generation in range(numGenerations):
    #         print("Generation: ", generation)
            
    #         trackDesc, trackFitness, trackModel, \
    #         trackDimen, trackR2train, trackR2valid, \
    #         trackR2test, testRMSE, testMAE, \
    #         testAccPred = self.evaluate_population(model=regressor, instructions=instructions, data=self.data,population=population, exportfile=fileW)  
            
    #         oldPopulation = population.copy()
    #         population = zeros((50, self.X_Train.shape[1]))
            
    #         dad, mom = self.generateParents(oldPopulation, trackFitness)
    #         child1, child2 = self.generateChildren(dad, mom)
    #         population[0] = dad
    #         population[1] = mom
    #         population[2] = child1
    #         population[3] = child2
    #         for i in range(4,50):
    #             population[i] = self.getValidRow()
    #         # self.outputModelInfo(trackDesc, trackFitness, trackModel, trackDimen, trackR2train, trackR2valid, trackR2test, testRMSE, testMAE, testAccPred)
    #         population = self.mutatePopulation(population)

#**********************************************************************************************
    def isValidRow(self, row):
        count = 0
        for value in row[0]:
            if value == 1:
                count += 1
            if count > 5 or count < 25:
                return row

    def getValidRow(self):
        numDescriptors=self.X_Train.shape[1]
        validRow = zeros((1,numDescriptors))
        count = 0
        while (count < 5) or (count > 25):
            count = 0
            for i in range(numDescriptors):
                rand = round(random.uniform(0,100),2)
                if rand < 1.5:
                    validRow[0][i] = 1
                    count +=1
        return validRow

    def DifferentialEvolutionModel(self, regressor, instructions, numGenerations, fileW):

        fileW.writerow(['Descriptor ID', 'Fitness', 'Algorithm', 'Dimen', 'R2_Train', 'R2_Valid', 'R2_Test', 'RMSE', 'MAE', 'Abs. Errors'])
        population = zeros((50,self.X_Train.shape[1]))

        for i in range(50):
                population[i] = self.getValidRow()
        

        for generation in range(numGenerations):
            print("Generation: ", generation)
            
            trackDesc, trackFitness, trackModel, \
            trackDimen, trackR2train, trackR2valid, \
            trackR2test, testRMSE, testMAE, \
            testAccPred = self.evaluate_population(model=regressor, instructions=instructions, data=self.data,population=population, exportfile=fileW)
            counter = 0
            shawn = []
            trail = []
            for i in range(50):
                trail.append(i)

            for key in trackDesc.keys():    
                shawn.append(trackFitness[key])

            df = pd.DataFrame(shawn)
            df.columns = ['fitness']
            # print(df)
            df1 = pd.DataFrame(trail)
            df1.columns = ['order']


            # print('Now df1!')
            # print(df1)
            df['order'] = df1

            # print('now after append')
            # print (df)

            df2 = df.sort_values('fitness')
            # print('After sorting!')
            # print(df2)

            order = []

            order=df2['order'].values.tolist()
            # print(order)

            #savetxt('binary_model.csv', binary_model, delimiter=',')
            binary_model2 = population.copy()

            for i in range(len(order)):
                #for j in range(593):
                a = order[i]
                binary_model2[i] = population[a]


            # print(binary_model2)
            #savetxt('binary_model2.csv', binary_model2, delimiter=',')


            population = binary_model2

            oldPopulation = population

            F = 0.7
            CV = 0.7
    
            for i in range(1, 50):
                # print('Inside loop')
                
                V = zeros(593)
                # print(V)

                a = random.randint(0, 49)
                b = random.randint(0, 49)
                c = random.randint(0, 49)

                # A = oldPopulation[a]
                # B = oldPopulation[b]
                # C = oldPopulation[c]

                # print("a b and c are", a, b, c)
                # print("A: ", A)
                # print("B: ", B)
                # print("C: ", C)

                for j in range(self.X_Train.shape[1]):
                    V[j] = math.floor(abs(oldPopulation[a,j] + (F * (oldPopulation[b,j]-oldPopulation[c,j]))))

                    rand_num = random.uniform(0, 1)
                    if (rand_num < CV):
                        population[i, j] = V[j]
                    else:
                        continue

            for i in range(0,50):
                check  = 0
                for j in range(0,593):
                    if population[i, j] == 1:
                        check += 1
            
                if check < 5 or check > 25:
                    population[i] = self.getValidRow()        
            # print(population)
    

#**********************************************************************************************        
    def outputModelInfo(self,trackDesc, trackFitness, trackModel, trackDimen, trackR2train, trackR2valid, trackR2test, testRMSE, testMAE, testAccPred): 
        print("\n\nFitness\t\tDimension\t\t\tR_SquareTrain\t\tR_SquareValid\t\tRMSE\t\tDescriptors")
        print("========================================================================")
        
        for key in trackDesc.keys():
            print(str(trackFitness[key]) + "\t\t" + str(trackDimen[key]) + "\t\t\t\t\t" + str(trackR2train[key]) \
            + "\t\t\t\t" + str(trackR2valid[key]) + "\t\t\t\t" + str(testRMSE[key]) + "\t\t" + str(trackDesc[key]))

        '''
        for key in trackDesc.keys():
            print("Descriptors:")
            print("\t" + str(trackDesc[key]))  # This will show the "true" indices of the featured descriptors in the full matrix
            print("Fitness:")
            print("\t" + str(trackFitness[key]))
            print("Model:")
            print("\t" + str(trackModel[key]))
            print("Dimensionality:")
            print("\t" + str(trackDimen[key]))
            print("R2_Train:")
            print("\t" + str(trackR2train[key]))
            print("R2_Valid:")
            print("\t" + str(trackR2valid[key]))
            print("R2_Test:")
            print("\t" + str(trackR2test[key]))
            print("Testing RMSE:")
            print("\t" + str(testRMSE[key]))
            print("Testing MAE:")
            print("\t" + str(testMAE[key]))
            print("Acceptable Predictions From Testing Set:")
            print("\t" + str(100*testAccPred[key]) + "% of predictions")
        '''
            
#**********************************************************************************************
# try to optimize this code if possible
    def open_descriptor_matrix(self,fileName):
        preferred_delimiters = [';', '\t', ',', '\n']

        with open(fileName, mode='r') as csvfile:
            # Dynamically determining the delimiter used in the input file
            row = csvfile.readline()

            delimit = ','
            for d in preferred_delimiters:
                if d in row:
                    delimit = d
                    break

            # Reading in the data from the input file
            csvfile.seek(0)
            datareader = csv.reader(csvfile, delimiter=delimit, quotechar=' ')
            dataArray = array([row for row in datareader if row != ''], order='C')

        if (min(dataArray.shape) == 1):  # flatten arrays of one row or column
            return dataArray.flatten(order='C')
        else:
            return dataArray

#************************************************************************************
#Try to optimize this code if possible
    def open_target_values(self,fileName):
        preferred_delimiters = [';', '\t', ',', '\n']

        with open(fileName, mode='r') as csvfile:
            # Dynamically determining the delimiter used in the input file
            row = csvfile.readline()
            delimit = ','
            for d in preferred_delimiters:
                if d in row:
                    delimit = d
                    break

            csvfile.seek(0)
            datalist = csvfile.read().split(delimit)
            if ' ' in datalist:
                datalist = datalist[0].split(' ')

        for i in range(datalist.__len__()):
            datalist[i] = datalist[i].replace('\n', '')
            try:
                datalist[i] = float(datalist[i])
            except:
                datalist[i] = datalist[i]

        try:
            datalist.remove('')
        except ValueError:
            no_empty_strings = True

        return datalist  
 #**********************************************************************************************   
    def removeInvalidData(self, descriptors, targets):
        # Numpy to df and series
        descriptors_df = pd.DataFrame(descriptors)
        targets_series = pd.Series(targets)

        # Junk to NaN
        descriptors_df = descriptors_df.apply(pd.to_numeric, errors='coerce')

        # Get indexes of rows with any NaN values
        descriptor_rows_with_nan = [index for index, row in descriptors_df.iterrows() if row.isnull().any()]

        # Drop rows with any NaN values
        descriptors_df = descriptors_df.drop(descriptor_rows_with_nan)
        targets_series = targets_series.drop(descriptor_rows_with_nan)
        delCount = len(descriptor_rows_with_nan)
        print("Dropped ", delCount, " rows containing any junk values.")

        # Drop columns that have more than 20 junks
        numJunkPerCol_Series = descriptors_df.isna().sum()
        delCount = numJunkPerCol_Series[numJunkPerCol_Series > 20].count()
        descriptors_df = descriptors_df.drop(numJunkPerCol_Series[numJunkPerCol_Series > 20].index, axis=1)
        print("Dropped ", delCount, " columns containing more than 20 junk values.")

        # change NaN to 0
        print("Converting remaining junk values to 0...")
        descriptors_df = descriptors_df.fillna(0)

        # drop columns containing all zeros
        tempLen = len(descriptors_df.columns)
        descriptors_df = descriptors_df.loc[:, descriptors_df.ne(0).any(axis=0)]
        delCount = tempLen - len(descriptors_df.columns)
        print("Dropped ", delCount, " columns containing all zeros.")

        # df and series to numpy for return
        descriptors = descriptors_df.to_numpy()
        targets = targets_series.to_numpy()

        return descriptors, targets
    
#**********************************************************************************************
    # Removes constant and near-constant descriptors.
    # But I think also does that too for real data.
    # So for now take this as it is

    def removeNearConstantColumns(self, data_matrix, num_unique=10):
        useful_descriptors = [col for col in range(data_matrix.shape[1])
                              if len(set(data_matrix[:, col])) > num_unique]
        filtered_matrix = data_matrix[:, useful_descriptors]

        remaining_desc = zeros(data_matrix.shape[1])
        remaining_desc[useful_descriptors] = 1

        return filtered_matrix, where(remaining_desc == 1)[0]
    
#**********************************************************************************************
    def rescale_data(self, descriptor_matrix):
        # Statistics for dataframe
        mean = descriptor_matrix.mean()
        stdev = descriptor_matrix.std()

        # Standardize DF (rescale)
        rescaled_descriptors = ((descriptor_matrix)- mean)/stdev
        
        print("Rescaled Descriptors:")
        print(rescaled_descriptors)
        
        return rescaled_descriptors
#**********************************************************************************************
    def sort_descriptor_matrix(self, descriptors, targets):
        # Placing descriptors and targets in ascending order of target (IC50) value.
        alldata = ndarray((descriptors.shape[0], descriptors.shape[1] + 1))
        alldata[:, 0] = targets
        alldata[:, 1:alldata.shape[1]] = descriptors
        alldata = alldata[alldata[:, 0].argsort()]
        descriptors = alldata[:, 1:alldata.shape[1]]
        targets = alldata[:, 0]

        return descriptors, targets
#**********************************************************************************************
# Performs a simple split of the data into training, validation, and testing sets.
# So how does it relate to the Data Mining Prediction?

    def simple_split(self, descriptors, targets):

        testX_indices = [i for i in range(descriptors.shape[0]) if i % 4 == 0]
        validX_indices = [i for i in range(descriptors.shape[0]) if i % 4 == 1]
        trainX_indices = [i for i in range(descriptors.shape[0]) if i % 4 >= 2]

        TrainX = descriptors[trainX_indices, :]
        ValidX = descriptors[validX_indices, :]
        TestX = descriptors[testX_indices, :]

        TrainY = targets[trainX_indices]
        ValidY = targets[validX_indices]
        TestY = targets[testX_indices]

        return TrainX, ValidX, TestX, TrainY, ValidY, TestY
#**********************************************************************************************
    def evaluate_population(self, model, instructions, data, population, exportfile):
        numOfPop = population.shape[0]
        fitness = zeros(numOfPop)
        predictive = 0

        TrainX = data['TrainX']
        TrainY = data['TrainY']
        ValidateX = data['ValidateX']
        ValidateY = data['ValidateY']
        TestX = data['TestX']
        TestY = data['TestY']
        UsedDesc = data['UsedDesc']

        trackDesc, trackFitness, trackModel, trackDimen, trackR2, trackR2PredValidation, \
        trackR2PredTest, trackRMSE, trackMAE, trackAcceptPred, trackCoefficients = self.InitializeTracks()

        unfit = 1000

        for i in range(numOfPop):

            xi = list(where(population[i] == 1)[0])

            idx = hashlib.sha1(array(xi)).digest()

            # Condenses binary models to a list of the indices of active features
            X_train_masked = TrainX.T[xi].T
            X_validation_masked = ValidateX.T[xi].T
            X_test_masked = TestX.T[xi].T

            try:
                model = model.fit(X_train_masked, TrainY)
            except:
                return unfit, fitness

            # Computed predicted values
            Yhat_training = model.predict(X_train_masked)
            Yhat_validation = model.predict(X_validation_masked)
            Yhat_testing = model.predict(X_test_masked)

            # Compute R2 scores (Prediction for Validation and Test set)
            r2_train = model.score(X_train_masked, TrainY)
            r2validation = model.score(X_validation_masked, ValidateY)
            r2test = model.score(X_test_masked, TestY)
            model_rmse, num_acceptable_preds = self.calculateRMSE(TestY, Yhat_testing)
            model_mae = self.calculateMAE(TestY, Yhat_testing)

            # Calculating fitness value
            fitness[i] = self.get_fitness(xi, TrainY, ValidateY, Yhat_training, Yhat_validation)

            # store stats
            trackDesc[idx] = (re.sub(",", "_", str(xi)))  # Editing descriptor set to match actual indices in the original data.
            trackDesc[idx] = (re.sub(",", "_", str(UsedDesc[xi].tolist())))  # Editing descriptor set to match actual indices in the original data.

            trackFitness[idx] = self.sigfig(fitness[i])
            trackModel[idx] = instructions['algorithm'] + ' with ' + instructions['MLM_type']
            trackDimen[idx] = int(xi.__len__())

            trackR2[idx] = self.sigfig(r2_train)
            trackR2PredValidation[idx] = self.sigfig(r2validation)
            trackR2PredTest[idx] = self.sigfig(r2test)

            trackRMSE[idx] = self.sigfig(model_rmse)
            trackMAE[idx] = self.sigfig(model_mae)
            trackAcceptPred[idx] = self.sigfig(float(num_acceptable_preds) / float(Yhat_testing.shape[0]))

            # For loop ends here.

        self.write(exportfile, trackDesc, trackFitness, trackModel, trackDimen, trackR2, trackR2PredValidation, trackR2PredTest, trackRMSE, trackMAE, trackAcceptPred)

        return trackDesc, trackFitness, trackModel, trackDimen, trackR2, trackR2PredValidation, trackR2PredTest, trackRMSE, trackMAE, trackAcceptPred

#**********************************************************************************************
    def sigfig(self, x):
        return float("%.4f"%x)

#**********************************************************************************************
    def InitializeTracks(self):
        trackDesc = {}
        trackFitness = {}
        trackAlgo = {}
        trackDimen = {}
        trackR2 = {}
        trackR2PredValidation = {}
        trackR2PredTest = {}
        trackRMSE = {}
        trackMAE = {}
        trackAcceptPred = {}
        trackCoefficients = {}

        return trackDesc, trackFitness, trackAlgo, trackDimen, trackR2, trackR2PredValidation, trackR2PredTest, \
               trackRMSE, trackMAE, trackAcceptPred, trackCoefficients

#**********************************************************************************************
    def get_fitness(self, xi, T_actual, V_actual, T_pred, V_pred, gamma=3, dim_limit=None, penalty=0.05):
        n = len(xi)
        mT = len(T_actual)
        mV = len(V_actual)

        train_errors = [T_pred[i] - T_actual[i] for i in range(T_actual.__len__())]
        RMSE_t = sum([element**2 for element in train_errors]) / mT
        valid_errors = [V_pred[i] - V_actual[i] for i in range(V_actual.__len__())]
        RMSE_v = sum([element**2 for element in valid_errors]) / mV

        numerator = ((mT - n - 1) * RMSE_t) + (mV * RMSE_v)
        denominator = mT - (gamma * n) - 1 + mV
        fitness = sqrt(numerator/denominator)


        # Adjusting for high-dimensionality models.
        if dim_limit is not None:
            if n > int(dim_limit * 1.5):
                fitness += ((n - dim_limit) * (penalty * dim_limit))
            elif n > dim_limit:
                fitness += ((n - dim_limit) * penalty)

        return fitness

#**********************************************************************************************
    def calculateMAE(self, experimental, predictions):
        errors = [abs(experimental[i] - predictions[i]) for i in range(experimental.__len__())]
        return sum(errors) / experimental.__len__()

#**********************************************************************************************
    def calculateRMSE(self, experimental, predictions):
        sum_of_squares = 0
        errors_below_1 = 0
        for mol in range(experimental.__len__()):
            abs_error = abs(experimental[mol] - predictions[mol])
            sum_of_squares += pow(abs_error, 2)
            if abs_error < 1:
                errors_below_1 += 1
        return sqrt(sum_of_squares / experimental.__len__()), int(errors_below_1)

#**********************************************************************************************
    def write(self, exportfile, descriptors, fitnesses, modelnames,
                    dimensionality, r2trainscores,r2validscores, r2testscores, rmse, mae, acc_pred):

        if exportfile is not None:
            for key in fitnesses.keys():
                exportfile.writerow([descriptors[key], fitnesses[key], modelnames[key],
                                     dimensionality[key], r2trainscores[key], r2validscores[key],
                                     r2testscores[key], rmse[key], mae[key], acc_pred[key]
                                     ])


def main():
    start_time = time.time()
    Alzheimer = DrugDiscovery("Practice_Descriptors.csv","Practice_Targets.csv")
    Alzheimer.processData()
    Alzheimer.splitData()
    Alzheimer.setUpDemoModel()
    
    #directory = os.path.join(os.getcwd(), 'Outputs')
    #os.makedirs(os.path.dirname(directory),exist_ok=True)
    
    directory = os.path.join(os.getcwd(), 'Outputs')

    #MLR
    # print("\nMLR: ")
    
    # output_filename = 'MLR_Outputs.csv'
    # file_path = os.path.join(directory, output_filename)
    # os.makedirs(os.path.dirname(file_path), exist_ok=True)
    # fileOut = open(file_path, 'w', newline='')  # create stream object for output file
    # fileW = csv.writer(fileOut)
    
    # regressor = linear_model.LinearRegression()
    # instructions = {'dim_limit': 4, 'algorithm': 'GA', 'MLM_type': 'MLR'}

    # Alzheimer.DifferentialEvolutionModel(regressor, instructions, 10000, fileW)


    # # #SVM
    # print("\nSVM: ") 
    
    # output_filename = 'SVM_Outputs.csv'
    # file_path = os.path.join(directory, output_filename)
    # os.makedirs(os.path.dirname(file_path), exist_ok=True)
    # fileOut = open(file_path, 'w', newline='')  # create stream object for output file
    # fileW = csv.writer(fileOut)
    
    # regressor = svm.SVR()
    # instructions = {'dim_limit': 4, 'algorithm': 'GA', 'MLM_type': 'SVM'}
    # Alzheimer.DifferentialEvolutionModel(regressor, instructions, 10000, fileW)
    
    
    #ANN
    print("\nANN: ") 
    
    output_filename = 'ANN_Outputs.csv'
    file_path = os.path.join(directory, output_filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    fileOut = open(file_path, 'w', newline='')  # create stream object for output file
    fileW = csv.writer(fileOut)
    
    regressor = neural_network.MLPRegressor(hidden_layer_sizes=(150, 50, 10))
    instructions = {'dim_limit': 4, 'algorithm': 'GA', 'MLM_type': 'ANN'}
    Alzheimer.DifferentialEvolutionModel(regressor, instructions, 1200, fileW)
    
    print("--- %s seconds ---" % (time.time() - start_time))
    

if __name__ == "__main__":
    main()

    # df = df['index', 'values']