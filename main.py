import json
import sys
import traceback
from utils.mclient import MinioClient
from pyjedai_utils import *
from blocking_based import get_BlockingBasedWorkflow
import time 
from pyjedai_utils import *
from blocking_based import get_BlockingBasedWorkflow
import os
from pyjedai.schema.schema_model import Schema
from pyjedai.datamodel import SchemaData
from pyjedai.schema.matching import ValentineSchemaMatching, ValentineMethodBuilder
from val_utils import *
from time import perf_counter
# Here you may define the imports your tool needs...
# import pandas as pd
# import numpy as np
# ...



# def prep_df(input_file, separator, engine, minio):
#     """
#     Prepare DataFrame from input file.
#     """
#     if input_file.startswith('s3://'):
#         bucket, key = input_file.replace('s3://', '').split('/', 1)
#         client = Minio(minio['endpoint_url'], access_key=minio['id'], secret_key=minio['key'])
#         df = pd.read_csv(client.get_object(bucket, key), sep=separator, na_filter=False)
#     else:
#         df = pd.read_csv(input_file, sep=separator, na_filter=False)
#     return df

            
        
    
    
    

def run(json_input):

    """
        This is the core method that initiates tool .py files execution. 
        It can be as large and complex as the tools needs. In this file you may import, call,
        and define any lib, method, variable or function you need for you tool execution.
        Any specific files you need can be in the same directory with this main.py or in subdirs
        with appropriate import statements with respect to dir structure.

        Any logic you implement here is going to be copied inside your tool image when 
        you build it using docker build or the provided Makefile.
        
            The MinIO initialization that is given down below is an example you may use it or not.
            MinIO access credentials are in the form of <ACCESS ID, ACCESS KEY, SESSION TOKEN>
            and are generated upon the OAuth 2.0 token of the user executing the tool. 

            For development purpose you may define your own credentials for your local MinIO 
            instance by commenting the MinIO init part.

    """

    try:
        """
        Init a MinIO Client using the custom STELAR MinIO util file.

        We access the MinIO credentials from the JSON field named 'minio' which 
        was acquired along the tool parameters.

        This credentials can be used for tool specific access too wherever needed
        inside this main.py file.

        """
        ################################## MINIO INIT #################################
        minio_id = json_input['minio']['id']
        minio_key = json_input['minio']['key']
        minio_skey = json_input['minio']['skey']
        minio_endpoint = json_input['minio']['endpoint_url']

        if 'https://' in minio_endpoint:
            minio_endpoint = minio_endpoint.replace('https://', '')
        
        mc = MinioClient(access_key=minio_id, secret_key= minio_key, session_token=minio_skey, endpoint=minio_endpoint)

        # It is strongly suggested to use the get_object and put_object methods of the MinioClient
        # as they handle input paths provided by STELAR API appropriately. (S3 like paths)
        ###############################################################################



        if not os.path.exists(".local"):
            os.mkdir(".local")
            
            
        """ 
        JSON ARCHITECTURE
        
        
        {
            "input": {
                "dataset_1" : {
                    "csv_path" : ,
                    "separator" : ,
                    "id_column_name" : ,

                    (optional)
                    "name" : ,
                    "attributes" : 
                    
                },
                (optional)
                "dataset_2" : {
                    "csv_path" : ,
                    "separator" : ,
                    "id_column_name" : ,
                    
                    (optional)
                    "name" : ,
                    "attributes" : 
                }
                (optional)
                "ground_truth" : {
                    "csv_path" : ,
                    "separator" : ,
                }                
                
            },
            "parameters": {
                "workflow": "BlockingBasedWorkflow" / "EmbeddingsNNWorkflow",
                "block_building" : {
                    "method": "StandardBlocking", 
                    "params" : {},
                    "attributes_1": ,
                    attributes_2"
                }
                "block_filtering" : []
                "comparison_cleaning": {}
                "entity_matching": {}
                "clustering": {}
                                    
                    
                
                
            }
            
            
            
        }
        
        
        
        
        """


        """
        Acquire tool specific parameters from json['parameters] which was given by the 
        KLMS Data API during the creation of the Tool Execution Task.

        An example of parameters for a tool that adds two numbers x,y could be:
        {
            "inputs": {
                "any_name": [
                    "XXXXXXXX-bucket/temp1.csv",
                    "XXXXXXXX-bucket/temp2.csv"
                ],
                "temp_files": [
                    "XXXXXXXX-bucket/intermediate.json"
                ]
                
            },
            "outputs": {
                "correlations_file": "/path/to/write/the/file",
                "log_file": "/path/to/write/the/file"
            },
            "parameters": {
                "x": 5,
                "y": 2,
            },
            "secrets": {
                "api_key": "AKIASIOSFODNNEXAMPLE"
            },
            "minio": {
                "endpoint_url": "minio.XXXXXX.gr",
                "id": "XXXXXXXX",
                "key": "XXXXXXXX",
                "skey": "XXXXXXXX",
            }

        }

        The parameters JSON field can be as large as the tool needs.

        For our simple example in this main.py we would access x,y as:
            x = json['parameters']['x']
            y = json['parameters']['y']
        """        
        metrics_dict = {}
        
        input = json_input['input'] if 'input' in json_input else json_input['inputs']
        params = json_input['parameters']
        
        for key in ['dataset_1', 'dataset_2', "ground_truth"]:
            if key not in input and key in params:
                del params[key]
                
        
       
        
        if params["workflow"] != "ValentineWorkflow":  
            data : Schema = load_input(mc = mc, input=input, parameters=params)
            if params["workflow"] == "BlockingBasedWorkflow":
                workflow = get_BlockingBasedWorkflow(data, params)
            elif params["workflow"] == "EmbeddingsNNWorkflow": 
                params = load_embeddings(mc, input, params) 
                workflow = get_EmbeddingsNNWorkFlow(data,params)
            elif params["workflow"] == "JoinWorkflow": 
                workflow = get_JoinWorkflow(data, params)    
            

            workflow.run(data, verbose=True, workflow_step_tqdm_disable=False)
            execution_time = workflow.workflow_exec_time


            # Handle Output
            pairs_df = workflow.export_pairs()
            metrics_df = workflow.to_df()
            number_of_pairs = pairs_df.shape[0] if not pairs_df.empty else 0
            
            
            if not pairs_df.empty: 
                merged1 = pd.merge(data.dataset_1,
                    pairs_df, left_on='id',
                    right_on='id1', how='left')
                d2 = data.dataset_2
                id2 = 'id' 
                # Step 2: Merge the result with df2 on mapping_df.id2 == df2.entity
                final_df = pd.merge(merged1, d2, left_on='id2', right_on=id2, how='left', suffixes=('_d1', '_d2'))
                # Optional: Drop unnecessary columns
                pairs_df = final_df.drop(columns=['id1', 'id2', 'id_d1', 'id_d2', 'data_d1', 'data_d2'])
                pairs_df.dropna(inplace=True)
            

            print(f"""
                \nPrinting Final Pairs : {workflow.final_pairs}
                \nPrinting Final Pairs: \n{pairs_df}
                """)
        
            
            if data.ground_truth is not None:
                metrics_dict['F1 %'], metrics_dict['Precision %'], metrics_dict['Recall %'] = workflow.get_final_scores()
        else:
            data : SchemaData = VAL_load_input(mc=mc,input=input, parameters=params)
            vmb = ValentineMethodBuilder
            methods_dict = {
                "Coma": vmb.coma_matcher,
                "Cupid": vmb.cupid_matcher,
                "DistributionBased": vmb.distribution_based_matcher,
                "JaccardDistanceMatcher": vmb.jaccard_distance_matcher,
                "SimilarityFlooding": vmb.similarity_flooding_mathcer
            }
            
            if "valentine_matching" in params:
                if "method" in params['valentine_matching']:
                    method = methods_dict[params['valentine_matching']['method']]
                    parameters = params['valentine_matching']['params']
                    sig = inspect.signature(method)
                    method_parameters = []    
                    #    Get the parameters
                    sig_dict = sig.parameters
                    for key in sig_dict:
                        method_parameters.append(key)
                    
                    
                    lista = list(parameters.keys())
                    for key in lista:
                        if key not in method_parameters:
                            del parameters[key]                        
                    
                    basematcher = method(**parameters)
    
                else: 
                    raise Exception("\"valentine_matching\": { \"method\" }was not provided")
            else: 
                raise Exception(f"\"valentine_matching\" was not provided")


            print(f"""
----- Starting {params['valentine_matching']['method']} ---- 
With parameters {json.dumps(params['valentine_matching']['params'], indent=4)} 
""")
            start_time = perf_counter()
            vsm = ValentineSchemaMatching(basematcher)
            top_columns = vsm.process(data)
            end_time = perf_counter()
            execution_time = end_time - start_time
            matches = vsm.matches
            
            
            pairs_list = []
            
            for pair in matches:
                pairs_list.append((pair[0][1], pair[1][1]))

            
            number_of_pairs = len(matches)
            
            metrics_dict
            if data.ground_truth: 
                metrics_dict = vsm.matches.get_metrics(data.ground_truth)
                        
            # Handle Output
            pairs_df = pd.DataFrame(pairs_list)
            metrics_df = pd.DataFrame([metrics_dict])
            number_of_pairs = pairs_df.shape[0] if not pairs_df.empty else 0
            

            print(f"""
                \nPrinting Final Pairs : {pairs_df}
                \nPrinting metrics Df : {metrics_df} 
                """)        
             
        
        metrics_dict['total_execution_time'] =  execution_time 
        metrics_dict['total_pairs'] =  number_of_pairs 

        
        
        print(f"""
            \nPrinting Final Metrics : {json.dumps(metrics_dict, indent=4)}
        
        """)
        
        outputs_dict = {}
        if 'output' or 'outputs' in json_input: 
            outputs = json_input['output'] if 'output' in json_input else json_input['outputs']
            
            if not os.path.exists(".local/output"):
                os.mkdir(".local/output")
            

            for key in outputs:
                output_path : str = None
                if key == 'metrics':
                    output_path = f'.local/output/{key}.csv'
                    metrics_df.to_csv(output_path, index=False)
                if key == 'pairs':
                    output_path = f'.local/output/pairs.csv'
                    pairs_df.to_csv(output_path, index=False)

                if output_path:
                    mc.put_object(file_path=output_path, s3_path=outputs[key])
                    outputs_dict[key] = outputs[key]         
        

        json_output = {
                'message': 'Tool Executed Succesfully',
                'metrics': metrics_dict,
                'status': "success",
        }

        json_output['output'] = outputs_dict
        
        
        


        """
            This json should contain any output of your tool that you consider valuable. Metrics field affects
            the metadata of the task execution. Status can be conventionally linked to HTTP status codes in order
            to mark success or error states.

            Output contains the resource ids from MinIO in which the valuable output data of your tool should be written
            An example of the output json is:

            {
                "message": "Tool executed successfully!",
                "outputs": {
                    "correlations_file": "XXXXXXXXX-bucket/2824af95-1467-4b0b-b12a-21eba4c3ac0f.csv",
                    "synopses_file": "XXXXXXXXX-bucket/21eba4c3ac0f.csv"			
                }
                "metrics": {	
                    "memory_allocated": "2048",
                    "peak_cpu_usage": "2.8"
                },
                "status": "success"
            }

        """

        return json_output
    except Exception as e:
        print(traceback.format_exc())
        return {
            'message': 'An error occurred during data processing.',
            'error': traceback.format_exc(),
            'status': 500
        }
    
if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise ValueError("Please provide 2 files.")
    with open(sys.argv[1]) as o:
        j = json.load(o)
    response = run(j)
    with open(sys.argv[2], 'w') as o:
        o.write(json.dumps(response, indent=4))
