' CẦU NỐI cho máy Windows cài TRƯỚC Thansa 1.19 - KHÔNG sửa, KHÔNG xoá.
' Updater của bản cũ (đang chạy trong bộ nhớ lúc bấm Cập nhật) và shortcut "JAVIS OS" trong thư mục
' Startup gọi đích danh file này. File thật nay là start-thansa.vbs. Bản cài mới không thấy file
' này (installer giấu bằng git skip-worktree). Đối số (/open, 0.306.0) chuyển nguyên sang file thật.
Set fso = CreateObject("Scripting.FileSystemObject")
args = ""
For Each a In WScript.Arguments
  args = args & " " & a
Next
CreateObject("WScript.Shell").Run "wscript.exe //nologo """ & fso.BuildPath(fso.GetParentFolderName(WScript.ScriptFullName), "start-thansa.vbs") & """" & args, 0, False
