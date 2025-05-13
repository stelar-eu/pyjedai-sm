from pyjedai.datamodel import SchemaData
from utils.mclient import MinioClient
import pandas as pd
from pyjedai_utils import check_dataset



# Check if input was correctly provided
def VAL_load_input(mc: MinioClient, input: dict, parameters: dict) -> SchemaData:
    if 'dataset_1' not in input:
        raise Exception("No dataset_1 was given")
    if 'dataset_2' not in input:
        raise Exception("No dataset_2 was given")
        
    data_dict = { 
        "dataset_name_1" : None,
        "dataset_name_2" : None,
        "ground_truth" : None,
    }
    

    for dataset in ['dataset_1', 'dataset_2', 'ground_truth']:
        if dataset in input and dataset not in parameters:
            raise Exception(f"Must provide required_keys in parameters for {dataset} : {required_keys[dataset]}")
        elif dataset in input and dataset in parameters: 
            
            check_dataset(parameters[dataset], dataset)
            
            if dataset=='ground_truth' and parameters['ground_truth']['is_json']: 
                mc.get_object(s3_path=input[dataset][0], local_path=f".local/{dataset}.json")
                df = pd.read_json(f".local/{dataset}.json")
            else:
                mc.get_object(s3_path=input[dataset][0], local_path=f".local/{dataset}.csv")
                df = pd.read_csv(f".local/{dataset}.csv", sep=parameters[dataset]["separator"], engine='python', na_filter=False)


            data_dict[dataset] = df.copy()
            
            if dataset != 'ground_truth': 
                for key in parameters[dataset]:
                    index = dataset.split('_', 1)[1]
                    data_dict_key = f'{key}_{index}'
                    if data_dict_key in data_dict and parameters[dataset][key]:
                        if key == 'attributes' and not isinstance(parameters[dataset]['attributes'],list): 
                            data_dict[data_dict_key] = list(parameters[dataset][key])
                        else: 
                            data_dict[data_dict_key] = parameters[dataset][key]
    
    data_dict[ "attributes_1"] = None
    data_dict[ "attributes_2"] = None
    
    offset = len(data_dict['dataset_1'].columns)
    end = len(data_dict['dataset_2'].columns) + offset
    if "matching_type" in parameters:
        match_type = parameters['matching_type'].upper()
        if match_type == 'SCHEMA': 
            for dataset in ['dataset_1', 'dataset_2']:
                data_dict[dataset] = pd.DataFrame(columns=data_dict[dataset].columns)
                data_dict[dataset].loc[0] = data_dict[dataset].columns
                data_dict[dataset] = data_dict[dataset].dropna(axis=1)
        elif match_type == 'CONTENT':
            if isinstance(data_dict['ground_truth'],pd.DataFrame):
                ground_truth = data_dict['ground_truth'].to_records(index=False).tolist()
                lista = list()
                for pair in ground_truth:
                    source_pair = data_dict['dataset_1'].columns.get_loc(pair[0])
                    target_pair = data_dict['dataset_2'].columns.get_loc(pair[1]) + offset
                    lista.append(source_pair, target_pair)
                data_dict['ground_truth'] = pd.DataFrame(lista)
            source_columns = range(offset)
            target_columns = range(offset, end + offset)
            data_dict['dataset_1'].columns = [str(x) for x in source_columns]
            data_dict['dataset_2'].columns = [str(x) for x in target_columns]

    return SchemaData(**data_dict)