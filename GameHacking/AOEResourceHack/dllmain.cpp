
// dllmain.cpp

#include "pch.h"
#include <Windows.h>
#include <TlHelp32.h>
#include <iostream>
#include <tchar.h> // _tcscmp
#include <vector>

// Get the base address of a module in a process by its name and process ID
DWORD GetModuleBaseAddress(TCHAR* lpszModuleName, DWORD pID) {
    DWORD dwModuleBaseAddress = 0;
    // Create a snapshot of all modules in the target process
    HANDLE hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE, pID);
    MODULEENTRY32 ModuleEntry32 = { 0 };
    ModuleEntry32.dwSize = sizeof(MODULEENTRY32);

    if (Module32First(hSnapshot, &ModuleEntry32)) // Get the first module
    {
        do {
            // Compare module name with target name
            if (_tcscmp(ModuleEntry32.szModule, lpszModuleName) == 0) {
                dwModuleBaseAddress = (DWORD)ModuleEntry32.modBaseAddr; // Store base address
                break;
            }
        } while (Module32Next(hSnapshot, &ModuleEntry32)); // Iterate through modules
    }
    CloseHandle(hSnapshot); // Clean up snapshot
    return dwModuleBaseAddress;
}

// Function to add resources (food) in the game by modifying memory
void AddFood()
{
    // Find the game window by its title
    HWND hGameWindow = FindWindow(NULL, L"Age of Empires Expansion");
    if (hGameWindow == NULL) {
        std::cout << "Start the game!" << std::endl; // Log if game is not running
    }

    DWORD pID = NULL; // Process ID of the game
    GetWindowThreadProcessId(hGameWindow, &pID); // Get process ID from window

    // Open the game process with full access
    HANDLE processHandle = NULL;
    processHandle = OpenProcess(PROCESS_ALL_ACCESS, FALSE, pID);
    if (processHandle == INVALID_HANDLE_VALUE || processHandle == NULL) {
        std::cout << "Failed to open process" << std::endl; // Log error
    }

    TCHAR gameName[13];
    wcscpy_s(gameName, 13, L"EMPIRESX.EXE"); // Name of the game executable
    DWORD gameBaseAddress = GetModuleBaseAddress(gameName, pID); // Get base address of game module

    DWORD offsetGameToBaseAdress = 0x003C4B18; // Base offset in game memory
    std::vector<DWORD> pointsOffsets{ 0x3c, 0x100, 0x50, 0x0 }; // Offsets to resource value

    DWORD baseAddress = NULL;
    // Read the base address from the game memory
    ReadProcessMemory(processHandle, (LPVOID)(gameBaseAddress + offsetGameToBaseAdress), &baseAddress, sizeof(baseAddress), NULL);
    
    DWORD pointsAddress = baseAddress;
    // Follow the pointer chain to find the resource address
    for (int i = 0; i < pointsOffsets.size() - 1; i++) {
        ReadProcessMemory(processHandle, (LPVOID)(pointsAddress + pointsOffsets.at(i)), &pointsAddress, sizeof(pointsAddress), NULL);
    }
    pointsAddress += pointsOffsets.at(pointsOffsets.size() - 1); // Add final offset

    float currentPoint = 0;
    // Read the current resource value
    ReadProcessMemory(processHandle, (LPVOID)(pointsAddress), &currentPoint, sizeof(currentPoint), NULL);

    float newPoints = currentPoint + 100; // Increase resource by 100
    // Write the new resource value back to memory
    WriteProcessMemory(processHandle, (LPVOID)(pointsAddress), &newPoints, 4, 0);
}

// Main thread function to monitor key presses and trigger resource addition
DWORD WINAPI MainThread(LPVOID param) {
    while (true) {
        // Check if F6 key is pressed
        if (GetAsyncKeyState(VK_F6) & 0x80000) {
            AddFood(); // Add resources when F6 is pressed
        }
        Sleep(100); // Pause to reduce CPU usage
    }
    return 0;
}

// DLL entry point, called when the DLL is loaded or unloaded
BOOL APIENTRY DllMain(HMODULE hModule,
    DWORD  ul_reason_for_call,
    LPVOID lpReserved
)
{
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH: // When DLL is injected
        MessageBoxA(NULL, "DLL Injected!", "DLL Injected!", MB_OK); // Show confirmation
        CreateThread(0, 0, MainThread, hModule, 0, 0); // Start main thread
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}
