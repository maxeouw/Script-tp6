import argparse
import subprocess
import re
import sys
import platform
import locale

def parse_traceroute_output(output):
    """Parse les adresses IP des sorties du traceroute."""
    ip_pattern = re.compile(r"(?:\d{1,3}\.){3}\d{1,3}")
    return ip_pattern.findall(output)

def run_traceroute(target, progressive, output_file):
    """Exécute le traceroute avec la gestion des exceptions."""
    try:
        is_windows = platform.system().lower() == "windows"
        encoding = locale.getpreferredencoding() if is_windows else "utf-8"
        command = ["tracert", target] if is_windows else ["traceroute", target]

        if progressive:
            process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, encoding=encoding
            )
            with open(output_file, "w") if output_file else sys.stdout as file:
                for line in iter(process.stdout.readline, ""):
                    line = line.strip()
                    if line:
                        ips = parse_traceroute_output(line)
                        for ip in ips:
                            print(ip)
                            file.write(ip + "\n")
            process.stdout.close()
            process.wait()
        else:
            result = subprocess.run(command, capture_output=True, text=True, encoding=encoding)
            if result.returncode == 0:
                ips = parse_traceroute_output(result.stdout)
                with open(output_file, "w") if output_file else sys.stdout as file:
                    for ip in ips:
                        print(ip)
                        file.write(ip + "\n")
            else:
                raise RuntimeError(f"Traceroute command failed: {result.stderr.strip()}")

    except FileNotFoundError:
        print("Error: The traceroute/tracert command is not available on your system.", file=sys.stderr)
    except PermissionError:
        print(f"Error: Permission denied while accessing the file '{output_file}'.", file=sys.stderr)
    except RuntimeError as e:
        print(f"Runtime error: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

def interactive_mode():
    """Mode interactif pour demander les options à l'utilisateur."""
    try:
        print("Welcome to the Traceroute Tool!")
        target = input("Enter the target URL or IP address: ").strip()
        while not target:
            print("Target cannot be empty.")
            target = input("Enter the target URL or IP address: ").strip()

        progressive = input("Enable progressive mode? (yes/no) [no]: ").strip().lower()
        progressive = progressive == "yes"

        output_file = input("Enter the output file name (or leave empty for no file): ").strip()
        output_file = output_file if output_file else None

        print("\nStarting traceroute...")
        run_traceroute(target, progressive, output_file)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace the route to a target and display intermediate IP addresses.")
    parser.add_argument("target", nargs="?", help="The target URL or IP address.")
    parser.add_argument("-p", "--progressive", action="store_true", help="Display IPs progressively.")
    parser.add_argument("-o", "--output-file", help="File to save the traceroute result.")
    parser.add_argument("-i", "--interactive", action="store_true", help="Run the program in interactive mode.")

    args = parser.parse_args()

    if args.interactive or not args.target:
        interactive_mode()
    else:
        run_traceroute(args.target, args.progressive, args.output_file)
