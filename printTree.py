import os

"""
Type the following in cmd before running this script:
set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=utf-8
Then do "python printTree.py > tree.txt" to reroute the output to a file
"""

def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(indent + os.path.basename(root) + "/")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print(subindent + f)

try:
    list_files(os.getcwd())
except:
    print("There was an error with the characater encoding. Please paste the following in the command line:")
    print("set PYTHONIOENCODING=utf-8")
    print("set PYTHONLEGACYWINDOWSSTDIO=utf-8")
    print("This type of error is likely due to a non-English character present.")
