# ETCD & ETCD-Light Benchmarking

## Running the Benchmark

1. Launch a cluster of 5 CloudLab nodes running the [billyb-consensus](https://www.cloudlab.us/show-profile.php?uuid=9d6c84f3-6431-11f0-90d9-e4434b2381fc) experiment profile on 'c6525-100g' machines.
2. Manually run an `etcd-light` benchmark to identify 3 functional 'server nodes' in your cluster. Or reference the [Known Nodes](#known-nodes) section, to identify 3 functional server nodes. It is still good practice to manually check that the nodes you are using behave normally.
3. Select one of the other nodes to be the 'client node' and the remaining node will be the 'control node', where the script is run.
4. On the control node, `cd` into the `/local/etcdl_benchmark` directory.

```bash
cd /local/etcdl_benchmark
```

5. Configure the `config.json` file's first entry: `cluster`. `cluster` has two fields: `servers` and `client`.

- `servers` should be set to an array of strings, where each string is an IP address of a server node. `servers` should have exactly three elements with no duplicates, the order of the IP addresses will be the order of the server nodes (the first address will be node 0, etc.).
- `client` should be set to a string, where this string is the IP address of the client node.

```json
"cluster": {
  "servers": [
    "10.10.1.1",
    "10.10.1.2",
    "10.10.1.3"
  ],
  "client": "10.10.1.5"
}
```

> The above configuration declares the first three CloudLab nodes to be the first three server nodes and declares the fifth CloudLab node to be the client. By process of elimination, the control node is the fourth CloudLab node.

6. Configure the `config.json` file's benchmark configurations. There is a field for each system to benchmark: `etcd` and `etcdl` (`etcd-light`). Configurations for the plots in the paper are presented in [Plot Configurations](#plot-configurations).

- `etcd` is a list of configurations for benchmarks of the standard `etcd` implementation. Each configuration in the list will run the benchmark it describes. Each configuration will need the following fields:
  - `test_name` should be set to a string, where the string is a name to give to the benchmark. The name will become the name of the `.csv` file where the collected data is stored. If the name is new, a new file will be created; if the name has been used before, then the data will be appended to the existing data.
  - `data_size` should be set to an integer, where the integer is the size of data to use in the benchmark in bytes.
  - `num_operations` should be set to an integer, where the integer is the number of operations to perform in the benchmark.
  - `read_ratio` should be set to a float, where the float is the proportion of the operations that should be read-operations.
  - `num_clients` should be set to an integer, where the integer is the number of clients per server to benchmark with.

```json
"etcd": [
  {
    "test_name": "all_write",
    "data_size": 10000,
    "num_operations": 100000,
    "read_ratio": 0.0,
    "num_clients": 33
  }
]
```

> The above configuration will run one `etcd` benchmark called 'all_write'. This benchmark will do 100,000 10,000 byte writes with 33 clients per server.

- `etcdl` is a list of configurations for benchmarks of the `etcd-light` system. Each configuration in the list will run the benchmark it describes. Each configuration will need the following fields:
  - `test_name` should be set to a string, where the string is a name to give to the benchmark. The name will become the name of the `.csv` file where the collected data is stored. If the name is new, a new file will be created; if the name has been used before, then the data will be appended to the existing data.
  - `data_size` should be set to an integer, where the integer is the size of data to use in the benchmark in bytes.
  - `num_operations` should be set to an integer, where the integer is the number of operations to perform in the benchmark.
  - `read_ratio` should be set to a float, where the float is the proportion of the operations that should be read-operations.
  - `num_clients` should be set to an integer, where the integer is the number of clients per server to benchmark with.
  - `fast_path_writes` should be set to a boolean, where the boolean is the truth of fast path writes being enabled.
  - `num_dbs` should be set to an integer, where the integer is the number of BoltDBs to use.
  - `wal_file_count` should be set to an integer, where the integer is the number of WAL files to use.

```json
"etcdl": [
  {
    "test_name": "all_read",
    "data_size": 10000,
    "num_operations": 100000,
    "read_ratio": 1.0,
    "num_clients": 33,
    "fast_path_writes": true,
    "num_dbs": 1,
    "wal_file_count": 1
  }
]
```

> The above configuration will run one `etcd-light` benchmark called 'all_read'. This benchmark will do 100,000 10,000 byte reads with 33 clients per server; on servers with fast path writes, one BoltDB, and one WAL file.

7. Verify that Python 3.13 is installed or install Python 3.13.
8. Run `main.py` using Python 3.13 with `sudo` privileges.

```bash
sudo python3.13 main.py
```

9. The data from the benchmarks you just ran will be saved in `.csv` files in the `data/` directory. These files will be named after the names given to the benchmarks.

## Known Nodes

### Good Nodes

- `amd250`
- `amd251`
- `amd252`
- `amd255`
- `amd256`
- `amd262`
- `amd268`

### Bad Nodes

- `amd264`
- `amd257`

## Plot Configurations

#### Plots 1 & 2

```json
"etcd": [
  {
    "test_name": "all_write",
    "data_size": 10000,
    "num_operations": 200000,
    "read_ratio": 0.0,
    "num_clients": 33
  }
]
"etcdl": [
  {
    "test_name": "all_write",
    "data_size": 10000,
    "num_operations": 200000,
    "read_ratio": 0.0,
    "num_clients": 33,
    "fast_path_writes": false,
    "num_dbs": 1,
    "wal_file_count": 1
  },
  {
    "test_name": "all_write",
    "data_size": 10000,
    "num_operations": 200000,
    "read_ratio": 0.0,
    "num_clients": 33,
    "fast_path_writes": false,
    "num_dbs": 3,
    "wal_file_count": 1
  },
  {
    "test_name": "all_write",
    "data_size": 10000,
    "num_operations": 200000,
    "read_ratio": 0.0,
    "num_clients": 33,
    "fast_path_writes": false,
    "num_dbs": 5,
    "wal_file_count": 1
  }
]
```

#### Plots 3 & 4

```json
"etcd": [
  {
    "test_name": "all_write",
    "data_size": 100000,
    "num_operations": 20000,
    "read_ratio": 0.0,
    "num_clients": 33
  }
]
"etcdl": [
  {
    "test_name": "all_write",
    "data_size": 100000,
    "num_operations": 20000,
    "read_ratio": 0.0,
    "num_clients": 33,
    "fast_path_writes": true,
    "num_dbs": 1,
    "wal_file_count": 1
  },
  {
    "test_name": "all_write",
    "data_size": 100000,
    "num_operations": 20000,
    "read_ratio": 0.0,
    "num_clients": 33,
    "fast_path_writes": true,
    "num_dbs": 1,
    "wal_file_count": 5
  },
  {
    "test_name": "all_write",
    "data_size": 100000,
    "num_operations": 20000,
    "read_ratio": 0.0,
    "num_clients": 33,
    "fast_path_writes": true,
    "num_dbs": 1,
    "wal_file_count": 10
  }
]
```
