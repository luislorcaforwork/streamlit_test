from calculator import calculator
from gemini_app import gemini_app

if __name__ == '__main__':
    gemini_app()

# we need you to create a python langue based programe that uses the streamlit library for its UI. we only require the raw code itself, you dont have to do anything with streamlit or github.
#
# step by step process on how it should work
# 1. it will download every file in a specific folder in google drive which is named "Descargas"
# 2. it will check if its a PDF file, if it is one then it will be read by the programme
# 3. the PDF can usually have a unique structure, the programe has to extract specific data from each file, the data will be  chosen with the help of regular expressions, he already have a json file with patterns in it, i will attach the file it is called "patterns.json" , the programme will have to figure out which
