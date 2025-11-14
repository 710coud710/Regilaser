myapp/
├─ main.py               # Khởi tạo app
├─ gui/
│   └─ main_window.py    # View
├─ model/
│   ├─ com_model.py      # Logic COM + state
│   └─ tcp_model.py      # Logic TCP + state
├─ presenter/            # hoặc viewmodel/
│   └─ main_presenter.py # Điều phối View <-> Model, quản lý thread
└─ workers/
    ├─ com_worker.py
    └─ tcp_worker.py
