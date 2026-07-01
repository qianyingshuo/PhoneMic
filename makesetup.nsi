Unicode true

!define APP_NAME "PhoneMic"
!define PUBLISHER "PhoneMic Team"
!define EXE_NAME "PhoneMic.exe"

!ifndef VERSION
  !define VERSION "0.0.0"
!endif
!ifndef BUILD_DATE
  !define BUILD_DATE "unknown"
!endif
!ifndef BUILD_COMMIT
  !define BUILD_COMMIT "unknown"
!endif

InstallDir "$PROGRAMFILES\${APP_NAME}"
!define SOURCE_DIR "build/phonemic_nuitka/PhoneMic.dist"

!ifndef BUILD_SUFFIX
  !define BUILD_SUFFIX "unknown"
!endif
OutFile "dist\${APP_NAME}_Setup_${BUILD_SUFFIX}.exe"

RequestExecutionLevel admin
LicenseData "NOTICE.txt"
Page license
Page directory
Page instfiles

Function .onInit
  # 1. 前置拦截：检测 PhoneMic 是否正在运行
  FindWindow $0 "" "PhoneMic"
  IntCmp $0 0 notRunning
    MessageBox MB_OK|MB_ICONSTOP "检测到 ${APP_NAME} 正在运行，请先关闭程序再进行安装。"
    Abort
  notRunning:

  # 2. 检测旧版本
  ReadRegStr $R0 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString"
  ReadRegStr $R1 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "InstallLocation"
  
  # 若未检测到旧版，直接继续安装
  StrCmp $R0 "" noOldVersion
  
  # 3. 弹窗提示确认卸载旧版本并升级
  MessageBox MB_YESNO|MB_ICONQUESTION "检测到系统已安装 ${APP_NAME} 的旧版本。$\n$\n是否先自动卸载旧版本以进行干净的升级安装？$\n（注意：这不会删除您的个人配置文件及按键映射）" IDYES proceedUninstall
    # 选择“否”，终止安装
    MessageBox MB_OK|MB_ICONINFORMATION "升级安装已取消。"
    Abort

  proceedUninstall:
    # 4. 校验旧版卸载文件 uninst.exe 是否存在
    StrCmp $R1 "" useDefaultDir
    Goto checkUninst
  useDefaultDir:
    StrCpy $R1 "$PROGRAMFILES\${APP_NAME}"

  checkUninst:
    IfFileExists "$R1\uninst.exe" runUninstaller
      # 卸载程序丢失，提示手动清理
      MessageBox MB_OK|MB_ICONSTOP "未找到旧版本的卸载程序（uninst.exe已丢失）。$\n$\n请先手动删除以下安装目录以清除旧版本，然后再重新运行安装：$\n$R1"
      Abort

  runUninstaller:
    # 5. 同步静默执行旧版本卸载
    ExecWait '"$R1\uninst.exe" /S _?=$R1' $R2
    
    # 6. 校验卸载结果
    IfFileExists "$R1\uninst.exe" uninstallFailed
      Goto noOldVersion

  uninstallFailed:
    MessageBox MB_OK|MB_ICONSTOP "旧版本卸载失败。请确保 PhoneMic 未在后台运行，或手动删除该目录后再试：$\n$R1"
    Abort

  noOldVersion:
FunctionEnd

Section
  SetShellVarContext all

  SetOutPath $INSTDIR
  File /r "${SOURCE_DIR}\*.*"
  WriteUninstaller "$INSTDIR\uninst.exe"

  CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${EXE_NAME}"
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${EXE_NAME}"
  CreateShortCut "$SMPROGRAMS\${APP_NAME}\Uninstall ${APP_NAME}.lnk" "$INSTDIR\uninst.exe"

  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" '"$INSTDIR\uninst.exe"'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayIcon" "$INSTDIR\${APP_NAME}.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "Publisher" "${PUBLISHER}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "BuildDate" "${BUILD_DATE}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "BuildCommit" "${BUILD_COMMIT}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "InstallLocation" "$INSTDIR"
SectionEnd

Function un.onInit
  # 卸载前检测进程是否正在运行，若在运行则提示用户关闭并中止卸载
  FindWindow $0 "" "PhoneMic"
  IntCmp $0 0 notRunning
    MessageBox MB_OK|MB_ICONEXCLAMATION "检测到 ${APP_NAME} 正在运行，请先关闭程序再进行卸载。"
    Abort
  notRunning:
FunctionEnd

Section Uninstall
  SetShellVarContext all

  # 安全校验：防止 $INSTDIR 被意外设置为空、盘符或敏感系统目录
  StrCmp $INSTDIR "" dir_error
  StrCmp $INSTDIR "C:\" dir_error
  StrCmp $INSTDIR "$PROGRAMFILES" dir_error
  Goto dir_ok

  dir_error:
    MessageBox MB_OK|MB_ICONSTOP "卸载路径异常，出于安全考虑已终止卸载。"
    Abort

  dir_ok:
    Delete "$INSTDIR\*.*"
    RMDir /r "$INSTDIR"
    Delete "$DESKTOP\${APP_NAME}.lnk"
    Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
    Delete "$SMPROGRAMS\${APP_NAME}\Uninstall ${APP_NAME}.lnk"
    RMDir "$SMPROGRAMS\${APP_NAME}"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
SectionEnd