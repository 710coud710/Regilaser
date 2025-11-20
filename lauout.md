

myapp/
├─ main.py                  # Khởi tạo app
├─ gui/
│   └─ main_window.py       # View
├─ model/                   # Xử lý dữ liệu, logic nghiệp vụ
│   ├─ com_model.py         # Logic COM + state
│   └─ tcp_model.py         # Logic TCP + state
├─ presenter/               # hoặc viewmodel/
│   └─ main_presenter.py    # Điều phối View <-> Model, quản lý thread
└─ workers/                 # Xử lý nặng: COM port, API, thread, crawl…
    ├─ com_worker.py
    └─ tcp_worker.py
