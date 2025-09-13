

# Khởi tạo lại repo git mới
git init

# Thêm remote origin trỏ đến GitHub
git remote add origin https://github.com/hoackdl/truck_tamanh.git

# Thêm toàn bộ file
git add .

# Commit lần đầu
git commit -m "Initial commit"

# Đẩy code lên GitHub (nhánh main)
git branch -M main
git push -u origin main -f

# Xoá toàn bộ thông tin git cũ
Remove-Item -Recurse -Force .git

# Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
# .\reset_git.ps1