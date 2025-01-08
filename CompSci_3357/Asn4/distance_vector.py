def bellman_ford(adj_matrix, n, start):
    # Initialize distances from source to all vertices as infinity
    distances = [float('inf')] * n
    distances[start] = 0
    
    # relax edges |V| - 1 times
    for run in range(n - 1):
        for i in range(n):
            for j in range(n):
                if adj_matrix[i][j] != float('inf'):
                    if (distances[i] != float('inf')) and ((distances[i] + adj_matrix[i][j]) < distances[j]):
                        distances[j] = distances[i] + adj_matrix[i][j]
    
    # Using one run, look for bad negative cycles
    for i in range(n):
        for j in range(n):
            if adj_matrix[i][j] != float('inf'):
                if (distances[i] != float('inf')) and ((distances[i] + adj_matrix[i][j]) < distances[j]):
                    return [None] * n
    
    return distances

def main():
    n = int(input()) # size of matrix
    matrix = []
    
    # get input and construct adjcency matrix
    for i in range(n):
        row = []
        for j in range(n):
            val = input()
            if val == 'f':
                row.append(float('inf'))
            else:
                row.append(int(val))
        matrix.append(row)
        
    # process each node
    for i in range(n):
        distances = bellman_ford(matrix, n, i)
        print(f"Node {i}: {distances}")

if __name__ == "__main__":
    main()
