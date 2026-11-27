import os 

base_folder = "/home/htthanh/Downloads/server/busnet-master-original/myPy/log_20250923_run_16"
# get all files in the base_folder
files = os.listdir(base_folder)
# get all files in the base_folder that are not in the subfolders
files = [f for f in files if os.path.isfile(os.path.join(base_folder, f))]
# get all files in the base_folder that are not in the subfolders

files = os.listdir(base_folder)
files = sorted([f for f in files if os.path.isfile(os.path.join(base_folder, f)) and f.startswith("log_")])
with open(os.path.join(base_folder, "summary_16.txt"), "w") as out_file:
    for f in files:
        with open(os.path.join(base_folder, f), "r") as in_file:
            start_cmds = []
            end_cmds = []
            routes = ""
            for line in in_file:
                if "routes to process: " in line:
                    routes = line.split("routes to process: ")[1]
                if "calcBetwCentralMultip part" in line:
                    start_cmds.append(line)
                if "part" in line and "written" in line:
                    end_cmds.append(line)
            if len(start_cmds) == len(end_cmds):
                out_file.write(f"{f}: FULLY COMPLETED\n")
            else:
                out_file.write(f"{f}: INCOMPLETE => {len(start_cmds)} / {len(end_cmds)} => {routes}\n")
print("Done")