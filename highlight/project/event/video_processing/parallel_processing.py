from multiprocessing import Pool

def parallel_process(function, data, num_processes):
    with Pool(num_processes) as pool:
        results = pool.map(function, data)
    return results
