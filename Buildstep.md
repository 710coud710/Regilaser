```Bash
python -m nuitka ^
  --standalone ^
  --onefile ^                     # hoặc bỏ --onefile nếu chấp nhận thư mục (nhẹ hơn ~5-10MB)
  --enable-plugin=pyside6 ^
  --windows-disable-console ^     # nếu là GUI, ẩn console
  --windows-icon-from-ico=icon.ico ^  # nếu có icon
  --assume-yes-for-downloads ^
  --clang ^                       # dùng clang thay gcc → exe nhỏ hơn ~10-20%
  --lto=yes ^                     # Link Time Optimization
  --prefer-source-code-distribution ^
  --include-data-files=resources/*=resources/* ^  # nếu có file tài nguyên
  --output-dir=dist ^
  main.py                         # thay bằng file chính của bạn

```

```Bash
python -m nuitka 
  --standalone 
  --onefile 
  --enable-plugin=pyside6 
  --windows-disable-console 
  --windows-icon-from-ico=icon.ico 
  --assume-yes-for-downloads 
  --clang                       
  --lto=yes 
  --prefer-source-code-distribution 
  --include-data-files=resources/*=resources/* 
  --output-dir=dist 
  main.py                         

```
