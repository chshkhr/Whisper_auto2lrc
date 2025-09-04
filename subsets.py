import random
import re


def load_data(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read().replace('\n', ',')
        content = re.sub(r'\s{2,}', ' ', content)  # Replace multiple spaces with a single space
        data = [item.strip() for item in content.split(',') if item.strip()]
    return data


def generate_subsets(data, num_subsets=20, min_size=5, max_size=8):
    subsets = []
    for _ in range(num_subsets):
        subset_size = random.randint(min_size, max_size)
        subsets.append(random.sample(data, subset_size))
    return subsets


def save_subsets(subsets, output_filename):
    with open(output_filename, 'w', encoding='utf-8') as file:
        for subset in subsets:
            file.write(', '.join(subset) + '\n')


def main():
    input_file = 'input.txt'  # Change to your input filename
    output_file = 'output.txt'  # Change to your output filename

    data = load_data(input_file)
    subsets = generate_subsets(data)
    save_subsets(subsets, output_file)
    print(f"Generated {len(subsets)} subsets and saved to {output_file}")


if __name__ == "__main__":
    main()
