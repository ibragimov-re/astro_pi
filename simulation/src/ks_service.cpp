#include "pch.h"
#include "utils.h"
#include "ks_service.h"
#include <stdexcept>
#include <vector>
#include <comutil.h>


KompasAPI7::IApplicationPtr ksGetApp() {
    KompasAPI7::IApplicationPtr kompasApp;
    kompasApp.GetActiveObject(L"Kompas.Application.7");
    if (!kompasApp) {
        consoleUtils::printError(L"Failed to find running Kompas-3D instance\n");
        throw std::runtime_error("[KS-SERVICE] App not found");
    }

    std::wstring appName = strUtils::bstrToWStr(kompasApp->ApplicationName[true]);
    consoleUtils::printMessage(L"[OK] Connected to Application: " + appName + L'\n');

    return kompasApp;
}


KompasAPI7::IKompasDocument3DPtr ksGetActiveDocument3D(KompasAPI7::IApplicationPtr kompasApp) {
    KompasAPI7::IKompasDocument3DPtr doc3d = kompasApp->ActiveDocument;
    if (!doc3d) {
        consoleUtils::printError(L"Failed to get active Kompas-3D document\n");
        throw std::runtime_error("[KS-SERVICE] Document not found");
    }

    std::wstring docName = strUtils::bstrToWStr(doc3d->Name);
    consoleUtils::printMessage(L"[OK] Connected to active document: " + docName + L'\n');

    return doc3d;
}


KompasAPI7::IFeature7Ptr ksGetFeatureByNameInDoc3D(KompasAPI7::IKompasDocument3DPtr doc3d, const std::wstring& name) {
    KompasAPI7::IPart7Ptr topPart(doc3d->TopPart);
    if (!topPart) {
        consoleUtils::printError(L"Failed to find top part in Kompas-3D document\n");
        throw std::runtime_error("[KS-SERVICE] Top part not found");
    }

    KompasAPI7::IFeature7Ptr feature;

    if (topPart->Detail) {
        feature = topPart;
        if (strUtils::bstrToWStr(feature->Name) == name) {
            return feature;
        }
    }
    else {
        KompasAPI7::IParts7Ptr parts = topPart->Parts;
        KompasAPI7::IPart7Ptr part = parts->Part[strUtils::wstrToBstr(name)];
        if (part) {
            feature = part;
            return feature;
        }
    }

    consoleUtils::printError(L"Failed to find part in Kompas-3D document: " + name + L'\n');
    throw std::runtime_error("[KS-SERVICE] Feature not found");
}


std::vector<KompasAPI7::IBody7Ptr> ksGetFeatureBodies(KompasAPI7::IFeature7Ptr feature) {
    std::vector<KompasAPI7::IBody7Ptr> bodiesVec;

    _variant_t bodiesVar = feature->ResultBodies;

    if (bodiesVar.vt == VT_EMPTY || bodiesVar.vt == VT_NULL) {
        consoleUtils::printError(L"Failed to get feature bodies\n");
        throw std::runtime_error("[KS-SERVICE] Feature bodies not found");
    }

    // Если только одно тело
    if (bodiesVar.vt == VT_DISPATCH) {
        KompasAPI7::IBody7Ptr body(bodiesVar.pdispVal);
        if (body) bodiesVec.push_back(body);
    }

    // Если несколько тел
    else if (bodiesVar.vt == (VT_ARRAY | VT_DISPATCH)) {
        SAFEARRAY* psa = bodiesVar.parray;
        LONG lBound, uBound;
        SafeArrayGetLBound(psa, 1, &lBound);
        SafeArrayGetUBound(psa, 1, &uBound);

        for (LONG i = lBound; i <= uBound; ++i) {
            IDispatch* pDisp = nullptr;
            SafeArrayGetElement(psa, &i, &pDisp);
            KompasAPI7::IBody7Ptr body(pDisp);
            if (body) {
                bodiesVec.push_back(body);
            }
            if (pDisp) pDisp->Release();
        }
    }

    return bodiesVec;
}


void ksSetBodyColor(KompasAPI7::IBody7Ptr body, int r, int g, int b) {
    KompasAPI7::IColorParam7Ptr colorParam;
    colorParam = body;

    long rgb = (r & 0xFF) | ((g & 0xFF) << 8) | ((b & 0xFF) << 16);
    colorParam->Color = rgb;

    body->Update();
}


void ksUpdateAllBodiesColorInAssembly(KompasAPI7::IKompasDocument3DPtr doc3d) {
    // Для мгновенного обновления цвета тел в документе со сборкой используется способ обновления через
    // переключение отображения резьбы, тогда Компас-3D сразу отрисует новый заданный цвет для тел
    bool isThreadsHidden = doc3d->HideAllThreads;
    if (isThreadsHidden) {
        doc3d->HideAllThreads = true;
        doc3d->HideAllThreads = false;
    }
    else {
        doc3d->HideAllThreads = false;
        doc3d->HideAllThreads = true;
    }
}


bool ksIsDocAssembly(KompasAPI7::IKompasDocument3DPtr doc3d) {
    KompasAPI7::IKompasDocumentPtr doc = doc3d;
    KompasAPI7::DocumentTypeEnum docType;

    // Здесь используется прямой COM-вызов get_DocumentType(), так как свойство DocumentType
    // через обычное Automation-обращение вызывает конфликт компиляции
    doc->get_DocumentType(&docType);

    if (docType == KompasAPI7::DocumentTypeEnum(Kompas6Constants::ksDocumentAssembly)) {
        return true;
    }
    else return false;
}


void ksSetVariableExpressionInPart(KompasAPI7::IPart7Ptr part, std::wstring variableName, std::wstring expression) {
    KompasAPI7::IFeature7Ptr feature = part;

    _variant_t varName(variableName.c_str());
    VARIANT_BOOL isExternal = VARIANT_FALSE; // Не внешняя переменная
    VARIANT_BOOL isInSource = VARIANT_TRUE; // Переменная из источника

    KompasAPI7::IVariable7Ptr var = feature->GetVariable(isExternal, isInSource, varName);

    if (!var) {
        consoleUtils::printError(L"Failed to find variable in Kompas-3D part: " + variableName + L'\n');
        throw std::runtime_error("[KS-SERVICE] Variable not found");
    }

    var->Expression = strUtils::wstrToBstr(expression);
}


void ksRebuildDocument(KompasAPI7::IKompasDocument3DPtr doc3d) {
    doc3d->RebuildDocument();
}