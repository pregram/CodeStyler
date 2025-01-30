# CodeStyler

## C++, C formatting script
  **format.py** - a python script that uses [astyle](https://astyle.sourceforge.net/)
  in order to format your C++, C files and headers.
  Formatting options are defined in my_style function,
  you can easily modify the options to the ones you prefer. 
  Discover more options in [astyle docs](https://astyle.sourceforge.net/astyle.html).
  
  **Usage:** 
  ```
  python format.py -s source -d destination
  ```
  **source:** an ***optional*** argument, a single **file or directory**(folder)
  that you would like to format.
  By **default** the source is the **current directory**.

  **destination:** an ***optional*** argument, a single **file or directory**(folder)
  where you would like to store formatted file or directory.
  By **default** the destination is the **source file or directory**.

  **Notes:** 
  - [astyle](https://astyle.sourceforge.net/) should be installed on your system.
    
  - Ensure that astyle is added to PATH variable.
    
  - The script currently modifies only C++, C files and headers. You could modify that in
    the variable ALLOWED_EXTENSIONS.
  
  - When the destination is the same as source, you can either pick to overwrite existing files
    and / or be prompted before each overwrite. If you choose not to overwrite existing files,
    new file(s) will be created with `styled_` prefix within the same directory of that file.
  
  - When the destination is a directory different than source, then all new files are created
    in directories matching the source's structure.

  **TODO**
  - [x] Copy all files (that aren't formatted) from source directory to the destination directory.
  - [x] Create an option to use default `gdo_overwrite`, `gdo_prompt` without asking.

  
