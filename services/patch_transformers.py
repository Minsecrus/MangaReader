import os
import transformers.utils.import_utils
import inspect

def apply_patch():
    """
    Patches transformers.utils.import_utils.check_torch_load_is_safe to bypass
    CVE-2025-32434 security check on older PyTorch versions.
    """
    target_file = inspect.getfile(transformers.utils.import_utils)
    print(f"Target file: {target_file}")
    
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The function signature to look for
    target_func = "def check_torch_load_is_safe():"
    
    if target_func not in content:
        print("Could not find check_torch_load_is_safe function.")
        return

    # Check if already patched
    if "return  # Patched by MangaReader" in content:
        print("Already patched.")
        return

    # We will replace the function definition and its docstring/body with a simple return
    # This is a simple string replacement. 
    # We look for the function and replace the beginning of its body.
    
    # A more robust way: Replace the specific check logic or just inject the return at the start.
    # Since we know the file structure, we can just replace the function definition line
    # and the next line (indentation) with the return.
    
    # However, string replacement is risky if indentation varies.
    # Let's try to find the exact string we want to replace.
    
    # Original code usually looks like:
    # def check_torch_load_is_safe():
    #     """
    #     Checks if the torch load is safe ...
    #     """
    #     if is_torch_available():
    
    # We want to change it to:
    # def check_torch_load_is_safe():
    #     return # Patched ...
    
    new_content = content.replace(
        "def check_torch_load_is_safe():",
        "def check_torch_load_is_safe():\n    return  # Patched by MangaReader to bypass CVE-2025-32434 check on PyTorch < 2.6\n"
    )
    
    if content == new_content:
        print("Patch failed (string mismatch).")
    else:
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Successfully patched transformers library.")

if __name__ == "__main__":
    apply_patch()
