#pragma once

#include <string>
#include <iostream>
#include <comdef.h>


// ------------------------------------------------------------------------------
// Конвертация строк
// ------------------------------------------------------------------------------
namespace strUtils {
    inline std::wstring bstrToWStr(const _bstr_t& bstr) {
        return std::wstring(static_cast<const wchar_t*>(bstr));
    }

    inline _bstr_t wstrToBstr(const std::wstring& wstr) {
        return _bstr_t(wstr.c_str());
    }
}


// ------------------------------------------------------------------------------
// Вывод сообщений в консоль с поддержкой Unicode символов
// ------------------------------------------------------------------------------
namespace consoleUtils {
    inline void printMessage(const std::wstring& msg) {
        DWORD written;
        WriteConsoleW(GetStdHandle(STD_OUTPUT_HANDLE),
            msg.c_str(),
            (DWORD)msg.size(),
            &written,
            nullptr);
    }

    inline void printError(const std::wstring& msg) {
        std::wstring text = L"[ERROR] " + msg;

        DWORD written;
        WriteConsoleW(GetStdHandle(STD_ERROR_HANDLE),
            text.c_str(),
            (DWORD)text.size(),
            &written,
            nullptr);
    }
}