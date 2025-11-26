`LM_INFO.csv` chính là bảng “thư viện cấu hình sản phẩm” của trạm laser, được tải và sử dụng ở hai chỗ:

1. **Khởi tạo Form lựa chọn sản phẩm (`Unit2.cpp`)**  
   - Ngay khi form `TForm2` dựng lên, chương trình lấy đường dẫn hiện tại và ghép thêm `LM_INFO.csv`. Nếu không tồn tại file này thì dừng hẳn ứng dụng.  
   - Toàn bộ nội dung file được nạp vào `TStringList`, lặp từ dòng thứ 2 trở đi (bỏ qua header) để bỏ vào `ComboBox1`. Mỗi item là cột 0 của từng dòng (tên sản phẩm).  
   
```15:33:Unit2.cpp
GetCurrentDirectory(MAX_PATH,gCurrentDir);
Form1->lm_infopath.printf("%s\\%s",AnsiString(gCurrentDir),"LM_INFO.csv");
if(!FileExists(Form1->lm_infopath)){
    ShowMessage("Can't found "+ Form1->lm_infopath);
    Application->Terminate();
}
TStringList *pstringlist_lminfo = new TStringList();
pstringlist_lminfo->LoadFromFile(Form1->lm_infopath);
for(int i =1;i<pstringlist_lminfo->Count;i++){
    this->ComboBox1->Items->Add(Form1->GetSubstringByFormat(
        pstringlist_lminfo->Strings[i],",",0));
}
```

   - Khi người dùng nhấn nút OK, giá trị đã chọn trong `ComboBox1` được ghi ngược lại vào `ALL_LM.tab` làm `Setup/ProductName`.  
```36:51:Unit2.cpp
Ftemp = this->ComboBox1->Text.Trim();
Form1->WriteIniValue("Setup","ProductName",Ftemp.c_str(),chrTabPath);
```

2. **Nạp cấu hình laser tương ứng trong `MainForm.cpp`**  
   - Sau khi Form chính lấy được `ProductName` từ `ALL_LM.tab`, nó mở lại `LM_INFO.csv`, tìm đúng dòng có cột 0 trùng với `ProductName`, rồi đọc các cột còn lại để cấu hình laser: mã chương trình (`HMX_LM_Script`), số panel, mode laser (`laser_modelname`), chế độ config (`laser_config`), tiền tố PSN (`psn_PRE`).  
   - Các giá trị này được đưa vào struct `laser_info` (khai báo trong `MainForm.h`) và dùng xuyên suốt: xác định script `GA,<script>`, số lượng block C2, số panel (`Panel_Num`), v.v.  

```581:605:MainForm.cpp
TStringList *pstringlist_lminfo = new  TStringList();
pstringlist_lminfo->LoadFromFile(lm_infopath);
for(int i =1;i<pstringlist_lminfo->Count;i++)
{
    laser_info.Product_Name = GetSubstringByFormat(pstringlist_lminfo->Strings[i],",",0).Trim();
    if(laser_info.Product_Name == AnsiString(Tab_ProductName))
    {
        laser_info.HMX_LM_Script = GetSubstringByFormat(pstringlist_lminfo->Strings[i],",",1);
        laser_info.str_Panel_Num = GetSubstringByFormat(pstringlist_lminfo->Strings[i],",",2);
        laser_info.laser_modelname = GetSubstringByFormat(pstringlist_lminfo->Strings[i],",",3);
        laser_info.laser_config = GetSubstringByFormat(pstringlist_lminfo->Strings[i],",",4);
        laser_info.psn_PRE = GetSubstringByFormat(pstringlist_lminfo->Strings[i],",",5);
        break;
    }
    ...
}
str_Panel_Num = laser_info.str_Panel_Num;
WriteIniValue("Setup","Panel_Num",str_Panel_Num.c_str(),chrTabPath);
```

**Tóm tắt nhiệm vụ của `LM_INFO.csv`:**
- Cung cấp danh sách ProductName để người vận hành chọn nhanh trên `Unit2`.
- Ánh xạ ProductName → thông số laser (script ID, số panel, loại máy, chế độ cấu hình, prefix PSN).  
Không có file này, ứng dụng sẽ thoát ngay vì không có dữ liệu cấu hình sản phẩm.

++++++++++++++++++++++++++++++++++++++++++

- Khi Form chính mở, chương trình đọc `LM_INFO.csv` để lấy `HMX_LM_Script`, `str_Panel_Num`, `laser_modelname`, `laser_config`, `psn_PRE` cho đúng ProductName (`MainForm.cpp`, đoạn 581‑604). Từ đó:
  - `HMX_LM_Script` → giá trị sau `GA,<script>` và `C2,<script>,…` trong lệnh gửi tới laser.
  - `str_Panel_Num` → số block/PSN cần đẩy vào lệnh `C2` và cũng được ghi lại vào `ALL_LM.tab`.
  - `psn_PRE` → tiền tố dùng kiểm tra PSN nhận từ SFIS.

- Cột `laser_config` điều khiển việc có cần “Config” riêng cho product hay không. Nếu `laser_config == "1"`, chương trình sẽ yêu cầu operator nhập `Config_temp` và lưu vào `General/Config`; giá trị này sau đó được đưa vào các tham số `C2` (nhánh code cũ thể hiện rõ việc chèn thêm block Config cho từng PSN) (`MainForm.cpp`, đoạn 614‑735 và 2765‑2782).

Vì vậy `LM_INFO.csv` không chỉ chọn tên sản phẩm hiển thị mà còn quyết định toàn bộ cấu hình và định dạng lệnh `GA`/`C2`/`NT` gửi cho laser: script ID nào, bao nhiêu PSN, có cần kèm Config riêng hay không.