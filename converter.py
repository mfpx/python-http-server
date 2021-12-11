import yaml
import json
import os
import sys

# Converts old format config to new (json -> yaml)
def configConvert(jsonFile, yamlFile):
    conversionFlag = 0
    try:
        if not os.path.isfile(yamlFile):
            yamlConf = open(yamlFile, 'w')
            jsonConf = open(jsonFile, 'r')
            yaml.dump(json.load(jsonConf), yamlConf)

            if os.path.isfile(yamlFile):
                print("Conversion successful!")
                conversionFlag = 1
    except Exception as ex:
        print("Automatic conversion failed!")
        print(ex)
        try:
            os.remove(yamlFile)
        except:
            print("Failed to remove file following a conversion failure!\n \
            Please remove it manually before rerunning the converter")
    finally:
        if conversionFlag == 1:
            os._exit(0)  # conversion done, exit
        else:
            os._exit(1)  # conversion failed, exit


if __name__ == "__main__":
    try:
        configConvert(sys.argv[1], sys.argv[2])  # try arguments
    except:
        configConvert('conf.json', 'conf.yml')  # assume defaults
