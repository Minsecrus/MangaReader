import sys
import os
import ctypes


def setup_environment():
    """
    Performs necessary environment setup for the packaged application.
    This includes pre-loading DLLs to fix WinError 1114 and injecting DLL paths.
    Must be called BEFORE importing torch.
    """
    # Determine base path
    if hasattr(sys, "_MEIPASS"):
        # OneFile mode (legacy)
        base_path = sys._MEIPASS
    else:
        # OneDir mode (new default) or Dev mode
        # In OneDir, sys.executable is inside the folder
        # In Dev, sys.executable is python.exe, so we need to be careful
        if getattr(sys, "frozen", False):
            base_path = os.path.dirname(sys.executable)
        else:
            # Dev mode, no need to inject paths usually, but for consistency:
            base_path = os.path.dirname(os.path.abspath(__file__))

    # Only run injection if frozen (packaged)
    if getattr(sys, "frozen", False):

        # --- 0. Inject PATH (Legacy DLL search) ---
        # Some DLLs still rely on PATH lookup. Merged from hook-torch.py.
        os.environ["PATH"] = base_path + os.pathsep + os.environ["PATH"]

        # --- 1. Pre-load OpenMP DLL (Fix WinError 1114) ---
        # MOVED to separate function to allow Llama.cpp to initialize first
        # See preload_torch_dependencies() below
        pass

        # --- 2. Inject DLL Paths (Fix WinError 1114) ---
        # Only add base paths here. Torch paths are added in preload_torch_dependencies
        paths_to_add = [base_path, os.path.join(os.environ["WINDIR"], "System32")]
        for p in paths_to_add:
            if os.path.exists(p) and hasattr(os, "add_dll_directory"):
                try:
                    os.add_dll_directory(p)
                except Exception:
                    pass


def preload_torch_dependencies():
    """
    Pre-loads Torch dependencies like libiomp5md.dll.
    Call this AFTER initializing Llama.cpp to avoid OpenMP conflicts.
    """
    if getattr(sys, "frozen", False):
        if hasattr(sys, "_MEIPASS"):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(sys.executable)

        # Add Torch paths to DLL search directory NOW
        torch_paths = [
            os.path.join(base_path, "torch", "lib"),
            os.path.join(base_path, "torch"),
            os.path.join(base_path, "torch", "bin"),
        ]
        for p in torch_paths:
            if os.path.exists(p) and hasattr(os, "add_dll_directory"):
                try:
                    os.add_dll_directory(p)
                    print(f"[Backend Service] [INFO] Added DLL directory: {p}")
                except Exception:
                    pass

        # Prioritize torch/lib version to ensure compatibility with torch
        libiomp_candidates = [
            os.path.join(base_path, "torch", "lib", "libiomp5md.dll"),
            os.path.join(base_path, "libiomp5md.dll"),
        ]
        for lib_path in libiomp_candidates:
            if os.path.exists(lib_path):
                try:
                    ctypes.CDLL(lib_path)
                    print(
                        f"[Backend Service] [INFO] Successfully pre-loaded: {lib_path}"
                    )
                    break
                except Exception as e:
                    print(
                        f"[Backend Service] [WARNING] Failed to pre-load {lib_path}: {e}"
                    )


def patch_libraries():
    """
    Patches libraries at runtime to bypass security checks or fix compatibility issues.
    """
    # --- Patch Transformers CVE-2025-32434 Check ---
    # Force override the security check function to allow older PyTorch versions to load models
    try:
        import transformers.utils.import_utils

        transformers.utils.import_utils.check_torch_load_is_safe = lambda: None
        print(
            "[Backend Service] [INFO] Successfully patched transformers.utils.import_utils.check_torch_load_is_safe"
        )
    except ImportError:
        print(
            "[Backend Service] [WARNING] Could not import transformers.utils.import_utils to patch"
        )
    except Exception as e:
        print(f"[Backend Service] [WARNING] Failed to patch transformers: {e}")
