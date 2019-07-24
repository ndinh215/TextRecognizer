"""
Train model
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from comet_ml import Experiment

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from sklearn.model_selection import train_test_split
from src.training.util import train_model
from src.data.emnist_dataset import EMNIST
from src.models.character_model import Character_Model
from src.networks.lenet import lenet
import argparse

def _parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--save-model", type=int, default=False,
        help="whether or not model should be saved")
    parser.add_argument("-w", "--weights", type=str, default=True,
        help="whether or not weights should be saved")
    parser.add_argument("-m", '--model', type=str, default="Character_Model",
        help="which model to use")
    parser.add_argument("-n", '--network', type=str, default="lenet",
        help="which network architecture to use")
    parser.add_argument("-d", '--dataset', type=str, default="EMNIST",
        help="which dataset to use")
    parser.add_argument("-e", '--epochs', type=int, default=10,
        help="Number of epochs")
    parser.add_argument("-b", '--batch_size', type=int, default=32,
        help="Batch size")        
    args = vars(parser.parse_args())

    return args


funcs = {'EMNIST': EMNIST, 'lenet': lenet, 'Character_Model': Character_Model}


def train(args, use_comet : bool = True):

    data_cls = funcs[args['dataset']]
    model = funcs[args['model']]
    network = funcs[args['network']]

    print ('[INFO] Getting dataset...')
    data = data_cls()
    (x_train, y_train), (x_test, y_test) = data.load_data()
    
    #Used for testing only
    x_train = x_train[:100, :, :]
    y_train = y_train[:100, :]
    x_test = x_test[:100, :, :]
    y_test = y_test[:100, :]
    print ('[INFO] Training shape: ', x_train.shape, y_train.shape)
    print ('[INFO] Test shape: ', x_test.shape, y_test.shape)
    #delete these lines

    # add this stratify=y_train after verifying distribution of classes 
    (x_train, x_valid, y_train, y_valid) = train_test_split(x_train, y_train, test_size=0.2,
                                                 random_state=42)

    print ('[INFO] Training shape: ', x_train.shape, y_train.shape)
    print ('[INFO] Validation shape: ', x_valid.shape, y_valid.shape)
    print ('[INFO] Test shape: ', x_test.shape, y_test.shape)

    print ('[INFO] Setting up the model..')
    Model = model(network, data_cls)
    print (Model)
    
    dataset = dict({
        'x_train' : x_train,
        'y_train' : y_train,
        'x_valid' : x_valid,
        'y_valid' : y_valid,
        'x_test' : x_test,
        'y_test' : y_test
    })

    if use_comet:
        #create an experiment with your api key
        experiment = Experiment(api_key='WVBNRAfMLCBWslJAAsffxM4Gz',
                                project_name='emnist',
                                auto_param_logging=False)

    print ('[INFO] Starting Training...')
    #will log metrics with the prefix 'train_'   
    with experiment.train():
        train_model(
            Model,
            dataset,
            batch_size=args['batch_size'],
            epochs=args['epochs']
            )

    print ('[INFO] Starting Testing...')    
    #will log metrics with the prefix 'test_'
    with experiment.test():  
        loss, score = Model.evaluate(dataset)
        print(f'[INFO] Test evaluation: {score}')
        metrics = {
            'loss':loss,
            'accuracy':score
        }
        experiment.log_metrics(metrics)    

    if args['weights']:
        Model.save_weights()

    experiment.log_parameters(args)
    experiment.log_dataset_hash(x_train) #creates and logs a hash of your data  
    

def main():
    """Run experiment."""
    args = _parse_args()
    train(args)

if __name__ == '__main__':
    main()