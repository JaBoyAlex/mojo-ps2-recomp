// Independently authored bootstrap; contains no original or translated game code.
#ifndef UNICODE
#define UNICODE
#endif
#ifndef _UNICODE
#define _UNICODE
#endif
#include <windows.h>
#include <commdlg.h>
#include <string>
#include <vector>
#include <cstdio>

static std::wstring quote(const std::wstring& s) {
    std::wstring out=L"\""; unsigned slashes=0;
    for (wchar_t c:s) {
        if(c==L'\\') { ++slashes; continue; }
        out.append(slashes*(c==L'"'?2:1), L'\\'); slashes=0;
        if(c==L'"') out+=L'\\'; out+=c;
    }
    out.append(slashes*2,L'\\'); return out+L'"';
}
int wmain(int argc, wchar_t** argv) {
    // Kill build descendants if the launcher cancels setup or its timeout expires.
    HANDLE job=CreateJobObjectW(nullptr,nullptr);
    JOBOBJECT_EXTENDED_LIMIT_INFORMATION limits{};
    limits.BasicLimitInformation.LimitFlags=JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
    if(!job || !SetInformationJobObject(job,JobObjectExtendedLimitInformation,&limits,sizeof(limits)) || !AssignProcessToJobObject(job,GetCurrentProcess())) return 21;
    wchar_t module[32768]; GetModuleFileNameW(nullptr,module,32768);
    std::wstring root(module); root.resize(root.find_last_of(L"\\/"));
    std::wstring game; bool prepare=false,smoke=false,full=false;
    for(int i=1;i<argc;++i) {
        std::wstring a=argv[i];
        if(a==L"--game" && i+1<argc) game=argv[++i];
        else if(a==L"--prepare") prepare=true;
        else if(a==L"--smoke") smoke=true;
        else if(a==L"--fullscreen") full=true;
        else { puts("Usage: MOJO.exe [--game IMAGE] [--prepare] [--fullscreen] [--smoke]"); return 2; }
    }
    if(game.empty() && GetFileAttributesW((root+L"\\userdata\\disc.iso").c_str())==INVALID_FILE_ATTRIBUTES) {
        if(prepare) { puts("Supply --game with your MOJO! USA PS2 disc image."); return 20; }
        wchar_t file[32768]={}; OPENFILENAMEW o{}; o.lStructSize=sizeof(o);
        o.lpstrFilter=L"MOJO! USA PS2 disc image\0*.iso;*.cue;*.bin;*.chd\0All files\0*.*\0";
        o.lpstrFile=file; o.nMaxFile=32768; o.lpstrTitle=L"Select your MOJO! USA PS2 disc (SLUS_207.41, VER 1.02)";
        o.Flags=OFN_FILEMUSTEXIST|OFN_NOCHANGEDIR;
        if(!GetOpenFileNameW(&o)) return 20; game=file;
    }
    wchar_t sys[32768]; GetSystemDirectoryW(sys,32768);
    std::wstring exe=std::wstring(sys)+L"\\WindowsPowerShell\\v1.0\\powershell.exe";
    std::wstring cmd=quote(exe)+L" -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "+quote(root+L"\\builder\\bootstrap.ps1");
    if(!game.empty()) cmd+=L" -Game "+quote(game);
    if(prepare) cmd+=L" -Prepare"; if(smoke) cmd+=L" -Smoke"; if(full) cmd+=L" -Fullscreen";
    STARTUPINFOW si{}; si.cb=sizeof(si); PROCESS_INFORMATION pi{};
    si.dwFlags=STARTF_USESTDHANDLES; si.hStdInput=GetStdHandle(STD_INPUT_HANDLE); si.hStdOutput=GetStdHandle(STD_OUTPUT_HANDLE); si.hStdError=GetStdHandle(STD_ERROR_HANDLE);
    if(!CreateProcessW(exe.c_str(),cmd.data(),nullptr,nullptr,TRUE,0,nullptr,root.c_str(),&si,&pi)) return 21;
    WaitForSingleObject(pi.hProcess,INFINITE); DWORD code=21; GetExitCodeProcess(pi.hProcess,&code);
    CloseHandle(pi.hThread); CloseHandle(pi.hProcess); return static_cast<int>(code);
}
