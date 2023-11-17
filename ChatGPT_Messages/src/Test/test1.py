import sys

def main():
    if len(sys.argv) != 3:
        print("Usage: python print_ij.py <i> <j>")
        sys.exit(1)

    i = int(sys.argv[1])
    j = int(sys.argv[2])

    k = i + 1
    m = 2 * j

    with open('output.txt', 'w') as output_file:
        output_file.write(f"{k} {m}")

if __name__ == '__main__':
    main()