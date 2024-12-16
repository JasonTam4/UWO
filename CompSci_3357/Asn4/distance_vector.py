def bellman_ford(adj_matrix, n, source):
    # Initialize distances from source to all vertices as infinity
    distances = [float('inf')] * n
    distances[source] = 0
    
    # Relax all edges |V| - 1 times
    for run in range(n - 1):
        for i in range(n):
            for j in range(n):
                if adj_matrix[i][j] != float('inf'):
                    if (distances[i] != float('inf')) and ((distances[i] + adj_matrix[i][j]) < distances[j]):
                        distances[j] = distances[i] + adj_matrix[i][j]
    
    # Using one run, check for negative cycles
    for i in range(n):
        for j in range(n):
            if adj_matrix[i][j] != float('inf'):
                if (distances[i] != float('inf')) and ((distances[i] + adj_matrix[i][j]) < distances[j]):
                    # Negative cycle detected
                    return [None] * n
    
    return distances

def main():
    size = int(input())
    matrix = []
    
    # Construct adjcency matrix
    for i in range(size):
        row = []
        for j in range(size):
            val = input()
            if val == 'f':
                row.append(float('inf'))
            else:
                row.append(int(val))
        matrix.append(row)
        
    # Calculate shortest paths for each node
    for i in range(size):
        distances = bellman_ford(matrix, size, i)
        print(f"Node {i}: {distances}")

if __name__ == "__main__":
    main()
