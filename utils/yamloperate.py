import yaml
from sympy.codegen.cnodes import union

'''
# 写入YAML文件
data > id_cls_dict

'''
def write_yaml(file_path, data_dict: dict[str,str]):
    yaml_names_dict = dict()
    yaml_names_dict["names"] = data_dict
    with open(file_path, 'w') as file:
        yaml.dump(yaml_names_dict, file, allow_unicode=True)

def read_yaml(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    return data

def get_id_cls_dict(file_path):
    yaml_dict = read_yaml(file_path)
    return yaml_dict["names"]

    # indices_class_dict = dict((k, v) for k, v in yaml_dict["names"].items())
    # return indices_class_dict

