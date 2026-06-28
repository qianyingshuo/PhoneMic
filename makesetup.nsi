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