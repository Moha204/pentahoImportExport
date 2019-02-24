# BI Dashbards Repository Export

This Repository holds all the pentaho dashboards for BI. There are
2 python scripts to make easier import / export data to Pentaho servers. 
These scripts are found on the **scripts**/ folder.

## Config File.
The config file is a basic ini file with **KEY=VALUE** organized in blocks (environments).
Here is an example of config file.
```
[TEST]
username: YOUR_USER
password: YOUR_PASSWORD
url: http://localhost.com
remote_path: REMOTE_PENTAHO_PATH
local_path: LOCAL_PATH
backup_path: BACKUP_PATH
```

You can have as many environments as you need, (test, pre, prod, etc) with their different configs.

## download_bi_repository.py
This script downloads all the data from the specified pentaho
server to our local dashboard directory. **THIS WILL DELETE ALL
THE DATA IN THE DASHBOARD FOLDER SO TAKE CARE BEFORE USING IT AND
CHECK IF YOU HAVE PENDING CHANGES.** Before overwritting
everything, we will save a backup on ***backup_path*** so you can
recover your previous data in case of disaster.

### Example
```
./download_bi_repository.py -c config.ini -e PRE
```

## upload_bi_repository.py
This scripts uploads all the data in your dashboard folder 
to the selected pentaho server. This will overwrite the already
existing files on the server path. Before uploading anything, 
the script will download a backup of the server path on the
*backup_path*, so everything should be recoverable if something
goes wrong

### Example
```
./upload_bi_repository.py -c config.ini -e TEST
```

### Prerequisites
Need this 
`pip install requests` or `easy_install requests`.
