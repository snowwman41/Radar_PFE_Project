

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import numpy as np
np.bool = np.bool_
import tensorflow as tf
import pandas as pd

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.callbacks import Callback, EarlyStopping, ModelCheckpoint
import matplotlib.pyplot as plt
from sklearn.experimental import enable_halving_search_cv

from sklearn.model_selection import train_test_split, HalvingGridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report


from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
import pickle

class Training:
    
    numberOfTrainingRuns=1
    filePrefix="../outputFolders/dataAcquisition_"
    detectionArray=[]
    noDetectionArray=[]    

    detectionFile=  "DETECTION.csv"
    noDetectionFile=  "NODETECTION.csv"

    detList=[]
    noDetList=[]

    #specify files indexes and the classification number
    fileIndex=[0,2,3,4,5,12,7,8,9,10,11]  #0,2,3,4,5,12 detection voiture / 7,8,9,10,11 detection humaine
    classificationNumber=[1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    classList=[]


    @classmethod
    def prepareData(cls):
        """ get, clean data and give classification number 
            depending of classificationNumber and fileIndex  """
        cleanedManually = True
        cleanDetFrame=[]
        cleanNoDetList=[]
        for classIndex,index in enumerate(cls.fileIndex):
            cleanFileDetList=[]
            detIndex=[] # removed false detections indexes array

            """           Detection          """           
            #get data
            detFile = f"{cls.filePrefix}{index}/{cls.detectionFile}" 
            detData=np.genfromtxt(detFile,delimiter=';',dtype=np.int32)
            
            #clean incoherent data (big difference in distance "bins" from close by samples) with moving average threshold
            i=0           
            while(i< len(detData)):   
                if not cleanedManually :
                    if i  < 10:
                        i=i+1
                        continue
                    else:        
                        #compare to moving average of 20 values                    
                        if abs(detData[i][1] - sum(array[1] for array in detData[i-10:i+9])/20)< 30:
                            cleanFileDetList.append(detData[i][1:])                        
                            detIndex.append(detData[i][0])
                            
                else:
                    cleanFileDetList.append(detData[i][1:])
                    detIndex.append(detData[i][0])
                i=i+1
            cleanFileDetList=np.array(cleanFileDetList)
            num_rows=cleanFileDetList.shape[0]
            
            #give classification number
            class_column=np.full((num_rows,1),cls.classificationNumber[classIndex])
            detDataFrame=pd.DataFrame(np.hstack((cleanFileDetList,class_column)))
            cleanDetFrame.append(detDataFrame)

            """           no Detection            """
            noDetFile = f"{cls.filePrefix}{index}/{cls.noDetectionFile}" 
            noDetData=np.genfromtxt(noDetFile,delimiter=';',dtype=np.int32)
            
            for data in noDetData:
                if data[0] in detIndex:
                    cleanNoDetList.append(data[1:])
                  
        detArray=np.vstack(cleanDetFrame)
        cleanDetFrame = pd.DataFrame(detArray)
        cleanNoDetList=np.array(cleanNoDetList)
        
        # """ No Detection"""
        # get random samples from noDetection the same size of Detection data
        num_rows=detArray.shape[0]
        class_column=np.full((num_rows,1),0)
        #give classification number which is always 0 in he case of no detection
        cleanNoDetFrame=pd.DataFrame(np.hstack((cleanNoDetList[np.random.choice(cleanNoDetList.shape[0],num_rows,replace=True)],class_column)))
        cls.fullDataFrame=pd.concat([cleanDetFrame,cleanNoDetFrame],ignore_index=True)


    @classmethod
    def trainNN(cls):
        # Set paths for saving the model
        checkpoint_path = 'nn_best_model.h5'
        model_save_path = 'nn_final_model.h5'

        # Load data
     
        # Split features and labels
        X = cls.fullDataFrame.iloc[:, :-1].values
        y = cls.fullDataFrame.iloc[:, -1].values

        # Standardize the data
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Split data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

        # Custom callback to save the best weights based on val_accuracy
        class BestValAccuracy(Callback):
            def __init__(self):
                super(BestValAccuracy, self).__init__()
                self.best_weights = None
                self.best_val_accuracy = 0.0

            def on_epoch_end(self, epoch, logs=None):
                current_val_accuracy = logs.get('val_accuracy')
                if current_val_accuracy > self.best_val_accuracy:
                    self.best_val_accuracy = current_val_accuracy
                    self.best_weights = self.model.get_weights()

            def on_train_end(self, logs=None):
                if self.best_weights is not None:
                    self.model.set_weights(self.best_weights)

        # Build the neural network model
        model = Sequential()
        model.add(Dense(128, input_dim=X_train.shape[1], activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(256, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(64, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(32, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(16, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(1, activation='sigmoid'))

        # Compile the model
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

        # Set up EarlyStopping and ModelCheckpoint to save the best model based on val_accuracy
        early_stopping = EarlyStopping(monitor='val_accuracy', patience=300, mode='max', restore_best_weights=True)
        best_val_accuracy = BestValAccuracy()
        model_checkpoint = ModelCheckpoint(checkpoint_path, monitor='val_accuracy', save_best_only=True, mode='max')

        # Train the model
        history = model.fit(X_train, y_train, validation_split=0.2, epochs=12000, batch_size=32, callbacks=[early_stopping, best_val_accuracy, model_checkpoint])

        # Restore the best weights based on val_accuracy
        if best_val_accuracy.best_weights is not None:
            model.set_weights(best_val_accuracy.best_weights)
            model.save(model_save_path)  # Save the final model with the best val_accuracy

        # Print the best val_accuracy
        print(f'Best Validation Accuracy: {best_val_accuracy.best_val_accuracy:.4f}')
        y_pred = model.predict(X_test)
        y_pred_classes = (y_pred > 0.5).astype(int)  # Convert probabilities to class labels

        # Print classification report
        report = classification_report(y_test, y_pred_classes,output_dict=True)
        print("Classification Report:\n", report)
        # Evaluate the model
        loss, accuracy = model.evaluate(X_test, y_test)
        # print(f'Test Accuracy: {accuracy*100:.2f}%')
        return report
        # # Visualize the training process
        # plt.plot(history.history['loss'], label='Training Loss')
        # plt.plot(history.history['val_loss'], label='Validation Loss')
        # plt.legend()
        # plt.show()

        # plt.plot(history.history['accuracy'], label='Training Accuracy')
        # plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
        # plt.legend()
        # plt.show()

    @classmethod
    def trainDecisionTree(cls):
       
        # 2. Separate features (X) and target (y)
        X = cls.fullDataFrame.iloc[:, :-1].values
        y = cls.fullDataFrame.iloc[:, -1].values

        # 3. Split into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # 4. Define the parameter grid to explore (hyperparameter tuning)
        param_grid = {
            'criterion': ['gini', 'entropy'],
            'max_depth': [None, 5, 10, 15],  # Try different depths or None for no limit
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }

        # 5. Create the base Decision Tree model
        base_model = DecisionTreeClassifier()

        # 6. Create the HalvingGridSearchCV object
        sh = HalvingGridSearchCV(base_model, param_grid, cv=5, factor=2, resource='n_samples', scoring='accuracy').fit(X_train, y_train)

        # 7. Get the best model from the search
        best_model = sh.best_estimator_

        # 8. Make predictions on the test data
        y_pred = best_model.predict(X_test)

        # 9. Evaluate the model
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred,output_dict=True)

        # print(f"Accuracy: {accuracy}")
        # print("Classification Report:\n", report)
        return report

    @classmethod
    def randomForest(cls):

        # 1. Load and preprocess data 
        X = cls.fullDataFrame.iloc[:, :-1]  # Features (all columns except the last)
        y = cls.fullDataFrame.iloc[:, -1]   # Target (last column)

        # 2. Split into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # 4. Definition of the parameter grid to explore
        param_grid = {
            'n_estimators': [50, 100, 200], 
            'max_depth': [None, 10, 20], 
            'min_samples_split': [2, 5, 10]
        }

        # 5. Create the base Random Forest model
        base_model = RandomForestClassifier(random_state=42)

        # 7. Train and select the best model
        sh = HalvingGridSearchCV(base_model, param_grid, cv=5, factor=2, resource='n_samples',  scoring='accuracy').fit(X_train, y_train)

        # 7. Train and select the best model
        best_model = sh.best_estimator_

        # 8. Save the best model
        model_filename = "random_forest_model.pkl"
        with open(model_filename, "wb") as f:
            pickle.dump(best_model, f)

        # 8. Make predictions on the test data
        y_pred = best_model.predict(X_test)

        # 9. Evaluate the model 
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred,output_dict=True)

        # print(f"Accuracy: {accuracy}")
        # print("Classification Report:\n", report)
        # print("Best Parameters:", sh.best_params_) 
        
        return report
    
    @classmethod
    def svm(cls):

        # 1. Load and preprocess data 
        X = cls.fullDataFrame.iloc[:, :-1]  # Features (all columns except the last)
        y = cls.fullDataFrame.iloc[:, -1]   # Target (last column)

        # Standardize features (important for SVM)
        scaler = StandardScaler()
        X = scaler.fit_transform(X)

        # 2. Split into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # 3. Define SVM model and hyperparameter grid
        svm = SVC()
        param_grid = {
            'C': [0.1, 1, 10, 100],  # Regularization parameter (wider range)
            'kernel': ['linear', 'rbf', 'poly'],  # Different kernel functions
            'gamma': ['scale', 'auto', 0.1, 1, 10], # Kernel coefficient (only for 'rbf' and 'poly')
            'degree': [2, 3, 4]  # Degree of the polynomial kernel (only for 'poly')
        }

        # 4. Create and fit HalvingGridSearchCV object
        search = HalvingGridSearchCV(svm, param_grid, scoring='accuracy', n_jobs=-1, random_state=42)
        search.fit(X_train, y_train)

        # 5. Get the best model and evaluate
        best_svm = search.best_estimator_
        y_pred = best_svm.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred,output_dict=True)

        # print("\nBest SVM Hyperparameters:", search.best_params_)
        # print("\nAccuracy on Test Set:", accuracy)
        # print("Classification Report:\n", report)
        return report
    
if __name__ == "__main__":  
    
    i=0
    nnDict = {'0': {'precision': 0, 'recall': 0, 'f1-score': 0., 'support': 0}, \
          '1': {'precision': 0, 'recall': 0, 'f1-score': 0, 'support': 0}, \
            'accuracy': 0, 'macro avg': {'precision': 0, 'recall': 0, 'f1-score': 0, 'support': 0}, \
          'weighted avg': {'precision': 0, 'recall': 0, 'f1-score': 0, 'support': 0}}
    
    rfDict = {'0': {'precision': 0, 'recall': 0, 'f1-score': 0., 'support': 0}, \
          '1': {'precision': 0, 'recall': 0, 'f1-score': 0, 'support': 0}, \
            'accuracy': 0, 'macro avg': {'precision': 0, 'recall': 0, 'f1-score': 0, 'support': 0}, \
          'weighted avg': {'precision': 0, 'recall': 0, 'f1-score': 0, 'support': 0}}
    
    svmDict= {'0': {'precision': 0, 'recall': 0, 'f1-score': 0., 'support': 0}, \
          '1': {'precision': 0, 'recall': 0, 'f1-score': 0, 'support': 0}, \
            'accuracy': 0, 'macro avg': {'precision': 0, 'recall': 0, 'f1-score': 0, 'support': 0}, \
          'weighted avg': {'precision': 0, 'recall': 0, 'f1-score': 0, 'support': 0}}

    
    decisionTreeDict = {'0': {'precision': 0, 'recall': 0, 'f1-score': 0., 'support': 0}, \
          '1': {'precision': 0, 'recall': 0, 'f1-score': 0, 'support': 0}, \
            'accuracy': 0, 'macro avg': {'precision': 0, 'recall': 0, 'f1-score': 0, 'support': 0}, \
          'weighted avg': {'precision': 0, 'recall': 0, 'f1-score': 0, 'support': 0}}
    
    while i< Training.numberOfTrainingRuns: 
        Training.prepareData()


        NNResult=Training.trainNN()
        for key in nnDict:
            if isinstance(nnDict[key], dict):  # Handle nested dictionaries
                for metric in nnDict[key]:
                    nnDict[key][metric] += NNResult[key][metric]/Training.numberOfTrainingRuns
            else:  # Handle simple values (e.g., 'accuracy')
                nnDict[key] += NNResult[key]/Training.numberOfTrainingRuns
        
        rfResult=Training.randomForest()
        for key in rfDict:
            if isinstance(rfDict[key], dict):  # Handle nested dictionaries
                for metric in rfDict[key]:
                    rfDict[key][metric] += rfResult[key][metric]/Training.numberOfTrainingRuns
            else:  # Handle simple values (e.g., 'accuracy')
                rfDict[key] += rfResult[key]/Training.numberOfTrainingRuns

        svmResult=Training.svm()
        for key in svmDict:
            if isinstance(svmDict[key], dict):  # Handle nested dictionaries
                for metric in svmDict[key]:
                    svmDict[key][metric] += svmResult[key][metric]/Training.numberOfTrainingRuns
            else:  # Handle simple values (e.g., 'accuracy')
                svmDict[key] += svmResult[key]/Training.numberOfTrainingRuns

        decisionTreeResult=Training.trainDecisionTree()
        for key in decisionTreeDict:
            if isinstance(decisionTreeDict[key], dict):  # Handle nested dictionaries
                for metric in decisionTreeDict[key]:
                    decisionTreeDict[key][metric] += decisionTreeResult[key][metric]/Training.numberOfTrainingRuns
            else:  # Handle simple values (e.g., 'accuracy')
                decisionTreeDict[key] += decisionTreeResult[key]/Training.numberOfTrainingRuns

        i=i+1
    print("Décision Tree :  ",pd.DataFrame(decisionTreeDict))
    print("Neural Network:  ",pd.DataFrame(nnDict))
    print("SVM :  ",pd.DataFrame(svmDict))
    print("Random forest:  ",pd.DataFrame(rfDict))

#x=[384,295.08401430275956,586.9914721922971,-145.46965065342204,-405.45471459172416,-74.54191776912313,300.8319886684544,200.5718603205026,-198.03417402358212,-191.6312392755768,-19.74022857712587,135.12062924403733,318.4900723134347,-133.26097630019552,-518.5824793466218,196.44776521376906,457.47203479528247,-241.17520927170102,-206.75517661687854,187.3210452082661,-4.074441620907635,-86.80919699329237,49.2402694260893,42.6151997921664,35.549650479628795,-110.45761098099769,-158.68121213474888,252.42876637749646,269.04612285864175,-369.0497756571263,-349.6328377948391,379.1466425440907,380.34634295483346,-279.78512704668304,-338.0642339892397,147.70509431423082,253.49276023839056,-71.75913005556475,-190.56918432826168,82.77127684611459,161.12974189703982,-134.3050660893018,-139.43836232197535,161.12652200383366,117.41068510853034,-166.92418076671225,-119.45169907629531,199.93540065528333,148.11222539872136,-257.1624516541357,-179.93350216118938,285.72653813707063,223.14636718609964,-270.12465340531685,-301.1977604106686,251.87280315995525,393.2171829143017,-261.33814662790274,-437.06224874350255,291.112876604618,411.1537428332871,-319.5475324272972,-364.9870461136143,328.25771388811484,354.52571150957874,-307.54685666634987,-378.8998874258743,278.9128477985804,404.48674377690094,-260.87924361111004,-416.1711708050694,247.76829542156497,427.87863700893337,-236.61203999573786,-427.35205260629664,226.00636510291977,390.9188404914528,-205.7363045968376,-360.3532342422309,174.8087295035931,382.52524672105704,-165.41130224394252,-440.20562656744573,189.00500687750815,481.41672022905664,-227.7802727140251,-489.5427800271876,264.76733536102876,479.66002611507616,-285.248983883735,-470.2647132261673,276.1382996044948,484.55798573708444,-242.69282131845898,-497.9016966222337,206.41395578712934,483.3041256526966,-180.37381072085768,-457.32516894860044,187.87166957913388,439.7001585976046]

# import time    
# with open("./random_forest_model.pkl", "rb") as f:
#     loaded_model = pickle.load(f)


#     time1=time.time()
#     predictions = loaded_model.predict(np.array(x).reshape(1,-1))
#     print(predictions)
#     print(time.time()- time1)
    

