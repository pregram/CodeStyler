import argparse
import subprocess
import os
import sys

ERROR_CODE = 1

USE_DEFAULT = False

# prompts the user for every file overwrite
gdo_prompt = False
# overwrites the source files, if False a new
#  file is created with a "styled_" prefix 
gdo_overwrite = True

# mode for creating new directory
DIR_MODE = 0o755

# file extensions that are affected(styled).
#  Note that astyle supports:  C, C++, C++/CLI, Objective-C, C#
#  and Java programming languages.
ALLOWED_EXTENSIONS = [
    '.c', 
    '.cpp', 
    '.cxx', 
    '.h', 
    '.hpp'
]

NO_PERMISSION_ERROR_MSG =\
"\
Error: cannot create a file/directory: {} \
or access it's content.\n\
Please provide the necessary permissions.\
"
INVALID_PARENT_PATH_ERROR_MSG =\
"\
Error: parent path for path: {} doesn't exist.\
"

def main() -> int:
    # take as input the folder which you want to format cpp/h
    # files in it
    SUCCESS_MSG = "Successfully styled the given directory"
    PROGRAM_DESCRIPTION =\
"\
Format C, C++ files using astyle recursively \
over a directory(folder).\
"

    parser = argparse.ArgumentParser(description=PROGRAM_DESCRIPTION)
    parser.add_argument(
        "-s", 
        "--source", 
        nargs='?', 
        default='.', 
        const='.', 
        help="Source file or directory (default: current directory)"
    )
    parser.add_argument(
        "-d", 
        "--destination", 
        nargs='?', 
        help="Destination file or directory (default: overwrite source)"
    )

    args = parser.parse_args()
    source, destination = validate_command(
        args.source, 
        args.destination
    )
    # print(source, destination)
    recursive_styler(path=source, styled_path=destination)
    print(SUCCESS_MSG)
    return 0


# here you can pick your own formatting options based on astyle
# link: https://astyle.sourceforge.net/
def my_style(src_path : str, styled_path : str) -> None:
    # allman style places each of '{', '}' on a seperate line
    # java style places inner code on a seperate line from {}.
    styles = ["allman", "java"]
    _style = styles[0]
    
    ptr_alignments = ["type", "middle","name"]
    _ptr_align = ptr_alignments[0]
    PLACE_CLOSING_BRACE_ON_SEPERATE_LINE = True

    MAX_CONSECUTIVE_EMPTY_LINES = 2
    MAX_CHARACTER_IN_CODE = 80
    MODE = 'c'      # For C, C++ files

    command = ["astyle", 
               # options
               "--style=" + _style,
               "--indent-switches",
               "--indent-cases",
               "--indent-namespaces",
               "--indent-after-parens",
               "--indent-preproc-define",
               "--indent-col1-comments",
               "--pad-oper",
               "--pad-include",
               "--pad-header",
               "--unpad-brackets",
               "--squeeze-lines=" + str(MAX_CONSECUTIVE_EMPTY_LINES),
               "--squeeze-ws",
               "--align-pointer=" + _ptr_align,
               "--break-one-line-headers",
               "--add-braces",
               "--close-templates",
               "--max-code-length=" + str(MAX_CHARACTER_IN_CODE),
               "--mode=" + MODE,
               "--stdin=" + src_path,
               "--stdout=" + styled_path
            ]
    if PLACE_CLOSING_BRACE_ON_SEPERATE_LINE:
        command.append("--break-closing-braces")
    result = subprocess.run(command, capture_output=True, text=True)
    
    

def style_wrapper(src_path : str, styled_path : str) -> None:
    styled_name = prefix_filename(prefix="styled_", file_path=src_path)
    # if user provided a destination path, return. 
    if not are_same_path(styled_path, src_path):
        my_style(src_path, styled_path)
        return
    styled_path = styled_name
    my_style(src_path, styled_path)
    global gdo_overwrite
    if gdo_overwrite:
        copy_file(src=styled_path, dest=src_path)
        remove_file(path=styled_path)

def are_same_path(left : str, right : str) -> bool:
    return os.path.abspath(left) == os.path.abspath(right)

def prefix_filename(prefix : str, file_path : str) -> str:
    prefixed_name = prefix + os.path.basename(file_path)
    return os.path.join(os.path.dirname(file_path), prefixed_name)

def copy_file(src : str, dest : str) -> None:
    src_file = open(src, 'rb')
    with open(dest, 'wb') as dest_file:
        dest_file.write(src_file.read())
    src_file.close()

def remove_file(path : str) -> None:
    if os.path.isfile(path):
        os.unlink(path)

def did_user_accept(answer : str) -> bool:
    if len(answer) == 0:
        return False
    return answer.strip()[0] in ['Y', 'y']

