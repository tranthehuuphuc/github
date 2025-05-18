// Injector.cpp : This file contains the 'main' function. Program execution begins and ends there.
// This program injects a DLL into a target process (EMPIRESX.EXE) to modify its memory.

#include <Windows.h>
#include <TlHelp32.h>
#include <iostream>
#include <fstream>
#include <strsafe.h>
#include <tchar.h>

// Get the process ID of the target application by its executable name
int getProcId(const wchar_t* procName) {
    DWORD pID = 0;
    PROCESSENTRY32 pe32;
    pe32.dwSize = sizeof(PROCESSENTRY32);
    // Take a snapshot of all running processes
    HANDLE hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    do {
        // Compare process name with target name
        if (wcscmp(pe32.szExeFile, procName) == 0) {
            CloseHandle(hSnapshot);
            pID = pe32.th32ParentProcessID; // Get parent process ID
            break;
        }
    } while (Process32Next(hSnapshot, &pe32)); // Iterate through all processes
    CloseHandle(hSnapshot);
    return pID;
}

// Check if a file exists on the disk
inline bool exist(const std::string& name)
{
    std::ifstream file(name);
    if (!file)            // If the file was not found
        return false;    // Return false
    else                 // If the file was found
        return true;     // Return true
}

// Display error message for the last system error and exit
void ErrorExit(const wchar_t* lpszFunction)
{
    LPVOID lpMsgBuf;
    LPVOID lpDisplayBuf;
    DWORD dw = GetLastError(); // Get the last error code

    // Format the error message
    FormatMessage(
        FORMAT_MESSAGE_ALLOCATE_BUFFER |
        FORMAT_MESSAGE_FROM_SYSTEM |
        FORMAT_MESSAGE_IGNORE_INSERTS,
        NULL,
        dw,
        MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
        (LPTSTR)&lpMsgBuf,
        0, NULL);

    // Prepare display buffer for error message
    lpDisplayBuf = (LPVOID)LocalAlloc(LMEM_ZEROINIT,
        (lstrlen((LPCTSTR)lpMsgBuf) + lstrlen((LPCTSTR)lpszFunction) + 40) * sizeof(TCHAR));
    StringCchPrintf((LPTSTR)lpDisplayBuf,
        LocalSize(lpDisplayBuf) / sizeof(TCHAR),
        TEXT("%s failed with error %d: %s"),
        lpszFunction, dw, lpMsgBuf);
    MessageBox(NULL, (LPCTSTR)lpDisplayBuf, TEXT("Error"), MB_OK); // Show error message box

    // Clean up and exit
    LocalFree(lpMsgBuf);
    LocalFree(lpDisplayBuf);
    ExitProcess(dw);
}

int main()
{
    HANDLE hProcess; // Handle to the target process
    LPVOID pszLibFileRemote = NULL; // Pointer to allocated memory in target process
    HANDLE handleThread; // Handle to the remote thread
    const wchar_t* process = L"EMPIRESX.EXE"; // Target process name
    int pID = getProcId(process); // Get process ID of target

    std::cout << "debuginfo: pID: " << pID << std::endl; // Log process ID

    char dll[] = "AOEResourceHack.dll"; // Name of the DLL to inject
    if (!exist(dll)) { // Check if DLL file exists
        std::cout << "debuginfo: Invalid DLL path!" << std::endl;
    }
    char dllPath[MAX_PATH] = { 0 }; // Buffer for full DLL path
    GetFullPathNameA(dll, MAX_PATH, dllPath, NULL); // Get absolute path of DLL
    std::cout << "debuginfo: Full DLL path: " << dllPath << std::endl; // Log DLL path

    // Open the target process with required permissions
    hProcess = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_CREATE_THREAD | PROCESS_VM_OPERATION | PROCESS_VM_WRITE, 0, pID);

    if (hProcess) {
        // Allocate memory in the target process for the DLL path
        pszLibFileRemote = VirtualAllocEx(hProcess, NULL, strlen(dllPath) + 1, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    }
    else {
        std::cout << "error: Could not open process handle with id:" << pID << std::endl; // Log error
    }

    if (pszLibFileRemote == NULL) std::cout << "error: Cannot allocate memory" << std::endl; // Log memory allocation failure

    // Write the DLL path into the target process's memory
    int isWriteOK = WriteProcessMemory(hProcess, pszLibFileRemote, dllPath, strlen(dllPath) + 1, NULL);
    if (!isWriteOK) std::cout << "error: Failed to write" << std::endl; // Log write failure

    // Create a remote thread to load the DLL using LoadLibraryA
    handleThread = CreateRemoteThread(hProcess, NULL, NULL, (LPTHREAD_START_ROUTINE)LoadLibraryA, pszLibFileRemote, NULL, NULL);
    if (handleThread == NULL) {
        std::cout << "error: Failed to create thread" << std::endl; // Log thread creation failure
        ErrorExit(_T("CreateRemoteThread")); // Show error and exit
    }

    // Wait for the remote thread to complete
    WaitForSingleObject(handleThread, INFINITE);
    CloseHandle(handleThread); // Clean up thread handle
    VirtualFreeEx(hProcess, dllPath, 0, MEM_RELEASE); // Free allocated memory
    CloseHandle(hProcess); // Close process handle

    return 0;
}
