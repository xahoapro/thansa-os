' CẦU NỐI cho máy Windows cài TRƯỚC Thansa 1.19 - KHÔNG sửa, KHÔNG xoá.
' Updater của bản cũ (đang chạy trong bộ nhớ lúc bấm Cập nhật) và shortcut "JAVIS OS" trong thư mục
' Startup gọi đích danh file này. File thật nay là start-thansa.vbs. Bản cài mới không thấy file
' này (installer giấu bằng git skip-worktree).
Set fso = CreateObject("Scripting.FileSystemObject")
CreateObject("WScript.Shell").Run "wscript.exe //nologo """ & fso.BuildPath(fso.GetParentFolderName(WScript.ScriptFullName), "start-thansa.vbs") & """", 0, False