# prompts the user that files will be overwritten 
# if gdo_prompt is False
def prompt_directory_overwrite(dir : str) -> None:
    global gdo_prompt, gdo_overwrite
    if gdo_prompt:
        return
    
    OVERWRITE_WARNING =\
"\
Warning: source file/directory: {}\t\
will be overwritten.\
"

    ASK_TO_NOT_OVERWRITE =\
"\
Do you want to overwrite file(s)? \
"
# if not then a copy is created\
# and styled instead\

    ASK_PROMPT_OVERWRITE =\
"\
Do you want to be prompted \
before every file overwrite? \
"
    print(OVERWRITE_WARNING.format(dir))
    response = input(ASK_TO_NOT_OVERWRITE)
    gdo_overwrite = did_user_accept(answer=response)
    if gdo_overwrite:
        response = input(ASK_PROMPT_OVERWRITE)
        gdo_prompt = did_user_accept(answer=response)
    else:
        gdo_prompt = gdo_overwrite
        

# returns True if astyle is installed False otherwise. 
def is_astyle_installed():
    try:
        subprocess.run(
            ["astyle", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return True
    except Exception:
        return False
    
def listdir_wrapper(dir_path : str) -> list[str]:
    global NO_PERMISSION_ERROR_MSG
    filenames = ''
    try:
        filenames = os.listdir(dir_path)
    except PermissionError:
        print(NO_PERMISSION_ERROR_MSG.format(dir_path), file=sys.stderr)
        sys.exit(ERROR_CODE)
    except OSError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(ERROR_CODE)
    return filenames

# creates directory if it doesn't exist,
# if it fails the program stops.
def mkdir_wrapper(dir_path : str) -> None:
    global DIR_MODE, NO_PERMISSION_ERROR_MSG
    global INVALID_PARENT_PATH_ERROR_MSG
    try:
        if not os.path.exists(dir_path):
            os.mkdir(path=dir_path, mode=DIR_MODE)
    except FileNotFoundError:
        print(INVALID_PARENT_PATH_ERROR_MSG.format(dir_path), file=sys.stderr)
        sys.exit(ERROR_CODE)
    except PermissionError:
        print(NO_PERMISSION_ERROR_MSG.format(dir_path), file=sys.stderr)
        sys.exit(ERROR_CODE)
    except OSError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(ERROR_CODE)

# returns True if ran script correctly and astyle is insatlled. 
def validate_command(source : str, dest : str) -> list[str]:

    ASTYLE_NOT_INSTALLED =\
"\
Error: astyle is not installed \
on your system.\t\
Please follow the instructions: \
https://astyle.sourceforge.net/\
"
    COULD_NOT_FIND_DIR =\
"\
Error: couldn't find a matching \
directory or file: {}\
"

    #  if destination wasn't specified
    #  update destination to match source
    if not dest:
        dest = source
    
    if not os.path.exists(source):
        print(COULD_NOT_FIND_DIR.format(source), file=sys.stderr)
        sys.exit(ERROR_CODE)
    
    # if it's not a regular file path then create directory 
    if os.path.splitext(dest)[1] == '':
        mkdir_wrapper(dest)
    if are_same_path(source, dest) and USE_DEFAULT:
        prompt_directory_overwrite(source)
    if not is_astyle_installed():
        print(ASTYLE_NOT_INSTALLED, file=sys.stderr)
        sys.exit(ERROR_CODE)

    return [source, dest]


# returns true if the provided file path is a C or C++ file or header  
def is_c_file(file_path : str) -> bool:
    global ALLOWED_EXTENSIONS
    file_extension = os.path.splitext(file_path)[1]
    return os.path.isfile(file_path) and \
        file_extension in ALLOWED_EXTENSIONS


def prompt_override(path : str) -> bool:
    answer = input(f"Do you want to overwrite {path} with style? ")
    return did_user_accept(answer=answer)

def recursive_styler(path: str = '.', styled_path : str = '.') -> None:
    global gdo_prompt
    if is_c_file(path):
        if gdo_prompt and path == styled_path and (not prompt_override(path)):
            return
        style_wrapper(src_path=path, styled_path=styled_path)
        return
    if os.path.isfile(path) and not are_same_path(path, styled_path):
        copy_file(src=path, dest=styled_path)
    
    if not os.path.isdir(path):
        return
    dir_path = path
    styled_dir_path = styled_path
    filenames = listdir_wrapper(dir_path)
    mkdir_wrapper(styled_dir_path)
    
    for filename in filenames:
        path = os.path.join(dir_path, filename)
        styled_path = os.path.join(styled_dir_path, filename)
        recursive_styler(path=path, styled_path=styled_path)


if __name__ == "__main__":
    main()
