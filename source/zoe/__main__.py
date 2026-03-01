import sys
from zoe import ZoeMetadata

def main():
    args = sys.argv[1:]
    if "--version" in args or "-v" in args:
        print(f"Zoe Framework {ZoeMetadata.version()}")
        return

    print("Zoe Framework CLI")
    print("Usage: python -m zoe [options]")

if __name__ == "__main__":
    main()
