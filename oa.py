import requests
from bs4 import BeautifulSoup  # Ensure you have installed beautifulsoup4 using pip

def fetch_google_doc(url):
    """Fetch the content of a Google Doc."""
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses
    return response.text

def parse_google_doc(content):
    """Parse the content of the Google Doc and extract text."""
    soup = BeautifulSoup(content, 'html.parser')
    paragraphs = soup.find_all('p')  # Find all paragraph tags
    organized_data = [p.get_text() for p in paragraphs]  # Extract text from paragraphs
    return organized_data

def to_matrix(organized_data):
    """Put the data into a matrix."""
    # Get the maximum x and y coordinate value for the initialization of the matrix
    max_x = max(int(organized_data[i]) for i in range(5, len(organized_data)-1, 3))
    max_y = max(int(organized_data[i + 2]) for i in range(5, len(organized_data)-1, 3))

    matrix = [[' ' for _ in range(max_y + 1)] for _ in range(max_x + 1)]

    i = 5
    while i < len(organized_data)-1:
        x_coord = int(organized_data[i])
        #print(f"x coord: {x_coord}")
        i += 1
        value = organized_data[i]
        #print(f"value: {value}")
        i += 1
        y_coord = int(organized_data[i])
        #print(f"y coord: {y_coord}")
        i += 1
        matrix[x_coord][y_coord] = value

    return matrix

def print_matrix(matrix):
    """Print out the matix."""
    for row in matrix:
        print(''.join(row))


def main():
    """Mainline logic."""
    url = "https://docs.google.com/document/d/e/2PACX-1vQGUck9HIFCyezsrBSnmENk5ieJuYwpt7YHYEzeNJkIb9OSDdx-ov2nRNReKQyey-cwJOoEKUhLmN9z/pub"
    content = fetch_google_doc(url)
    organized_data = parse_google_doc(content)
    matrix = to_matrix(organized_data)
    print_matrix(matrix)

if __name__ == "__main__":
    main()
